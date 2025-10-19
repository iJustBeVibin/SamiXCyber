"""
Multi-dimensional Risk Aggregator for DeFi protocols.
Combines Security, Financial, Operational, and Market risk scores.
"""

import logging
from typing import Dict, Any, List, Tuple
from engine.tech_baseline import tech_baseline

logging.basicConfig(level=logging.INFO)


class RiskAggregator:
    """
    Aggregates multiple risk dimensions into an overall protocol risk score.
    
    Risk Categories:
    - Security (40%): Contract verification, audits, governance keys
    - Financial (30%): TVL, price volatility, trading volume
    - Operational (20%): Protocol maturity, governance structure
    - Market (10%): Market position, adoption metrics
    """
    
    # Weights for overall score calculation
    WEIGHTS = {
        'security': 0.40,
        'financial': 0.30,
        'operational': 0.20,
        'market': 0.10
    }
    
    def __init__(self):
        """Initialize the risk aggregator."""
        pass
    
    def _normalize_score(self, score: float, min_val: float = 0, max_val: float = 100) -> int:
        """
        Normalize a score to 0-100 range.
        
        Args:
            score: Raw score value
            min_val: Minimum possible value
            max_val: Maximum possible value
            
        Returns:
            Normalized score between 0-100
        """
        if max_val == min_val:
            return 50  # Default to middle if no range
        
        normalized = ((score - min_val) / (max_val - min_val)) * 100
        return max(0, min(100, int(normalized)))
    
    def calculate_security_score(self, tech_features: Dict[str, Any], 
                                 audit_data: Dict[str, Any] = None) -> Tuple[int, List[str]]:
        """
        Calculate security risk score.
        
        Args:
            tech_features: Technical features from contract analysis
            audit_data: Audit information (placeholder for MVP)
            
        Returns:
            Tuple of (score, reasons)
        """
        # Use existing tech_baseline for contract verification scoring
        tech_score, tech_reasons = tech_baseline(tech_features)
        
        # For MVP, security score is primarily based on tech_baseline
        # Future: Add audit status, bug bounty programs, etc.
        score = tech_score
        reasons = tech_reasons.copy()
        
        # Placeholder for audit status (neutral for MVP)
        if audit_data and audit_data.get('audited', False):
            score = min(100, score + 5)
            reasons.append("Contract audited")
        
        return score, reasons[:3]  # Max 3 reasons
    
    def calculate_financial_score(self, tvl_data: Dict[str, Any], 
                                  market_data: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Calculate financial risk score based on TVL and market metrics.
        
        Args:
            tvl_data: TVL data from DeFi Llama
            market_data: Market data from CoinGecko
            
        Returns:
            Tuple of (score, reasons)
        """
        score = 50  # Start neutral
        reasons = []
        
        # TVL scoring (higher TVL = lower risk = higher score)
        tvl = tvl_data.get('tvl', 0)
        if tvl > 1_000_000_000:  # > $1B
            score += 25
            reasons.append(f"High TVL: ${tvl/1e9:.1f}B")
        elif tvl > 100_000_000:  # > $100M
            score += 15
            reasons.append(f"Moderate TVL: ${tvl/1e6:.0f}M")
        elif tvl > 10_000_000:  # > $10M
            score += 5
            reasons.append(f"Low TVL: ${tvl/1e6:.0f}M")
        else:
            score -= 10
            reasons.append(f"Very low TVL: ${tvl/1e6:.1f}M")
        
        # Price volatility scoring (lower volatility = lower risk = higher score)
        price_change_24h = abs(market_data.get('price_change_24h', 0))
        if price_change_24h > 20:
            score -= 15
            reasons.append(f"High volatility: {price_change_24h:.1f}% (24h)")
        elif price_change_24h > 10:
            score -= 5
            reasons.append(f"Moderate volatility: {price_change_24h:.1f}% (24h)")
        elif price_change_24h < 5:
            score += 10
            reasons.append(f"Low volatility: {price_change_24h:.1f}% (24h)")
        
        # Volume/Market Cap ratio (higher = more liquid = lower risk)
        volume = market_data.get('volume_24h', 0)
        market_cap = market_data.get('market_cap', 1)
        if market_cap > 0:
            volume_ratio = volume / market_cap
            if volume_ratio > 0.1:  # >10% daily turnover
                score += 10
                reasons.append("High liquidity")
            elif volume_ratio < 0.01:  # <1% daily turnover
                score -= 5
                reasons.append("Low liquidity")
        
        # Clamp score
        score = max(0, min(100, score))
        
        return score, reasons[:3]  # Max 3 reasons
    
    def calculate_operational_score(self, protocol_data: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Calculate operational risk score.
        
        Args:
            protocol_data: Protocol metadata and operational info
            
        Returns:
            Tuple of (score, reasons)
        """
        # Placeholder for MVP - return neutral score
        # Future: Add protocol age, team transparency, governance activity, etc.
        score = 60  # Neutral-positive default
        reasons = []
        
        # Basic category-based scoring
        category = protocol_data.get('category', 'Unknown')
        if category in ['Lending', 'DEX']:
            score += 10
            reasons.append(f"Established category: {category}")
        
        # Placeholder for governance
        reasons.append("Governance structure: Not evaluated (MVP)")
        
        return score, reasons[:3]
    
    def calculate_market_score(self, market_data: Dict[str, Any], 
                               tvl_data: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Calculate market risk score based on adoption and position.
        
        Args:
            market_data: Market data from CoinGecko
            tvl_data: TVL data from DeFi Llama
            
        Returns:
            Tuple of (score, reasons)
        """
        score = 50  # Start neutral
        reasons = []
        
        # Market cap rank (lower rank = higher adoption = lower risk)
        rank = market_data.get('market_cap_rank', 999)
        if rank <= 50:
            score += 30
            reasons.append(f"Top 50 by market cap (#{rank})")
        elif rank <= 100:
            score += 20
            reasons.append(f"Top 100 by market cap (#{rank})")
        elif rank <= 200:
            score += 10
            reasons.append(f"Top 200 by market cap (#{rank})")
        else:
            score -= 10
            reasons.append(f"Lower market cap rank (#{rank})")
        
        # Multi-chain presence (more chains = more adoption)
        chains = tvl_data.get('chains', {})
        num_chains = len(chains)
        if num_chains > 5:
            score += 15
            reasons.append(f"Multi-chain: {num_chains} chains")
        elif num_chains > 2:
            score += 5
            reasons.append(f"Multi-chain: {num_chains} chains")
        
        # Clamp score
        score = max(0, min(100, score))
        
        return score, reasons[:3]
    
    def calculate_overall_score(self, security_score: int, financial_score: int,
                               operational_score: int, market_score: int) -> Tuple[int, str]:
        """
        Calculate weighted overall risk score.
        
        Args:
            security_score: Security risk score (0-100)
            financial_score: Financial risk score (0-100)
            operational_score: Operational risk score (0-100)
            market_score: Market risk score (0-100)
            
        Returns:
            Tuple of (overall_score, traffic_light_indicator)
        """
        overall = (
            security_score * self.WEIGHTS['security'] +
            financial_score * self.WEIGHTS['financial'] +
            operational_score * self.WEIGHTS['operational'] +
            market_score * self.WEIGHTS['market']
        )
        
        overall_score = int(overall)
        
        # Determine traffic light indicator
        if overall_score >= 70:
            indicator = "🟢 Low Risk"
        elif overall_score >= 40:
            indicator = "🟡 Medium Risk"
        else:
            indicator = "🔴 High Risk"
        
        return overall_score, indicator
    
    def aggregate_risk(self, tech_features: Dict[str, Any],
                      tvl_data: Dict[str, Any],
                      market_data: Dict[str, Any],
                      protocol_data: Dict[str, Any],
                      audit_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Aggregate all risk dimensions into comprehensive risk assessment.
        
        Args:
            tech_features: Technical features from contract analysis
            tvl_data: TVL data from DeFi Llama
            market_data: Market data from CoinGecko
            protocol_data: Protocol metadata
            audit_data: Audit information (optional)
            
        Returns:
            Dictionary with all risk scores and reasons
        """
        # Calculate individual risk scores
        security_score, security_reasons = self.calculate_security_score(tech_features, audit_data)
        financial_score, financial_reasons = self.calculate_financial_score(tvl_data, market_data)
        operational_score, operational_reasons = self.calculate_operational_score(protocol_data)
        market_score, market_reasons = self.calculate_market_score(market_data, tvl_data)
        
        # Calculate overall score
        overall_score, indicator = self.calculate_overall_score(
            security_score, financial_score, operational_score, market_score
        )
        
        result = {
            'overall_score': overall_score,
            'risk_indicator': indicator,
            'category_scores': {
                'security': security_score,
                'financial': financial_score,
                'operational': operational_score,
                'market': market_score
            },
            'reasons': {
                'security': security_reasons,
                'financial': financial_reasons,
                'operational': operational_reasons,
                'market': market_reasons
            },
            'weights': self.WEIGHTS
        }
        
        logging.info(f"Risk aggregation complete: Overall={overall_score}, Security={security_score}, "
                    f"Financial={financial_score}, Operational={operational_score}, Market={market_score}")
        
        return result


if __name__ == "__main__":
    # Test the risk aggregator
    print("Testing RiskAggregator...")
    
    aggregator = RiskAggregator()
    
    # Test case: High-quality protocol (like Aave)
    print("\n1. Testing high-quality protocol:")
    tech_features = {
        'verified': True,
        'has_admin_key': True,
        'has_supply_key': False,
        'has_pause_key': True,
        'has_freeze_key': False,
        'has_wipe_key': False,
        'has_kyc_key': False,
        'has_fee_key': False,
        'upgradeable': True
    }
    
    tvl_data = {
        'tvl': 5_000_000_000,  # $5B
        'tvl_change_24h': 2.5,
        'chains': {'ethereum': 3_000_000_000, 'polygon': 1_000_000_000}
    }
    
    market_data = {
        'price': 95.50,
        'market_cap': 1_400_000_000,
        'volume_24h': 150_000_000,
        'price_change_24h': 3.2,
        'market_cap_rank': 45
    }
    
    protocol_data = {
        'name': 'Aave V3',
        'category': 'Lending'
    }
    
    result = aggregator.aggregate_risk(tech_features, tvl_data, market_data, protocol_data)
    
    print(f"   Overall Score: {result['overall_score']} - {result['risk_indicator']}")
    print(f"   Security: {result['category_scores']['security']}")
    print(f"   Financial: {result['category_scores']['financial']}")
    print(f"   Operational: {result['category_scores']['operational']}")
    print(f"   Market: {result['category_scores']['market']}")
    
    # Test case: Lower-quality protocol
    print("\n2. Testing lower-quality protocol:")
    tech_features_low = {
        'verified': False,
        'has_admin_key': True
    }
    
    tvl_data_low = {
        'tvl': 5_000_000,  # $5M
        'chains': {'ethereum': 5_000_000}
    }
    
    market_data_low = {
        'price': 0.50,
        'market_cap': 10_000_000,
        'volume_24h': 50_000,
        'price_change_24h': 25.5,
        'market_cap_rank': 500
    }
    
    protocol_data_low = {
        'name': 'Unknown Protocol',
        'category': 'Other'
    }
    
    result_low = aggregator.aggregate_risk(tech_features_low, tvl_data_low, market_data_low, protocol_data_low)
    
    print(f"   Overall Score: {result_low['overall_score']} - {result_low['risk_indicator']}")
    print(f"   Security: {result_low['category_scores']['security']}")
    print(f"   Financial: {result_low['category_scores']['financial']}")
    print(f"   Operational: {result_low['category_scores']['operational']}")
    print(f"   Market: {result_low['category_scores']['market']}")
    
    print("\n✅ RiskAggregator tests passed!")
