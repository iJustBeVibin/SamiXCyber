"""
HashScan API fetcher and verification checker.
Checks contract verification status via Sourcify and builds explorer links.
"""

import requests
from typing import Dict, Any
from config import (
    get_hashscan_url,
    API_TIMEOUT,
    API_RETRIES,
    REQUEST_DELAY,
    NETWORK
)


def _make_request_with_retries(url: str, timeout: int = API_TIMEOUT) -> Dict[str, Any]:
    """
    Make HTTP request with retry logic, similar to mirror.py
    """
    import time
    last_exception = None
    
    for attempt in range(API_RETRIES + 1):
        try:
            if attempt > 0:
                time.sleep(REQUEST_DELAY * attempt)
                
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


def check_sourcify_verification(contract_address: str) -> Dict[str, bool]:
    """
    Check if contract is verified on Sourcify.
    
    Args:
        contract_address: EVM address of the contract
        
    Returns:
        Dictionary with verification status:
        {
            "verified": bool,
            "full_match": bool,
            "partial_match": bool
        }
    """
    try:
        # Sourcify API endpoint for testnet
        sourcify_base = "https://repo.sourcify.dev"
        
        # Try to get files for full verification
        files_url = f"{sourcify_base}/contracts/full_match/296/{contract_address}/"
        
        try:
            response = requests.get(files_url, timeout=API_TIMEOUT)
            if response.status_code == 200:
                return {
                    "verified": True,
                    "full_match": True,
                    "partial_match": False
                }
        except:
            pass
        
        # Try partial match
        partial_url = f"{sourcify_base}/contracts/partial_match/296/{contract_address}/"
        try:
            response = requests.get(partial_url, timeout=API_TIMEOUT)
            if response.status_code == 200:
                return {
                    "verified": True,
                    "full_match": False,
                    "partial_match": True
                }
        except:
            pass
        
        # Not verified
        return {
            "verified": False,
            "full_match": False,
            "partial_match": False
        }
        
    except Exception:
        # Default to not verified on any error
        return {
            "verified": False,
            "full_match": False,
            "partial_match": False
        }


def hedera_verification_status(contract_id: str) -> Dict[str, Any]:
    """
    Get comprehensive verification status for a Hedera contract.
    
    Args:
        contract_id: Contract ID (0.0.12345) or EVM address (0x...)
        
    Returns:
        Dictionary containing verification info:
        {
            "verified": bool,
            "bytecode_only": bool,
            "admin_keys_present": bool,
            "hashscan_url": str,
            "contract_id": str,
            "evm_address": str
        }
    """
    try:
        # Import here to avoid circular imports
        from fetch.mirror import hedera_contract
        
        # Get contract info from Mirror Node
        contract_info = hedera_contract(contract_id)
        
        # Check verification status via Sourcify if we have EVM address
        verified = False
        evm_address = contract_info.get("evm_address", "")
        
        if evm_address and evm_address.startswith("0x"):
            verification = check_sourcify_verification(evm_address)
            verified = verification["verified"]
        
        # Determine if we have bytecode but no verification (bytecode_only)
        bytecode_present = contract_info.get("bytecode_present", False)
        bytecode_only = bytecode_present and not verified
        
        return {
            "verified": verified,
            "bytecode_only": bytecode_only,
            "admin_keys_present": contract_info.get("admin_keys_present", False),
            "hashscan_url": contract_info.get("hashscan_url", ""),
            "contract_id": contract_info.get("contract_id", contract_id),
            "evm_address": evm_address
        }
        
    except Exception as e:
        # Return safe defaults on error
        return {
            "verified": False,
            "bytecode_only": False,
            "admin_keys_present": False,
            "hashscan_url": get_hashscan_url("contract", contract_id),
            "contract_id": contract_id,
            "evm_address": "",
            "error": str(e)
        }


def build_explorer_links(entity_type: str, entity_id: str) -> Dict[str, str]:
    """
    Build explorer links for tokens or contracts.
    
    Args:
        entity_type: "token" or "contract"
        entity_id: Entity ID or address
        
    Returns:
        Dictionary with explorer links:
        {
            "hashscan": str
        }
    """
    return {
        "hashscan": get_hashscan_url(entity_type, entity_id)
    }


def get_contract_metadata(contract_id: str) -> Dict[str, Any]:
    """
    Get additional contract metadata that might be useful.
    This is a placeholder for future enhancements.
    
    Args:
        contract_id: Contract ID or address
        
    Returns:
        Dictionary with metadata
    """
    # For now, just return verification status
    # In the future, could include:
    # - Compiler version
    # - Optimization settings
    # - Constructor arguments
    # - Creation timestamp
    
    return hedera_verification_status(contract_id)


if __name__ == "__main__":
    # Test the verification checker
    print("Testing HashScan verification checker...")
    
    # Test with example addresses (these may not exist, just for testing structure)
    test_addresses = [
        "0.0.123456",  # Hedera ID
        "0x1234567890123456789012345678901234567890"  # EVM address
    ]
    
    for addr in test_addresses:
        print(f"\\nTesting verification for {addr}:")
        
        verification_info = hedera_verification_status(addr)
        print(f"Verified: {verification_info['verified']}")
        print(f"Bytecode only: {verification_info['bytecode_only']}")
        print(f"Admin keys present: {verification_info['admin_keys_present']}")
        print(f"HashScan URL: {verification_info['hashscan_url']}")
        
        if "error" in verification_info:
            print(f"Error: {verification_info['error']}")
        
        # Test explorer links
        links = build_explorer_links("contract", addr)
        print(f"Explorer links: {links}")