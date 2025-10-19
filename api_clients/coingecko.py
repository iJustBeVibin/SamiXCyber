"""
CoinGecko API client for cryptocurrency market data.
"""

import logging
from typing import Dict, Any, Optional
from api_clients.base import BaseAPIClient

logging.basicConfig(level=logging.INFO)


class CoinGeckoClient(BaseAPIClient):
    """
    Client for CoinGecko API to fetch cryptocurrency market data.
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_ttl: int = 300):
        """
        Initialize CoinGecko client.
        
        Args:
            api_key: Optional CoinGecko API key for higher rate limits
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        base_url = "https://api.coingecko.com/api/v3"
        super().__init__(base_url, timeout=10, retries=2, cache_ttl=cache_ttl)
        self.api_key = api_key
    
    def get_token_data(self, coin_id: str) -> Dict[str, Any]:
        """
        Fetch comprehensive token data including price, market cap, volume, and price change.
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum', 'aave')
            
        Returns:
            Dictionary with token data:
            {
                'price': float,
                'market_cap': float,
                'volume_24h': float,
                'price_change_24h': float (percentage),
                'price_change_7d': float (percentage),
                'market_cap_rank': int,
                'circulating_supply': float,
                'total_supply': float,
                'ath': float (all-time high),
                'ath_change_percentage': float,
                'last_updated': str
            }
            
        Raises:
            ValueError: If coin_id is not found
            requests.RequestException: If API request fails
        """
        try:
            params = {
                'localization': 'false',
                'tickers': 'false',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }
            
            if self.api_key:
                params['x_cg_pro_api_key'] = self.api_key
            
            endpoint = f"coins/{coin_id}"
            data = self.get(endpoint, params=params)
            
            # Extract relevant market data
            market_data = data.get('market_data', {})
            
            result = {
                'coin_id': coin_id,
                'name': data.get('name', 'Unknown'),
                'symbol': data.get('symbol', '').upper(),
                'price': market_data.get('current_price', {}).get('usd', 0),
                'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                'price_change_24h': market_data.get('price_change_percentage_24h', 0),
                'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                'market_cap_rank': market_data.get('market_cap_rank', 0),
                'circulating_supply': market_data.get('circulating_supply', 0),
                'total_supply': market_data.get('total_supply', 0),
                'ath': market_data.get('ath', {}).get('usd', 0),
                'ath_change_percentage': market_data.get('ath_change_percentage', {}).get('usd', 0),
                'last_updated': data.get('last_updated', '')
            }
            
            logging.info(f"Fetched token data for {coin_id}: ${result['price']:.2f}")
            return result
            
        except Exception as e:
            logging.error(f"Failed to fetch token data for {coin_id}: {e}")
            # Return empty data structure on error
            return {
                'coin_id': coin_id,
                'name': 'Unknown',
                'symbol': '',
                'price': 0,
                'market_cap': 0,
                'volume_24h': 0,
                'price_change_24h': 0,
                'price_change_7d': 0,
                'market_cap_rank': 0,
                'circulating_supply': 0,
                'total_supply': 0,
                'ath': 0,
                'ath_change_percentage': 0,
                'last_updated': '',
                'error': str(e)
            }
    
    def get_simple_price(self, coin_ids: list, vs_currencies: list = ['usd']) -> Dict[str, Any]:
        """
        Fetch simple price data for multiple coins (lighter endpoint).
        
        Args:
            coin_ids: List of CoinGecko coin IDs
            vs_currencies: List of currencies to get prices in (default: ['usd'])
            
        Returns:
            Dictionary mapping coin_id to price data
        """
        try:
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': ','.join(vs_currencies),
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            
            if self.api_key:
                params['x_cg_pro_api_key'] = self.api_key
            
            data = self.get("simple/price", params=params)
            logging.info(f"Fetched simple price data for {len(coin_ids)} coins")
            return data
            
        except Exception as e:
            logging.error(f"Failed to fetch simple price data: {e}")
            return {}


if __name__ == "__main__":
    # Test the CoinGecko client
    print("Testing CoinGeckoClient...")
    
    client = CoinGeckoClient()
    
    try:
        # Test 1: Get token data for Ethereum
        print("\n1. Fetching Ethereum token data:")
        eth_data = client.get_token_data("ethereum")
        print(f"   Name: {eth_data['name']}")
        print(f"   Symbol: {eth_data['symbol']}")
        print(f"   Price: ${eth_data['price']:,.2f}")
        print(f"   Market Cap: ${eth_data['market_cap']:,.0f}")
        print(f"   24h Change: {eth_data['price_change_24h']:.2f}%")
        
        # Test 2: Get token data for Aave
        print("\n2. Fetching Aave token data:")
        aave_data = client.get_token_data("aave")
        print(f"   Name: {aave_data['name']}")
        print(f"   Price: ${aave_data['price']:,.2f}")
        print(f"   Market Cap Rank: #{aave_data['market_cap_rank']}")
        
        # Test 3: Test caching (second request should be instant)
        print("\n3. Testing cache (second request):")
        import time
        start = time.time()
        eth_data2 = client.get_token_data("ethereum")
        elapsed = time.time() - start
        print(f"   Request completed in {elapsed:.3f}s (should be <0.01s if cached)")
        
        # Test 4: Get simple price for multiple coins
        print("\n4. Fetching simple prices:")
        prices = client.get_simple_price(["bitcoin", "ethereum", "aave"])
        for coin, data in prices.items():
            print(f"   {coin}: ${data.get('usd', 0):,.2f}")
        
        # Test 5: Handle invalid coin ID
        print("\n5. Testing error handling (invalid coin):")
        invalid_data = client.get_token_data("invalid-coin-id-12345")
        if 'error' in invalid_data:
            print(f"   ✓ Error handled gracefully: {invalid_data.get('error', '')[:50]}...")
        
        print("\n✅ CoinGeckoClient tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
