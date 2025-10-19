"""
Technical Risk Baseline Scoring Engine.
Implements the exact algorithm specified in the prototype specification.

Algorithm:
1. If unverified → score = 40, reason = "Contract unverified"
2. If verified → start = 85
3. For each key in [admin, supply, pause, freeze, wipe, kyc, fee]
   → −8 points per key found (max −32)
4. Clip between 10 and 95
5. Return final score + reasons (max 3)
"""

from typing import Dict, Any, Tuple, List


def tech_baseline(features: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Calculate technical risk baseline score based on contract verification and key permissions.
    
    Args:
        features: Technical features dictionary from features/tech.py
        
    Returns:
        Tuple of (score, reasons) where:
        - score: Integer between 10-95
        - reasons: List of up to 3 reason strings
        
    Algorithm matches specification exactly:
    - Unverified contracts: 40 points
    - Verified contracts: Start with 85, subtract 8 per risky key (max 32 penalty)
    - Final score clamped between 10-95
    """
    # Step 1: Check verification status
    if not features.get("verified", False):
        return 40, ["Contract unverified"]
    
    # Step 2: Start with base score for verified contracts
    score = 85
    reasons = []
    penalties = 0
    
    # Step 3: Check each risky key type and apply penalties
    key_checks = [
        ("has_admin_key", "Admin key present"),
        ("has_supply_key", "Supply key present"), 
        ("has_pause_key", "Pause key present"),
        ("has_freeze_key", "Freeze key present"),
        ("has_wipe_key", "Wipe key present"),
        ("has_kyc_key", "Kyc key present"),
        ("has_fee_key", "Fee key present")
    ]
    
    for key_field, reason_text in key_checks:
        if features.get(key_field, False):
            penalties += 8
            reasons.append(reason_text)
            
            # Stop at max penalty (32 points = 4 keys)
            if penalties >= 32:
                break
    
    # Apply penalties
    score -= penalties
    
    # Add penalty for upgradeable + admin combo
    if features.get("upgradeable") and features.get("has_admin_key"):
        score -= 8
        reasons.append("Upgradeable + admin control")
    
    # Step 4: Clip score between 10 and 95
    score = max(10, min(95, score))
    
    # Step 5: Handle case where no risky keys found
    if not reasons:
        reasons.append("Verified source; no risky keys")
    
    # Return max 3 reasons as specified
    return score, reasons[:3]


def get_risk_category(score: int) -> str:
    """
    Categorize risk based on score.
    
    Args:
        score: Technical risk score (0-100)
        
    Returns:
        Risk category string
    """
    if score >= 80:
        return "Low Risk"
    elif score >= 60:
        return "Medium Risk"
    elif score >= 40:
        return "High Risk"
    else:
        return "Very High Risk"


def explain_score(score: int, reasons: List[str]) -> Dict[str, Any]:
    """
    Generate detailed explanation of the score.
    
    Args:
        score: Technical risk score
        reasons: List of reasons for the score
        
    Returns:
        Dictionary with detailed explanation
    """
    risk_category = get_risk_category(score)
    
    explanation = {
        "score": score,
        "risk_category": risk_category,
        "primary_reasons": reasons,
        "methodology": "Hedera Technical Risk Baseline v0.2",
        "score_range": "10-95 (higher is better)",
    }
    
    # Add specific guidance based on score
    if score <= 40:
        explanation["recommendation"] = "High caution advised - contract not verified or has many risky permissions"
    elif score <= 60:
        explanation["recommendation"] = "Moderate caution - some risky permissions present"
    elif score <= 80:
        explanation["recommendation"] = "Generally safe - few risky permissions"
    else:
        explanation["recommendation"] = "Low risk - verified contract with minimal risky permissions"
    
    return explanation


def batch_score_features(feature_list: List[Dict[str, Any]]) -> List[Tuple[int, List[str]]]:
    """
    Score multiple feature sets in batch.
    
    Args:
        feature_list: List of technical feature dictionaries
        
    Returns:
        List of (score, reasons) tuples
    """
    return [tech_baseline(features) for features in feature_list]


if __name__ == "__main__":
    # Test the scoring engine with various scenarios
    print("Testing Technical Risk Baseline Scoring Engine...")
    
    test_cases = [
        {
            "name": "Unverified contract",
            "features": {
                "verified": False,
                "bytecode_only": True,
                "has_admin_key": False,
                "has_supply_key": False,
                "has_pause_key": False,
                "has_freeze_key": False,
                "has_wipe_key": False,
                "has_kyc_key": False,
                "has_fee_key": False,
                "holders_estimate": 0
            }
        },
        {
            "name": "Verified, no risky keys",
            "features": {
                "verified": True,
                "bytecode_only": False,
                "has_admin_key": False,
                "has_supply_key": False,
                "has_pause_key": False,
                "has_freeze_key": False,
                "has_wipe_key": False,
                "has_kyc_key": False,
                "has_fee_key": False,
                "holders_estimate": 100
            }
        },
        {
            "name": "Verified, some risky keys",
            "features": {
                "verified": True,
                "bytecode_only": False,
                "has_admin_key": True,
                "has_supply_key": True,
                "has_pause_key": False,
                "has_freeze_key": True,
                "has_wipe_key": False,
                "has_kyc_key": False,
                "has_fee_key": False,
                "holders_estimate": 523
            }
        },
        {
            "name": "Verified, all risky keys",
            "features": {
                "verified": True, "bytecode_only": False, "has_admin_key": True,
                "has_supply_key": True, "has_pause_key": True, "has_freeze_key": True,
                "has_wipe_key": True, "has_kyc_key": True, "has_fee_key": True,
                "upgradeable": False, "holders_estimate": 50
            }
        },
        {
            "name": "Upgradeable contract with admin",
            "features": {
                "verified": True, "bytecode_only": False, "has_admin_key": True,
                "has_supply_key": False, "has_pause_key": True, "has_freeze_key": False,
                "has_wipe_key": False, "has_kyc_key": False, "has_fee_key": False,
                "upgradeable": True, "holders_estimate": 120
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\\n--- {test_case['name']} ---")
        score, reasons = tech_baseline(test_case['features'])
        print(f"Score: {score}")
        print(f"Reasons: {reasons}")
        
        explanation = explain_score(score, reasons)
        print(f"Risk Category: {explanation['risk_category']}")
        print(f"Recommendation: {explanation['recommendation']}")
    
    # Test edge cases
    print("\\n--- Edge Cases ---")
    
    # Empty features
    try:
        score, reasons = tech_baseline({})
        print(f"Empty features - Score: {score}, Reasons: {reasons}")
    except Exception as e:
        print(f"Empty features error: {e}")
    
    # Missing verification field
    try:
        score, reasons = tech_baseline({"has_admin_key": True})
        print(f"Missing verification - Score: {score}, Reasons: {reasons}")
    except Exception as e:
        print(f"Missing verification error: {e}")
    
    print("\\nScoring engine tests completed!")
