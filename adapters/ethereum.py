"""
Ethereum adapter for Multi-Chain Technical Risk Scoring System.
Implements unified interface for Ethereum smart contract analysis,
including proxy resolution and robust verification checks.
"""

import time
import requests
import logging
from typing import Dict, Any, Optional

from config import (
    get_chain_config,
    get_explorer_url,
    API_TIMEOUT,
    API_RETRIES,
    REQUEST_DELAY,
    assert_read_only
)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _make_request_with_retries(url: str, params: Dict = None, timeout: int = API_TIMEOUT) -> Dict[str, Any]:
    """Make HTTP request with retry logic and backoff."""
    assert_read_only()
    last_exception = None
    for attempt in range(API_RETRIES + 1):
        try:
            time.sleep(REQUEST_DELAY * attempt)  # Exponential backoff
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code in [403, 429]:
                logging.warning(f"Etherscan API rate limit hit (status {response.status_code}). Retrying...")
                if attempt < API_RETRIES:
                    continue
                else:
                    logging.error("Etherscan API rate limit exceeded after multiple retries.")
                    response.raise_for_status()

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            last_exception = e
    raise last_exception

def _get_etherscan_source(address: str, network: str) -> Dict[str, Any]:
    """Fetch source code and ABI from Etherscan, handling proxies."""
    config = get_chain_config("ethereum", network)
    
    # Use Etherscan API V2 format: https://api.etherscan.io/v2/api?chainid=1&module=...
    # Determine chain ID
    chain_id = "1" if network == "mainnet" else "5"  # 5 for Goerli testnet
    
    params = {
        "chainid": chain_id,
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": config["etherscan_key"]
    }
    
    # Log the request URL without the API key for security
    params_for_logging = params.copy()
    params_for_logging["apikey"] = "REDACTED"
    request_url_for_logging = requests.Request('GET', config["etherscan_api"], params=params_for_logging).prepare().url
    logging.info(f"Querying Etherscan for address: {address} | URL: {request_url_for_logging}")

    data = _make_request_with_retries(config["etherscan_api"], params)
    logging.info(f"Etherscan raw response for {address}: {data}")
    
    if data.get("status") == "0" or not data.get("result"):
        logging.warning(f"Etherscan returned no data for {address}. Message: {data.get('message')}, Result: {data.get('result')}")
        return {}

    source_info = data["result"][0]
    
    # Handle proxy contracts
    if source_info.get("Proxy") == "1" and source_info.get("Implementation"):
        impl_address = source_info["Implementation"]
        logging.info(f"Proxy contract detected. Hopping from {address} to implementation {impl_address}")
        return _get_etherscan_source(impl_address, network)
        
    return source_info

def _check_sourcify_verification(address: str, network: str) -> bool:
    """Check Sourcify for full or partial contract verification."""
    # Hedera network IDs for Sourcify: testnet=296, mainnet=295. Ethereum: mainnet=1, testnet=5.
    # The original code used '1' for mainnet and '5' for testnet, which is correct for Ethereum.
    network_id = "1" if network == "mainnet" else "5"
    try:
        config = get_chain_config("ethereum", network)
        url = f"{config['sourcify_api']}/check-by-addresses"
        params = {"addresses": address.lower(), "chainIds": network_id}
        
        logging.info(f"Querying Sourcify for address: {address.lower()}")
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if data and any(d.get("status") in ["perfect", "partial"] for d in data):
                logging.info(f"Sourcify verification found for {address}")
                return True
    except Exception as e:
        logging.error(f"Sourcify check failed for {address}: {e}")
    return False

def _analyze_abi_for_flags(abi: str) -> Dict[str, bool]:
    """Analyze ABI for common governance patterns (case-insensitive)."""
    flags = {"admin": False, "pause": False, "supply": False}
    if not isinstance(abi, str): return flags
    
    abi_lower = abi.lower()
    if '"name":"owner"' in abi_lower and '"name":"transferownership"' in abi_lower:
        flags["admin"] = True
    if '"name":"grantrole"' in abi_lower:
        flags["admin"] = True
    if '"name":"pause"' in abi_lower and '"name":"unpause"' in abi_lower:
        flags["pause"] = True
    if '"name":"mint"' in abi_lower or '"name":"burn"' in abi_lower:
        flags["supply"] = True
        
    return flags

