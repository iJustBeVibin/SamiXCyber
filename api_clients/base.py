"""
Base API client with caching and retry logic.
"""

import time
import logging
import requests
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BaseAPIClient:
    """
    Base class for API clients with built-in caching and retry logic.
    """
    
    def __init__(self, base_url: str, timeout: int = 10, retries: int = 2, cache_ttl: int = 300):
        """
        Initialize the base API client.
        
        Args:
            base_url: Base URL for the API
            timeout: Request timeout in seconds (default: 10)
            retries: Number of retry attempts (default: 2)
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        
    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from endpoint and parameters."""
        if params:
            param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            return f"{endpoint}?{param_str}"
        return endpoint
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if not cache_entry:
            return False
        age = time.time() - cache_entry.get('timestamp', 0)
        return age < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from cache if valid."""
        cache_entry = self._cache.get(cache_key)
        if cache_entry and self._is_cache_valid(cache_entry):
            logging.info(f"Cache hit for {cache_key}")
            return cache_entry.get('data')
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save data to cache with timestamp."""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def get(self, endpoint: str, params: Optional[Dict] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        Make GET request with caching and retry logic.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            use_cache: Whether to use cached data (default: True)
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.RequestException: If all retry attempts fail
        """
        cache_key = self._get_cache_key(endpoint, params)
        
        # Check cache first
        if use_cache:
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        # Build full URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(self.retries + 1):
            try:
                if attempt > 0:
                    backoff_time = 0.5 * (2 ** (attempt - 1))  # 0.5s, 1s, 2s...
                    logging.info(f"Retry attempt {attempt} after {backoff_time}s backoff")
                    time.sleep(backoff_time)
                
                logging.info(f"GET {url} (params: {params})")
                response = requests.get(url, params=params, timeout=self.timeout)
                
                # Handle rate limiting
                if response.status_code in [429, 403]:
                    logging.warning(f"Rate limit hit (status {response.status_code})")
                    if attempt < self.retries:
                        continue
                    else:
                        logging.error("Rate limit exceeded after all retries")
                        response.raise_for_status()
                
                response.raise_for_status()
                data = response.json()
                
                # Save to cache
                self._save_to_cache(cache_key, data)
                
                return data
                
            except requests.Timeout as e:
                last_exception = e
                logging.error(f"Request timeout on attempt {attempt + 1}: {e}")
            except requests.RequestException as e:
                last_exception = e
                logging.error(f"Request failed on attempt {attempt + 1}: {e}")
        
        # All retries failed
        logging.error(f"All retry attempts failed for {url}")
        raise last_exception
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        logging.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self._cache)
        valid_entries = sum(1 for entry in self._cache.values() if self._is_cache_valid(entry))
        
        return {
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'expired_entries': total_entries - valid_entries,
            'cache_ttl': self.cache_ttl
        }


if __name__ == "__main__":
    # Test the base client
    print("Testing BaseAPIClient...")
    
    # Test with a public API
    client = BaseAPIClient("https://api.coingecko.com/api/v3", cache_ttl=60)
    
    try:
        # First request (should hit API)
        print("\n1. First request (should hit API):")
        data1 = client.get("ping")
        print(f"Response: {data1}")
        
        # Second request (should hit cache)
        print("\n2. Second request (should hit cache):")
        data2 = client.get("ping")
        print(f"Response: {data2}")
        
        # Cache stats
        print("\n3. Cache stats:")
        stats = client.get_cache_stats()
        print(f"Stats: {stats}")
        
        # Clear cache
        print("\n4. Clearing cache...")
        client.clear_cache()
        stats = client.get_cache_stats()
        print(f"Stats after clear: {stats}")
        
        print("\n✅ BaseAPIClient tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
