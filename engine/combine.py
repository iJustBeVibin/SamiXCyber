"""
Combined scoring module - placeholder for future market risk integration.
Currently only passes through technical scores.
"""

from typing import Dict, Any, Optional, Tuple, List


def combine_scores(tech_score: int, 
                  tech_reasons: List[str],
                  market_score: Optional[int] = None,
                  market_reasons: Optional[List[str]] = None) -> Tuple[int, List[str]]:
    """
    Combine technical and market risk scores.
    
    Currently this is a placeholder that only returns the technical score.
    Future versions will implement proper combined scoring when market risk is added.
    
    Args:
        tech_score: Technical risk score (10-95)
        tech_reasons: Technical risk reasons
        market_score: Market risk score (future use)
        market_reasons: Market risk reasons (future use)
        
    Returns:
        Tuple of (combined_score, combined_reasons)
    """
    # For now, just pass through technical score
    # TODO: Implement proper combined scoring when market risk is available
    
    if market_score is None:
        # Phase 1: Tech-only scoring
        return tech_score, tech_reasons
    else:
        # Future: Implement combined scoring algorithm
        # This might be weighted average, minimum, or more sophisticated logic
        # Placeholder implementation:
        combined_score = int((tech_score + market_score) / 2)
        combined_reasons = tech_reasons + (market_reasons or [])
        return combined_score, combined_reasons[:3]  # Max 3 reasons


def get_overall_assessment(combined_score: int, 
                          combined_reasons: List[str],
                          tech_score: int,
                          market_score: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate overall risk assessment combining all factors.
    
    Args:
        combined_score: Final combined risk score
        combined_reasons: List of combined reasons
        tech_score: Technical risk component
        market_score: Market risk component (future)
        
    Returns:
        Dictionary with overall assessment
    """
    assessment = {
        "overall_score": combined_score,
        "overall_reasons": combined_reasons,
        "component_scores": {
            "technical": tech_score
        },
        "scoring_method": "tech-only-v0.2"
    }
    
    if market_score is not None:
        assessment["component_scores"]["market"] = market_score
        assessment["scoring_method"] = "combined-v1.0"
    
    # Risk categorization
    if combined_score >= 80:
        assessment["risk_level"] = "Low"
        assessment["color_code"] = "green"
    elif combined_score >= 60:
        assessment["risk_level"] = "Medium"
        assessment["color_code"] = "yellow"
    elif combined_score >= 40:
        assessment["risk_level"] = "High" 
        assessment["color_code"] = "orange"
    else:
        assessment["risk_level"] = "Very High"
        assessment["color_code"] = "red"
    
    return assessment


if __name__ == "__main__":
    # Test the combine module
    print("Testing combine module (tech-only mode)...")
    
    # Test tech-only combination
    tech_score = 61
    tech_reasons = ["Admin key present", "Supply key present"]
    
    combined_score, combined_reasons = combine_scores(tech_score, tech_reasons)
    print(f"Tech-only result: Score={combined_score}, Reasons={combined_reasons}")
    
    # Test overall assessment
    assessment = get_overall_assessment(combined_score, combined_reasons, tech_score)
    print(f"Assessment: {assessment}")
    
    # Test with mock market data (future functionality)
    print("\\nTesting with mock market data...")
    market_score = 70
    market_reasons = ["Low liquidity", "High volatility"]
    
    combined_score2, combined_reasons2 = combine_scores(
        tech_score, tech_reasons, market_score, market_reasons
    )
    print(f"Combined result: Score={combined_score2}, Reasons={combined_reasons2}")
    
    assessment2 = get_overall_assessment(combined_score2, combined_reasons2, tech_score, market_score)
    print(f"Combined assessment: {assessment2}")
    
    print("\\nCombine module tests completed!")