def get_tech_facts(id_or_addr: str, network: str = "mainnet") -> Dict[str, Any]:
    """Get technical facts for an Ethereum smart contract."""
    if not id_or_addr.startswith("0x") or len(id_or_addr) != 42:
        raise ValueError("Invalid input. Provide a 0x... address.")
        
    address = id_or_addr.strip().lower()
    original_address = address  # Keep track of the original address
    
    etherscan_source = {}
    etherscan_verified = False
    sourcify_verified = False
    is_proxy = False
    
    try:
        # First, check the original address for proxy status
        config = get_chain_config("ethereum", network)
        chain_id = "1" if network == "mainnet" else "5"
        params = {
            "chainid": chain_id,
            "module": "contract",
            "action": "getsourcecode",
            "address": original_address,
            "apikey": config["etherscan_key"]
        }
        data = _make_request_with_retries(config["etherscan_api"], params)
        
        if data.get("status") == "1" and data.get("result"):
            original_source_info = data["result"][0]
            is_proxy = original_source_info.get("Proxy") == "1"
            
            if is_proxy and original_source_info.get("Implementation"):
                # If it's a proxy, get the implementation contract details
                logging.info(f"Proxy detected at {original_address}, implementation: {original_source_info.get('Implementation')}")
                etherscan_source = _get_etherscan_source(original_address, network)
            else:
                etherscan_source = original_source_info
        else:
            etherscan_source = _get_etherscan_source(address, network)
            
        etherscan_verified = bool(etherscan_source.get("SourceCode"))
        
        # Log Etherscan verification status
        logging.info(f"Etherscan verification status for {address}: {etherscan_verified}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Etherscan API error for {address}: {e}. Attempting Sourcify fallback.")
        # If Etherscan fails (e.g., rate limit, no data), proceed to Sourcify
        etherscan_verified = False # Explicitly set to False if Etherscan failed
    except Exception as e:
        logging.error(f"Unexpected error during Etherscan fetch for {address}: {e}")
        etherscan_verified = False

    # Always attempt Sourcify if Etherscan didn't confirm verification
    if not etherscan_verified:
        sourcify_verified = _check_sourcify_verification(address, network)
        logging.info(f"Sourcify verification status for {address}: {sourcify_verified}")

    verified = etherscan_verified or sourcify_verified
    
    # If both failed, ensure we have a default error state
    if not verified and not etherscan_source:
        logging.error(f"Both Etherscan and Sourcify failed for {address}. Marking as unverified.")
        return {
            "verified": False, "bytecode_only": True, "admin_keys_present": False,
            "governance_flags": {key: False for key in ["admin", "pause", "supply", "upgradeable"]},
            "holders_estimate": None,
            "explorer_url": get_explorer_url("ethereum", "address", original_address, network),
            "error": f"Data unavailable (Etherscan/Sourcify)"
        }

    abi = etherscan_source.get("ABI")
    gov_flags = _analyze_abi_for_flags(abi)

    # Log final verification status and chosen address for explorer link
    final_address_for_explorer = original_address
    logging.info(f"Final verification status for {address}: {verified}. Using {final_address_for_explorer} for explorer link.")

    return {
        "verified": verified,
        "bytecode_only": not verified,
        "admin_keys_present": gov_flags["admin"],
        "governance_flags": {
            "admin": gov_flags["admin"],
            "pause": gov_flags["pause"],
            "supply": gov_flags["supply"],
            "freeze": False, "wipe": False, "kyc": False, "fee": False,
            "upgradeable": is_proxy,
        },
        "holders_estimate": None,
        "explorer_url": get_explorer_url("ethereum", "address", final_address_for_explorer, network),
        "debug": {
            "etherscan_verified": etherscan_verified,
            "sourcify_verified": sourcify_verified,
            "is_proxy": is_proxy,
            "implementation": etherscan_source.get("Implementation", "N/A")
        }
    }

if __name__ == "__main__":
    # Self-check asserts from debug.md
    print("--- Running Self-Check Asserts ---")
    
    # WETH Test
    weth_addr = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    print(f"\nTesting WETH: {weth_addr}")
    weth_facts = get_tech_facts(weth_addr, "mainnet")
    assert weth_facts["explorer_url"].startswith("https://etherscan.io/address/")
    assert weth_facts["verified"] is True, weth_facts
    assert weth_facts["governance_flags"]["upgradeable"] is False, weth_facts
    print("✅ WETH Asserts Passed")

    # USDC Test
    usdc_addr = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    print(f"\nTesting USDC: {usdc_addr}")
    usdc_facts = get_tech_facts(usdc_addr, "mainnet")
    assert usdc_facts["verified"] is True, usdc_facts
    assert usdc_facts["governance_flags"]["upgradeable"] is True, usdc_facts
    # Note: USDC has admin/pause but they may not be detected from implementation ABI
    print("✅ USDC Asserts Passed")
    
    print("\n--- All asserts passed! ---")
