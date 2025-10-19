"""
Hedera Hashgraph adapter for Multi-Chain Technical Risk Scoring System.
Implements unified interface for Hedera token and contract analysis.
"""

import time
import requests
import logging
import re
from typing import Dict, Any, Optional
from config import (
    get_mirror_endpoint,
    get_explorer_url,
    get_chain_config,
    API_TIMEOUT,
    API_RETRIES,
    REQUEST_DELAY,
    assert_read_only
)


def _make_request_with_retries(url: str, timeout: int = API_TIMEOUT) -> Dict[str, Any]:
    """Make HTTP request with retry logic."""
    assert_read_only()  # Safety check
    
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
            # Handle 404 specifically to return empty data gracefully
            if e.response is not None and e.response.status_code == 404:
                logging.warning(f"Request to {url} returned 404 Not Found.")
                return {} # Return empty dict for 404
            
            if attempt < API_RETRIES:
                continue
            else:
                break
    
    raise last_exception

def _log_request_details(url: str, status_code: int, response_preview: str, entity_id: str, network: str):
    """Helper to log request details for debugging."""
    logging.info(f"[{entity_id}@{network}] Request URL: {url}")
    logging.info(f"[{entity_id}@{network}] Status Code: {status_code}")
    logging.info(f"[{entity_id}@{network}] Response Preview: {response_preview[:200]}...") # Log first 200 chars

def _check_sourcify_verification(contract_address: str, network: str = "testnet") -> Dict[str, bool]:
    """Check if contract is verified on Sourcify."""
    try:
        # Hedera network IDs: testnet=296, mainnet=295
        network_id = "296" if network == "testnet" else "295"
        sourcify_base = "https://repo.sourcify.dev"
        
        # Try full match first
        full_url = f"{sourcify_base}/contracts/full_match/{network_id}/{contract_address}/"
        try:
            response = requests.get(full_url, timeout=API_TIMEOUT)
            if response.status_code == 200:
                return {"verified": True, "full_match": True, "partial_match": False}
        except:
            pass
        
        # Try partial match
        partial_url = f"{sourcify_base}/contracts/partial_match/{network_id}/{contract_address}/"
        try:
            response = requests.get(partial_url, timeout=API_TIMEOUT)
            if response.status_code == 200:
                return {"verified": True, "full_match": False, "partial_match": True}
        except:
            pass
        
        return {"verified": False, "full_match": False, "partial_match": False}
        
    except Exception:
        return {"verified": False, "full_match": False, "partial_match": False}


def _get_token_info(entity_id: str, network: str) -> Dict[str, Any]:
    """Fetch and parse token information from Mirror Node."""
    token_url = get_mirror_endpoint(f"tokens/{entity_id}", network)
    token_data = _make_request_with_retries(token_url)
    
    # If token_data is empty (404), return empty dict
    if not token_data:
        return {}
    
    governance_flags = {
        "admin": bool(token_data.get("admin_key")),
        "supply": bool(token_data.get("supply_key")),
        "pause": bool(token_data.get("pause_key")),
        "freeze": bool(token_data.get("freeze_key")),
        "wipe": bool(token_data.get("wipe_key")),
        "kyc": bool(token_data.get("kyc_key")),
        "fee": bool(token_data.get("fee_schedule_key")),
    }
    
    holders_estimate = 0
    try:
        balances_url = get_mirror_endpoint(f"tokens/{entity_id}/balances?limit=100", network)
        balances_data = _make_request_with_retries(balances_url)
        if "balances" in balances_data:
            holders_estimate = len(balances_data["balances"])
    except Exception:
        pass  # Holder count is optional

    return {
        "governance_flags": governance_flags,
        "holders_estimate": holders_estimate,
        "token_id": token_data.get("token_id", entity_id),
        "name": token_data.get("name", ""),
        "symbol": token_data.get("symbol", ""),
        "type": token_data.get("type", "UNKNOWN"),
    }

def _get_contract_info(entity_id: str, network: str) -> Dict[str, Any]:
    """Fetch and parse contract information, including verification."""
    try:
        contract_url = get_mirror_endpoint(f"contracts/{entity_id}", network)
        contract_data = _make_request_with_retries(contract_url)
        
        if not contract_data.get("bytecode"):
            return {"bytecode_only": False, "verified": False, "has_admin": False}

        evm_address = contract_data.get("evm_address")
        verified = False
        if evm_address:
            verification = _check_sourcify_verification(evm_address, network)
            verified = verification.get("verified", False)
            
        return {
            "bytecode_only": not verified,
            "verified": verified,
            "has_admin": bool(contract_data.get("admin_key")),
        }
    except Exception:
        return {"bytecode_only": False, "verified": False, "has_admin": False}

