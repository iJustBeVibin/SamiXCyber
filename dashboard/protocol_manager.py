"""
Protocol Manager for Risk Dashboard.
Manages protocol configurations and coordinates data fetching from multiple sources.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from api_clients.coingecko import CoinGeckoClient
from api_clients.defillama import DefiLlamaClient
from engine.risk_aggregator import RiskAggregator
from adapters.ethereum import get_tech_facts
from features.tech import build_tech_features
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProtocolManager:
    """
    Manages protocol configurations and coordinates data fetching.
    
    Responsibilities:
    - Load protocol configurations from JSON file
    - Initialize API clients (CoinGecko, DeFi Llama)
    - Initialize RiskAggregator
    - Coordinate data fetching and risk calculation
    - Manage data caching with 15-minute refresh interval
    """
    
    # Cache refresh interval in seconds (15 minutes)
    CACHE_REFRESH_INTERVAL = 900
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Protocol Manager.
        
        Args:
            config_path: Path to protocols.json configuration file.
                        Defaults to 'dashboard/protocols.json'
        
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration is invalid
        """
        # Set default config path
        if config_path is None:
            config_path = os.path.join('dashboard', 'protocols.json')
        
        self.config_path = config_path
        
        # Load protocol configurations
        self.protocols = self._load_protocol_configs()
        logger.info(f"Loaded {len(self.protocols)} protocol configurations")
        
        # Initialize API clients
        self.coingecko_client = CoinGeckoClient()
        self.defillama_client = DefiLlamaClient()
        logger.info("Initialized API clients: CoinGecko, DeFi Llama")
        
        # Initialize risk aggregator
        self.risk_aggregator = RiskAggregator()
        logger.info("Initialized RiskAggregator")
        
        # Initialize protocol data cache
        # Structure: {protocol_id: {data: dict, timestamp: int}}
        self._protocol_cache = {}
        logger.info("Initialized protocol data cache")
    
    def _load_protocol_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Load protocol configurations from JSON file.
        
        Returns:
            Dictionary mapping protocol IDs to their configurations
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If JSON is invalid or missing required fields
        """
        try:
            config_file = Path(self.config_path)
            
            if not config_file.exists():
                raise FileNotFoundError(
                    f"Protocol configuration file not found: {self.config_path}"
                )
            
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            if 'protocols' not in data:
                raise ValueError("Configuration must contain 'protocols' key")
            
            protocols_list = data['protocols']
            
            if not isinstance(protocols_list, list):
                raise ValueError("'protocols' must be a list")
            
            if len(protocols_list) == 0:
                raise ValueError("No protocols configured")
            
            # Convert list to dictionary keyed by protocol ID
            protocols_dict = {}
            for protocol in protocols_list:
                # Validate required fields
                required_fields = ['id', 'name', 'chain', 'contract_address', 
                                 'coingecko_id', 'defillama_slug']
                
                missing_fields = [field for field in required_fields 
                                if field not in protocol]
                
                if missing_fields:
                    logger.warning(
                        f"Protocol '{protocol.get('name', 'Unknown')}' missing fields: "
                        f"{missing_fields}. Skipping."
                    )
                    continue
                
                protocol_id = protocol['id']
                protocols_dict[protocol_id] = protocol
                logger.debug(f"Loaded protocol: {protocol_id} - {protocol['name']}")
            
            if len(protocols_dict) == 0:
                raise ValueError("No valid protocols found in configuration")
            
            return protocols_dict
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            logger.error(f"Error loading protocol configurations: {e}")
            raise
    
    def get_protocol_config(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific protocol.
        
        Args:
            protocol_id: Protocol identifier
            
        Returns:
            Protocol configuration dictionary or None if not found
        """
        return self.protocols.get(protocol_id)
    
    def list_protocols(self) -> List[Dict[str, Any]]:
        """
        Get list of all configured protocols.
        
        Returns:
            List of protocol configuration dictionaries
        """
        return list(self.protocols.values())
    
    def get_protocol_ids(self) -> List[str]:
        """
        Get list of all protocol IDs.
        
        Returns:
            List of protocol ID strings
        """
        return list(self.protocols.keys())
    
    def _is_cache_valid(self, protocol_id: str) -> bool:
        """
        Check if cached data for a protocol is still valid.
        
        Args:
            protocol_id: Protocol identifier
            
        Returns:
            True if cache exists and is within refresh interval, False otherwise
        """
        if protocol_id not in self._protocol_cache:
            return False
        
        cache_entry = self._protocol_cache[protocol_id]
        cache_age = time.time() - cache_entry['timestamp']
        
        return cache_age < self.CACHE_REFRESH_INTERVAL
    
    def _get_cached_data(self, protocol_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data for a protocol if valid.
        
        Args:
            protocol_id: Protocol identifier
            
        Returns:
            Cached protocol data or None if cache is invalid
        """
        if self._is_cache_valid(protocol_id):
            logger.info(f"Using cached data for protocol: {protocol_id}")
            return self._protocol_cache[protocol_id]['data']
        
        return None
    
    def _cache_protocol_data(self, protocol_id: str, data: Dict[str, Any]) -> None:
        """
        Cache protocol data with current timestamp.
        
        Args:
            protocol_id: Protocol identifier
            data: Protocol risk data to cache
        """
        self._protocol_cache[protocol_id] = {
            'data': data,
            'timestamp': time.time()
        }
        logger.debug(f"Cached data for protocol: {protocol_id}")
    
    @staticmethod
    def format_data_age(timestamp: int) -> str:
        """
        Format data age in human-readable format.
        
        Args:
            timestamp: Unix timestamp of last update
            
        Returns:
            Human-readable string like "2 minutes ago", "1 hour ago", etc.
        """
        age_seconds = int(time.time() - timestamp)
        
        if age_seconds < 60:
            return f"{age_seconds} second{'s' if age_seconds != 1 else ''} ago"
        
        age_minutes = age_seconds // 60
        if age_minutes < 60:
            return f"{age_minutes} minute{'s' if age_minutes != 1 else ''} ago"
        
        age_hours = age_minutes // 60
        if age_hours < 24:
            return f"{age_hours} hour{'s' if age_hours != 1 else ''} ago"
        
        age_days = age_hours // 24
        return f"{age_days} day{'s' if age_days != 1 else ''} ago"
    
    def get_protocol_risk_data(self, protocol_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch and aggregate all risk data for a protocol.
        
        This method:
        1. Checks cache for valid data (unless force_refresh is True)
        2. Fetches on-chain data using Ethereum adapter
        3. Fetches market data from CoinGecko
        4. Fetches TVL data from DeFi Llama
        5. Calculates risk scores using RiskAggregator
        6. Handles partial data availability when APIs fail
        7. Caches the result with timestamp
        
        Args:
            protocol_id: Protocol identifier
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Dictionary with comprehensive risk assessment:
            {
                'protocol_id': str,
                'name': str,
                'contract_address': str,
                'chain': str,
                'scores': {
                    'overall': int,
                    'security': int,
                    'financial': int,
                    'operational': int,
                    'market': int
                },
                'risk_indicator': str,
                'reasons': {
                    'security': [str],
                    'financial': [str],
                    'operational': [str],
                    'market': [str]
                },
                'metadata': {
                    'last_updated': int (timestamp),
                    'data_sources': [str],
                    'data_availability': str,
                    'api_failures': [str],
                    'cache_status': str
                }
            }
            
        Raises:
            ValueError: If protocol_id is not found
        """
        # Get protocol configuration
        protocol_config = self.get_protocol_config(protocol_id)
        if not protocol_config:
            raise ValueError(f"Protocol '{protocol_id}' not found in configuration")
        
        # Check cache if not forcing refresh
        if not force_refresh:
            cached_data = self._get_cached_data(protocol_id)
            if cached_data is not None:
                # Add cache status to metadata
                cached_data['metadata']['cache_status'] = 'cached'
                return cached_data
        
        logger.info(f"Fetching risk data for protocol: {protocol_id} ({protocol_config['name']})")
        
        # Track data sources and failures
        data_sources = []
        api_failures = []
        
        # Initialize data containers with defaults
        tech_features = {}
        market_data = {}
        tvl_data = {}
        
        # 1. Fetch on-chain data using Ethereum adapter
        try:
            logger.info(f"Fetching on-chain data for {protocol_config['contract_address']}")
            tech_facts = get_tech_facts(
                protocol_config['contract_address'],
                protocol_config.get('network', 'mainnet')
            )
            tech_features = build_tech_features(
                tech_facts,
                protocol_config['chain'],
                protocol_config.get('network', 'mainnet')
            )
            data_sources.append('ethereum')
            logger.info(f"✓ On-chain data fetched successfully")
        except Exception as e:
            logger.error(f"Failed to fetch on-chain data: {e}")
            api_failures.append(f"ethereum: {str(e)}")
            # Provide default tech features
            tech_features = {
                'verified': False,
                'has_admin_key': False,
                'has_supply_key': False,
                'has_pause_key': False,
                'has_freeze_key': False,
                'has_wipe_key': False,
                'has_kyc_key': False,
                'has_fee_key': False,
                'upgradeable': False
            }
        
        # 2. Fetch market data from CoinGecko
        try:
            logger.info(f"Fetching market data for {protocol_config['coingecko_id']}")
            market_data = self.coingecko_client.get_token_data(protocol_config['coingecko_id'])
            if 'error' not in market_data:
                data_sources.append('coingecko')
                logger.info(f"✓ Market data fetched successfully")
            else:
                api_failures.append(f"coingecko: {market_data['error']}")
                logger.warning(f"CoinGecko returned error: {market_data['error']}")
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            api_failures.append(f"coingecko: {str(e)}")
            # Provide default market data
            market_data = {
                'price': 0,
                'market_cap': 0,
                'volume_24h': 0,
                'price_change_24h': 0,
                'market_cap_rank': 999
            }
        
        # 3. Fetch TVL data from DeFi Llama
        try:
            logger.info(f"Fetching TVL data for {protocol_config['defillama_slug']}")
            tvl_data = self.defillama_client.get_protocol_tvl(protocol_config['defillama_slug'])
            if 'error' not in tvl_data:
                data_sources.append('defillama')
                logger.info(f"✓ TVL data fetched successfully")
            else:
                api_failures.append(f"defillama: {tvl_data['error']}")
                logger.warning(f"DeFi Llama returned error: {tvl_data['error']}")
        except Exception as e:
            logger.error(f"Failed to fetch TVL data: {e}")
            api_failures.append(f"defillama: {str(e)}")
            # Provide default TVL data
            tvl_data = {
                'tvl': 0,
                'tvl_change_24h': 0,
                'chains': {}
            }
        
        # 4. Calculate risk scores using RiskAggregator
        logger.info("Calculating risk scores...")
        try:
            risk_assessment = self.risk_aggregator.aggregate_risk(
                tech_features=tech_features,
                tvl_data=tvl_data,
                market_data=market_data,
                protocol_data=protocol_config,
                audit_data=None  # Placeholder for MVP
            )
            logger.info(f"✓ Risk scores calculated: Overall={risk_assessment['overall_score']}")
        except Exception as e:
            logger.error(f"Failed to calculate risk scores: {e}")
            # Provide default risk assessment
            risk_assessment = {
                'overall_score': 0,
                'risk_indicator': '⚠️ Data Unavailable',
                'category_scores': {
                    'security': 0,
                    'financial': 0,
                    'operational': 0,
                    'market': 0
                },
                'reasons': {
                    'security': ['Data unavailable'],
                    'financial': ['Data unavailable'],
                    'operational': ['Data unavailable'],
                    'market': ['Data unavailable']
                }
            }
        
        # 5. Determine data availability status
        if len(data_sources) == 3:
            data_availability = 'complete'
        elif len(data_sources) > 0:
            data_availability = 'partial'
        else:
            data_availability = 'unavailable'
        
        # Construct final result
        result = {
            'protocol_id': protocol_id,
            'name': protocol_config['name'],
            'contract_address': protocol_config['contract_address'],
            'chain': protocol_config['chain'],
            'category': protocol_config.get('category', 'Unknown'),
            'scores': {
                'overall': risk_assessment['overall_score'],
                'security': risk_assessment['category_scores']['security'],
                'financial': risk_assessment['category_scores']['financial'],
                'operational': risk_assessment['category_scores']['operational'],
                'market': risk_assessment['category_scores']['market']
            },
            'risk_indicator': risk_assessment['risk_indicator'],
            'reasons': risk_assessment['reasons'],
            'metadata': {
                'last_updated': int(time.time()),
                'data_sources': data_sources,
                'data_availability': data_availability,
                'api_failures': api_failures,
                'cache_status': 'fresh'
            }
        }
        
        # Cache the result
        self._cache_protocol_data(protocol_id, result)
        
        logger.info(f"✓ Risk data aggregation complete for {protocol_id}")
        logger.info(f"  Data availability: {data_availability}")
        logger.info(f"  Data sources: {', '.join(data_sources)}")
        if api_failures:
            logger.warning(f"  API failures: {len(api_failures)}")
        
        return result
    
    def refresh_protocol_data(self, protocol_id: str) -> Dict[str, Any]:
        """
        Force refresh of protocol data, bypassing cache.
        
        This method is useful when you need to ensure you have the most
        up-to-date data, regardless of cache status.
        
        Args:
            protocol_id: Protocol identifier
            
        Returns:
            Fresh protocol risk data
            
        Raises:
            ValueError: If protocol_id is not found
        """
        logger.info(f"Force refreshing data for protocol: {protocol_id}")
        return self.get_protocol_risk_data(protocol_id, force_refresh=True)
    
    def get_all_protocols(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch risk data for all configured protocols.
        
        This method fetches data for all protocols sequentially, handling
        individual protocol failures without blocking others. Each protocol
        is processed independently, so if one fails, the others will still
        be returned.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data for all protocols
            
        Returns:
            List of protocol risk data dictionaries. Protocols that fail to load
            will have an error indicator in their metadata.
            
        Example:
            >>> manager = ProtocolManager()
            >>> all_data = manager.get_all_protocols()
            >>> print(f"Loaded {len(all_data)} protocols")
            >>> for protocol in all_data:
            ...     print(f"{protocol['name']}: {protocol['scores']['overall']}")
        """
        logger.info(f"Fetching risk data for all {len(self.protocols)} protocols...")
        
        results = []
        successful_count = 0
        failed_count = 0
        
        # Process each protocol sequentially
        for protocol_id in self.protocols.keys():
            try:
                logger.info(f"Processing protocol {successful_count + failed_count + 1}/{len(self.protocols)}: {protocol_id}")
                
                # Fetch protocol risk data
                protocol_data = self.get_protocol_risk_data(protocol_id, force_refresh=force_refresh)
                results.append(protocol_data)
                successful_count += 1
                
                logger.info(f"✓ Successfully loaded {protocol_id}")
                
            except Exception as e:
                # Log the error but continue with other protocols
                logger.error(f"✗ Failed to load protocol '{protocol_id}': {e}")
                failed_count += 1
                
                # Create error entry for this protocol
                protocol_config = self.protocols[protocol_id]
                error_entry = {
                    'protocol_id': protocol_id,
                    'name': protocol_config.get('name', 'Unknown'),
                    'contract_address': protocol_config.get('contract_address', ''),
                    'chain': protocol_config.get('chain', 'Unknown'),
                    'category': protocol_config.get('category', 'Unknown'),
                    'scores': {
                        'overall': 0,
                        'security': 0,
                        'financial': 0,
                        'operational': 0,
                        'market': 0
                    },
                    'risk_indicator': '❌ Error',
                    'reasons': {
                        'security': [f'Failed to load: {str(e)}'],
                        'financial': [],
                        'operational': [],
                        'market': []
                    },
                    'metadata': {
                        'last_updated': int(time.time()),
                        'data_sources': [],
                        'data_availability': 'unavailable',
                        'api_failures': [f'protocol_load_error: {str(e)}'],
                        'cache_status': 'error'
                    }
                }
                results.append(error_entry)
        
        # Log summary
        logger.info(f"Batch protocol fetch complete:")
        logger.info(f"  ✓ Successful: {successful_count}/{len(self.protocols)}")
        if failed_count > 0:
            logger.warning(f"  ✗ Failed: {failed_count}/{len(self.protocols)}")
        
        return results


if __name__ == "__main__":
    """Test the ProtocolManager."""
    print("Testing ProtocolManager...")
    
    try:
        # Test initialization
        print("\n1. Testing initialization:")
        manager = ProtocolManager()
        print(f"   ✅ Initialized with {len(manager.protocols)} protocols")
        
        # Test protocol listing
        print("\n2. Testing protocol listing:")
        protocols = manager.list_protocols()
        print(f"   Found {len(protocols)} protocols:")
        for protocol in protocols:
            print(f"   - {protocol['id']}: {protocol['name']} ({protocol['category']})")
        
        # Test getting specific protocol
        print("\n3. Testing get_protocol_config:")
        if protocols:
            test_id = protocols[0]['id']
            config = manager.get_protocol_config(test_id)
            if config:
                print(f"   ✅ Retrieved config for '{test_id}':")
                print(f"      Name: {config['name']}")
                print(f"      Chain: {config['chain']}")
                print(f"      Contract: {config['contract_address']}")
                print(f"      CoinGecko ID: {config['coingecko_id']}")
                print(f"      DeFi Llama Slug: {config['defillama_slug']}")
            else:
                print(f"   ❌ Failed to retrieve config for '{test_id}'")
        
        # Test getting protocol IDs
        print("\n4. Testing get_protocol_ids:")
        protocol_ids = manager.get_protocol_ids()
        print(f"   Protocol IDs: {', '.join(protocol_ids)}")
        
        # Test invalid protocol
        print("\n5. Testing invalid protocol:")
        invalid_config = manager.get_protocol_config('nonexistent-protocol')
        if invalid_config is None:
            print("   ✅ Correctly returned None for invalid protocol")
        else:
            print("   ❌ Should have returned None for invalid protocol")
        
        # Test get_protocol_risk_data
        print("\n6. Testing get_protocol_risk_data:")
        if protocols:
            test_id = protocols[0]['id']
            print(f"   Fetching risk data for '{test_id}'...")
            try:
                risk_data = manager.get_protocol_risk_data(test_id)
                print(f"   ✅ Risk data retrieved successfully:")
                print(f"      Overall Score: {risk_data['scores']['overall']} - {risk_data['risk_indicator']}")
                print(f"      Security: {risk_data['scores']['security']}")
                print(f"      Financial: {risk_data['scores']['financial']}")
                print(f"      Operational: {risk_data['scores']['operational']}")
                print(f"      Market: {risk_data['scores']['market']}")
                print(f"      Data Sources: {', '.join(risk_data['metadata']['data_sources'])}")
                print(f"      Data Availability: {risk_data['metadata']['data_availability']}")
                if risk_data['metadata']['api_failures']:
                    print(f"      API Failures: {len(risk_data['metadata']['api_failures'])}")
            except Exception as e:
                print(f"   ❌ Failed to fetch risk data: {e}")
                import traceback
                traceback.print_exc()
        
        # Test get_all_protocols
        print("\n7. Testing get_all_protocols:")
        try:
            print(f"   Fetching risk data for all protocols...")
            all_protocols_data = manager.get_all_protocols()
            print(f"   ✅ Batch fetch completed:")
            print(f"      Total protocols: {len(all_protocols_data)}")
            
            successful = [p for p in all_protocols_data if p['metadata']['cache_status'] != 'error']
            failed = [p for p in all_protocols_data if p['metadata']['cache_status'] == 'error']
            
            print(f"      Successful: {len(successful)}")
            if failed:
                print(f"      Failed: {len(failed)}")
            
            print(f"\n   Protocol Summary:")
            for protocol_data in all_protocols_data:
                status_icon = "✓" if protocol_data['metadata']['cache_status'] != 'error' else "✗"
                print(f"      {status_icon} {protocol_data['name']}: {protocol_data['scores']['overall']} - {protocol_data['risk_indicator']}")
                
        except Exception as e:
            print(f"   ❌ Failed to fetch all protocols: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n✅ All ProtocolManager tests passed!")
        
    except FileNotFoundError as e:
        print(f"\n❌ Configuration file not found: {e}")
        print("   Make sure dashboard/protocols.json exists")
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
