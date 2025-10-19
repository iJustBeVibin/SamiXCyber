"""
DeFi Llama API client for protocol TVL and DeFi data.
"""

import logging
from typing import Dict, Any, Optional, List
from api_clients.base import BaseAPIClient

logging.basicConfig(level=logging.INFO)


class DefiLlamaClient(BaseAPIClient):
    """
    Client for DeFi Llama API to fetch protocol TVL and DeFi metrics.
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize DeFi Llama client.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        base_url = "https://api.llama.fi"
        super().__init__(base_url, timeout=10, retries=2, cache_ttl=cache_ttl)
    
    def get_protocol_tvl(self, protocol_slug: str) -> Dict[str, Any]:
        """
        Fetch TVL data for a specific protocol.
        
        Args:
            protocol_slug: DeFi Llama protocol slug (e.g., 'aave-v3', 'uniswap-v3')
            
        Returns:
            Dictionary with TVL data:
            {
                'protocol': str,
                'tvl': float (current TVL in USD),
                'tvl_change_24h': float (percentage),
                'tvl_change_7d': float (percentage),
                'chains': dict (TVL by chain),
                'chain_tvls': dict (detailed chain breakdown),
                'category': str,
                'last_updated': int (timestamp)
            }
            
        Raises:
            requests.RequestException: If API request fails
        """
        try:
            endpoint = f"protocol/{protocol_slug}"
            data = self.get(endpoint)
            
            # Calculate TVL changes if historical data available
            tvl_change_24h = 0
            tvl_change_7d = 0
            
            if 'tvl' in data and isinstance(data['tvl'], list) and len(data['tvl']) > 0:
                current_tvl = data['tvl'][-1].get('totalLiquidityUSD', 0)
                
                # Calculate 24h change
                if len(data['tvl']) > 1:
                    tvl_24h_ago = data['tvl'][-2].get('totalLiquidityUSD', current_tvl)
                    if tvl_24h_ago > 0:
                        tvl_change_24h = ((current_tvl - tvl_24h_ago) / tvl_24h_ago) * 100
                
                # Calculate 7d change (approximate)
                if len(data['tvl']) > 7:
                    tvl_7d_ago = data['tvl'][-8].get('totalLiquidityUSD', current_tvl)
                    if tvl_7d_ago > 0:
                        tvl_change_7d = ((current_tvl - tvl_7d_ago) / tvl_7d_ago) * 100
            else:
                current_tvl = data.get('tvl', 0)
            
            # Extract chain-specific TVL
            chain_tvls = data.get('chainTvls', {})
            chains = {}
            for chain, values in chain_tvls.items():
                if isinstance(values, dict) and 'tvl' in values:
                    chains[chain] = values['tvl']
                elif isinstance(values, list) and len(values) > 0:
                    chains[chain] = values[-1].get('totalLiquidityUSD', 0)
            
            result = {
                'protocol': data.get('name', protocol_slug),
                'slug': protocol_slug,
                'tvl': current_tvl,
                'tvl_change_24h': tvl_change_24h,
                'tvl_change_7d': tvl_change_7d,
                'chains': chains,
                'category': data.get('category', 'Unknown'),
                'description': data.get('description', ''),
                'logo': data.get('logo', ''),
                'url': data.get('url', ''),
                'last_updated': data['tvl'][-1].get('date', 0) if isinstance(data.get('tvl'), list) and len(data['tvl']) > 0 else 0
            }
            
            logging.info(f"Fetched TVL data for {protocol_slug}: ${result['tvl']:,.0f}")
            return result
            
        except Exception as e:
            logging.error(f"Failed to fetch TVL data for {protocol_slug}: {e}")
            # Return empty data structure on error
            return {
                'protocol': protocol_slug,
                'slug': protocol_slug,
                'tvl': 0,
                'tvl_change_24h': 0,
                'tvl_change_7d': 0,
                'chains': {},
                'category': 'Unknown',
                'description': '',
                'logo': '',
                'url': '',
                'last_updated': 0,
                'error': str(e)
            }
    
    def get_all_protocols(self) -> List[Dict[str, Any]]:
        """
        Fetch list of all protocols with basic TVL data.
        
        Returns:
            List of protocol dictionaries with basic info
        """
        try:
            data = self.get("protocols")
            logging.info(f"Fetched {len(data)} protocols from DeFi Llama")
            return data
        except Exception as e:
            logging.error(f"Failed to fetch protocols list: {e}")
            return []
    
    def get_protocol_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Search for a protocol by name in the protocols list.
        
        Args:
            name: Protocol name to search for
            
        Returns:
            Protocol data if found, None otherwise
        """
        try:
            protocols = self.get_all_protocols()
            name_lower = name.lower()
            
            for protocol in protocols:
                if protocol.get('name', '').lower() == name_lower:
                    return protocol
            
            logging.warning(f"Protocol '{name}' not found")
            return None
            
        except Exception as e:
            logging.error(f"Failed to search for protocol {name}: {e}")
            return None
    
    def get_chains(self) -> List[Dict[str, Any]]:
        """
        Fetch list of all chains with TVL data.
        
        Returns:
            List of chain dictionaries
        """
        try:
            data = self.get("chains")
            logging.info(f"Fetched {len(data)} chains from DeFi Llama")
            return data
        except Exception as e:
            logging.error(f"Failed to fetch chains list: {e}")
            return []