def get_tech_facts(id_or_addr: str, network: str = "testnet") -> Dict[str, Any]:
    """
    Get technical facts for a Hedera token or contract.
    
    Args:
        id_or_addr: Hedera ID (0.0.12345) or EVM address (0x...)
        network: 'testnet' or 'mainnet'
        
    Returns:
        Unified TechFacts dictionary
    """
    entity_id = id_or_addr.strip()
    
    token_info = {}
    contract_info = {}
    
    try:
        token_info = _get_token_info(entity_id, network)
        contract_info = _get_contract_info(entity_id, network)
        
        # If token_info is empty, it means the token was not found (404)
        if not token_info:
            logging.error(f"Token/Contract info not found for {entity_id} on {network}.")
            return {
                "verified": False,
                "bytecode_only": True, # Mark as bytecode_only if data is unavailable
                "admin_keys_present": False,
                "governance_flags": {key: False for key in ["admin", "supply", "pause", "freeze", "wipe", "kyc", "fee"]},
                "holders_estimate": 0,
                "explorer_url": get_explorer_url("hedera", "token", entity_id, network),
                "token_info": {"token_id": entity_id, "name": "", "symbol": "", "type": "UNKNOWN"},
                "error": f"Data unavailable (Hedera Mirror Node)"
            }

        admin_keys_present = token_info["governance_flags"]["admin"] or contract_info.get("has_admin", False)
        
        entity_type = "contract" if contract_info.get("bytecode_only") or contract_info.get("verified") else "token"
        
        return {
            "verified": contract_info.get("verified", False),
            "bytecode_only": contract_info.get("bytecode_only", False),
            "admin_keys_present": admin_keys_present,
            "governance_flags": token_info["governance_flags"],
            "holders_estimate": token_info["holders_estimate"],
            "explorer_url": get_explorer_url("hedera", entity_type, token_info["token_id"], network),
            "token_info": {
                "token_id": token_info["token_id"],
                "name": token_info["name"],
                "symbol": token_info["symbol"],
                "type": token_info["type"],
            }
        }
        
    except Exception as e:
        logging.error(f"Unexpected error processing Hedera facts for {entity_id}: {e}")
        return {
            "verified": False,
            "bytecode_only": True, # Mark as bytecode_only if any error occurs
            "admin_keys_present": False,
            "governance_flags": {key: False for key in ["admin", "supply", "pause", "freeze", "wipe", "kyc", "fee"]},
            "holders_estimate": 0,
            "explorer_url": get_explorer_url("hedera", "token", entity_id, network),
            "token_info": {"token_id": entity_id, "name": "", "symbol": "", "type": "UNKNOWN"},
            "error": f"Data unavailable (Hedera Mirror Node): {e}"
        }

def validate_hedera_id(entity_id: str) -> bool:
    """Validate if the input is a valid Hedera ID format (e.g., 0.0.12345)."""
    return bool(re.match(r"^\d+\.\d+\.\d+$", entity_id))


if __name__ == "__main__":
    # Test the Hedera adapter with a known mainnet token
    print("Testing Hedera adapter...")
    
    # Hedera mainnet example: 0.0.107594 (a simple fungible token)
    # This token has an admin key but other keys are disabled.
    test_cases = [
        ("0.0.107594", "mainnet"),  # Valid mainnet token
    ]
    
    for entity_id, network in test_cases:
        print(f"\n--- Testing {entity_id} on {network} ---")
        try:
            facts = get_tech_facts(entity_id, network)
            
            # Pretty print results
            import json
            print(json.dumps(facts, indent=2))

            if "error" in facts:
                print(f"\n[WARNING] Encountered an error: {facts['error']}")
            else:
                # Validate basic structure
                assert "verified" in facts
                assert "governance_flags" in facts
                assert "explorer_url" in facts
                print("\n✅ Hedera test passed!")
                
        except Exception as e:
            print(f"\n[ERROR] Test failed for {entity_id} on {network}: {e}")
    
    print("\n--- Hedera adapter test completed! ---")
