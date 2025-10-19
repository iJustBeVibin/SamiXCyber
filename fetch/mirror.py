"""
Hedera Mirror Node API fetcher.
Retrieves token and contract information from the Mirror Node REST API.
"""

import time
import requests
from typing import Dict, Optional, Any
from config import (
    get_mirror_endpoint,
    get_hashscan_url,
    API_TIMEOUT,
    API_RETRIES,
    REQUEST_DELAY,
)


def _make_request_with_retries(url: str, timeout: int = API_TIMEOUT) -> Dict[str, Any]:
    """
    Make HTTP request with retry logic.
    
    Args:
        url: The URL to request
        timeout: Request timeout in seconds
        
    Returns:
        JSON response as dictionary
        
    Raises:
        requests.RequestException: If all retries fail
    """
    last_exception = None
    
    for attempt in range(API_RETRIES + 1):
        try:
            if attempt > 0:
                time.sleep(REQUEST_DELAY * attempt)  # Exponential backoff
                
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            last_exception = e
            if attempt < API_RETRIES:
                continue
            else:
                break
    
    raise last_exception


def hedera_token(token_id: str) -> Dict[str, Any]:
    """
    Fetch token information from Hedera Mirror Node.
    
    Args:
        token_id: Token ID in format "0.0.12345" or EVM address
        
    Returns:
        Dictionary containing token info:
        {
            "type": "FUNGIBLE" | "NON_FUNGIBLE",
            "keys": {
                "admin": bool,
                "supply": bool,
                "pause": bool,
                "freeze": bool,
                "wipe": bool,
                "kyc": bool,
                "fee": bool
            },
            "holders_estimate": int,
            "hashscan_url": str,
            "token_id": str,
            "name": str,
            "symbol": str
        }
    """
    try:
        # Normalize token ID
        if token_id.startswith('0x'):
            # EVM address - use as-is for Mirror Node
            token_param = token_id
        else:
            # Hedera ID format
            token_param = token_id
        
        # Fetch token info
        url = get_mirror_endpoint(f"tokens/{token_param}")
        token_data = _make_request_with_retries(url)
        
        # Extract key information
        keys = {
            "admin": False,
            "supply": False, 
            "pause": False,
            "freeze": False,
            "wipe": False,
            "kyc": False,
            "fee": False
        }
        
        # Parse keys from Mirror Node response
        if "key" in token_data:
            keys["admin"] = token_data["key"] is not None
            
        for key_field in ["supply_key", "pause_key", "freeze_key", "wipe_key", "kyc_key", "fee_schedule_key"]:
            if key_field in token_data and token_data[key_field]:
                key_name = key_field.replace("_key", "").replace("fee_schedule", "fee")
                keys[key_name] = True
        
        # Get holder count (approximate)
        holders_estimate = 0
        try:
            accounts_url = get_mirror_endpoint(f"tokens/{token_param}/balances")
            accounts_data = _make_request_with_retries(accounts_url)
            if "balances" in accounts_data:
                holders_estimate = len(accounts_data["balances"])
        except Exception:
            # If we can't get holder count, use 0
            pass
        
        # Determine token ID for HashScan URL
        final_token_id = token_data.get("token_id", token_id)
        hashscan_url = get_hashscan_url("token", final_token_id)
        
        return {
            "type": token_data.get("type", "UNKNOWN"),
            "keys": keys,
            "holders_estimate": holders_estimate,
            "hashscan_url": hashscan_url,
            "token_id": final_token_id,
            "name": token_data.get("name", ""),
            "symbol": token_data.get("symbol", "")
        }
        
    except Exception as e:
        # Return minimal data structure on error
        return {
            "type": "UNKNOWN",
            "keys": {
                "admin": False,
                "supply": False,
                "pause": False,
                "freeze": False,
                "wipe": False,
                "kyc": False,
                "fee": False
            },
            "holders_estimate": 0,
            "hashscan_url": get_hashscan_url("token", token_id),
            "token_id": token_id,
            "name": "",
            "symbol": "",
            "error": str(e)
        }


def hedera_contract(contract_id: str) -> Dict[str, Any]:
    """
    Fetch contract information from Hedera Mirror Node.
    
    Args:
        contract_id: Contract ID in format "0.0.12345" or EVM address
        
    Returns:
        Dictionary containing contract info:
        {
            "bytecode_present": bool,
            "admin_keys_present": bool,
            "hashscan_url": str,
            "contract_id": str,
            "evm_address": str
        }
    """
    try:
        # Normalize contract ID
        if contract_id.startswith('0x'):
            contract_param = contract_id
        else:
            contract_param = contract_id
            
        # Fetch contract info
        url = get_mirror_endpoint(f"contracts/{contract_param}")
        contract_data = _make_request_with_retries(url)
        
        # Extract relevant information
        bytecode_present = bool(contract_data.get("bytecode"))
        admin_keys_present = bool(contract_data.get("admin_key"))
        
        # Get final contract ID and EVM address
        final_contract_id = contract_data.get("contract_id", contract_id)
        evm_address = contract_data.get("evm_address", "")
        
        hashscan_url = get_hashscan_url("contract", final_contract_id)
        
        return {
            "bytecode_present": bytecode_present,
            "admin_keys_present": admin_keys_present,
            "hashscan_url": hashscan_url,
            "contract_id": final_contract_id,
            "evm_address": evm_address
        }
        
    except Exception as e:
        return {
            "bytecode_present": False,
            "admin_keys_present": False,
            "hashscan_url": get_hashscan_url("contract", contract_id),
            "contract_id": contract_id,
            "evm_address": "",
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the fetchers
    print("Testing Mirror Node fetchers...")
    
    # Test with a known testnet token (you might need to replace with actual testnet token)
    test_token = "0.0.123456"  # Replace with actual testnet token ID
    
    print(f"\nTesting token fetch for {test_token}:")
    token_info = hedera_token(test_token)
    print(f"Token type: {token_info['type']}")
    print(f"Keys: {token_info['keys']}")
    print(f"HashScan URL: {token_info['hashscan_url']}")
    
    print(f"\nTesting contract fetch for {test_token}:")
    contract_info = hedera_contract(test_token)
    print(f"Bytecode present: {contract_info['bytecode_present']}")
    print(f"Admin keys present: {contract_info['admin_keys_present']}")
    print(f"HashScan URL: {contract_info['hashscan_url']}")