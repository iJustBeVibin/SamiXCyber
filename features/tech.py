"""
Technical features extraction module.
Converts raw token/contract data into standardized AI-ready features.

The feature schema is FROZEN and must not change without version updates.
"""

from typing import Dict, Any, Optional


# FROZEN FEATURE SCHEMA - DO NOT MODIFY
TECH_FEATURE_SCHEMA = {
    "verified": bool,
    "bytecode_only": bool,
    "has_admin_key": bool,
    "has_supply_key": bool,
    "has_pause_key": bool,
    "has_freeze_key": bool,
    "has_wipe_key": bool,
    "has_kyc_key": bool,
    "has_fee_key": bool,
    "holders_estimate": int,
    "upgradeable": bool,
    "chain": str,
    "network": str,
}

def build_tech_features(tech_facts: Dict[str, Any], chain: str, network: str) -> Dict[str, Any]:
    """
    Build standardized technical features from unified adapter output.
    
    Args:
        tech_facts: Raw data from a chain adapter (e.g., hedera.py)
        chain: The blockchain identifier (e.g., "hedera")
        network: The network identifier (e.g., "mainnet")
        
    Returns:
        Dictionary with frozen technical features.
    """
    gov_flags = tech_facts.get("governance_flags", {})
    
    features = {
        "verified": tech_facts.get("verified", False),
        "bytecode_only": tech_facts.get("bytecode_only", False),
        "has_admin_key": tech_facts.get("admin_keys_present", False),
        "has_supply_key": gov_flags.get("supply", False),
        "has_pause_key": gov_flags.get("pause", False),
        "has_freeze_key": gov_flags.get("freeze", False),
        "has_wipe_key": gov_flags.get("wipe", False),
        "has_kyc_key": gov_flags.get("kyc", False),
        "has_fee_key": gov_flags.get("fee", False),
        "upgradeable": gov_flags.get("upgradeable", False),
        "holders_estimate": tech_facts.get("holders_estimate") or 0,
        "chain": chain,
        "network": network,
    }
    
    # Ensure all schema keys are present with correct types
    for key, expected_type in TECH_FEATURE_SCHEMA.items():
        if key not in features:
            if expected_type == bool:
                features[key] = False
            elif expected_type == int:
                features[key] = 0
            elif expected_type == str:
                features[key] = ""
        # Coerce type if necessary
        elif not isinstance(features[key], expected_type):
             try:
                features[key] = expected_type(features[key])
             except (ValueError, TypeError):
                features[key] = expected_type() # Fallback to default value

    return features


def validate_tech_features(features: Dict[str, Any]) -> bool:
    """
    Validate that feature dictionary matches the frozen schema.
    
    Args:
        features: Feature dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check all required keys are present
        for key in TECH_FEATURE_SCHEMA:
            if key not in features:
                return False
                
            # Check data types
            expected_type = TECH_FEATURE_SCHEMA[key]
            actual_value = features[key]
            
            if not isinstance(actual_value, expected_type):
                return False
        
        # Check for unexpected keys (schema violations)
        for key in features:
            if key not in TECH_FEATURE_SCHEMA:
                # Allow extra keys for debugging, but warn
                continue
        
        return True
        
    except Exception:
        return False


def get_feature_summary(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a human-readable summary of the features.
    
    Args:
        features: Technical features dictionary
        
    Returns:
        Dictionary with summary information
    """
    risky_keys = []
    for key, value in features.items():
        if key.startswith("has_") and value:
            key_name = key.replace("has_", "").replace("_key", "")
            risky_keys.append(key_name.capitalize())
    
    return {
        "verification_status": "Verified" if features["verified"] else "Unverified",
        "bytecode_available": not features["bytecode_only"],
        "risky_keys_count": len(risky_keys),
        "risky_keys": risky_keys,
        "holders_count": features["holders_estimate"],
        "has_risky_permissions": len(risky_keys) > 0
    }


if __name__ == "__main__":
    print("Testing unified technical features builder...")
    
    # Sample Hedera data
    sample_hedera_facts = {
      "verified": True, "bytecode_only": False, "admin_keys_present": True,
      "governance_flags": {
        "admin": True, "supply": True, "pause": False, "freeze": True,
        "wipe": False, "kyc": False, "fee": False
      },
      "holders_estimate": 523
    }
    
    # Sample Ethereum data
    sample_ethereum_facts = {
      "verified": True, "bytecode_only": False, "admin_keys_present": True,
      "governance_flags": {
        "admin": True, "pause": True, "supply": False, "upgradeable": True
      },
      "holders_estimate": None
    }
    
    # Build features for Hedera
    hedera_features = build_tech_features(sample_hedera_facts, "hedera", "mainnet")
    print("\n--- Hedera Features ---")
    import json
    print(json.dumps(hedera_features, indent=2))
    print(f"Valid: {validate_tech_features(hedera_features)}")
    
    # Build features for Ethereum
    ethereum_features = build_tech_features(sample_ethereum_facts, "ethereum", "mainnet")
    print("\n--- Ethereum Features ---")
    print(json.dumps(ethereum_features, indent=2))
    print(f"Valid: {validate_tech_features(ethereum_features)}")

    # Test summary
    summary = get_feature_summary(ethereum_features)
    print("\n--- Ethereum Summary ---")
    print(json.dumps(summary, indent=2))