if __name__ == "__main__":
    # Test the DeFi Llama client
    print("Testing DefiLlamaClient...")
    
    client = DefiLlamaClient()
    
    try:
        # Test 1: Get TVL for Aave V3
        print("\n1. Fetching Aave V3 TVL data:")
        aave_data = client.get_protocol_tvl("aave-v3")
        print(f"   Protocol: {aave_data['protocol']}")
        print(f"   TVL: ${aave_data['tvl']:,.0f}")
        print(f"   24h Change: {aave_data['tvl_change_24h']:.2f}%")
        print(f"   Category: {aave_data['category']}")
        print(f"   Chains: {list(aave_data['chains'].keys())}")
        
        # Test 2: Get TVL for Uniswap V3
        print("\n2. Fetching Uniswap V3 TVL data:")
        uni_data = client.get_protocol_tvl("uniswap-v3")
        print(f"   Protocol: {uni_data['protocol']}")
        print(f"   TVL: ${uni_data['tvl']:,.0f}")
        print(f"   7d Change: {uni_data['tvl_change_7d']:.2f}%")
        
        # Test 3: Test caching
        print("\n3. Testing cache (second request):")
        import time
        start = time.time()
        aave_data2 = client.get_protocol_tvl("aave-v3")
        elapsed = time.time() - start
        print(f"   Request completed in {elapsed:.3f}s (should be <0.01s if cached)")
        
        # Test 4: Get all protocols (limited output)
        print("\n4. Fetching all protocols:")
        all_protocols = client.get_all_protocols()
        print(f"   Total protocols: {len(all_protocols)}")
        if all_protocols:
            print(f"   Top 3 by TVL:")
            sorted_protocols = sorted(all_protocols, key=lambda x: x.get('tvl', 0), reverse=True)
            for i, p in enumerate(sorted_protocols[:3], 1):
                print(f"      {i}. {p.get('name', 'Unknown')}: ${p.get('tvl', 0):,.0f}")
        
        # Test 5: Handle invalid protocol
        print("\n5. Testing error handling (invalid protocol):")
        invalid_data = client.get_protocol_tvl("invalid-protocol-12345")
        if 'error' in invalid_data:
            print(f"   ✓ Error handled gracefully: {invalid_data.get('error', '')[:50]}...")
        
        # Test 6: Get chains
        print("\n6. Fetching chains:")
        chains = client.get_chains()
        print(f"   Total chains: {len(chains)}")
        if chains:
            print(f"   Top 3 chains by TVL:")
            for i, chain in enumerate(chains[:3], 1):
                print(f"      {i}. {chain.get('name', 'Unknown')}: ${chain.get('tvl', 0):,.0f}")
        
        print("\n✅ DefiLlamaClient tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
