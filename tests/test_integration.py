"""
Integration tests for the complete scoring pipeline.
Run with: pytest tests/test_integration.py -v
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adapters import ethereum, hedera
from features.tech import build_tech_features
from engine.tech_baseline import tech_baseline


class TestIntegrationPipeline:
    """Test the complete analysis pipeline."""
    
    def test_ethereum_full_pipeline(self):
        """Test complete Ethereum analysis pipeline."""
        # Fetch facts
        address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH
        facts = ethereum.get_tech_facts(address, "mainnet")
        
        # Build features
        features = build_tech_features(facts, "ethereum", "mainnet")
        
        # Calculate score
        score, reasons = tech_baseline(features)
        
        # Validate results
        assert isinstance(score, int)
        assert 10 <= score <= 95, "Score should be between 10 and 95"
        assert isinstance(reasons, list)
        assert len(reasons) > 0, "Should have at least one reason"
        assert len(reasons) <= 3, "Should have at most 3 reasons"
        
    def test_hedera_full_pipeline(self):
        """Test complete Hedera analysis pipeline."""
        # Fetch facts
        token_id = "0.0.107594"
        facts = hedera.get_tech_facts(token_id, "mainnet")
        
        # Build features
        features = build_tech_features(facts, "hedera", "mainnet")
        
        # Calculate score
        score, reasons = tech_baseline(features)
        
        # Validate results
        assert isinstance(score, int)
        assert 10 <= score <= 95, "Score should be between 10 and 95"
        assert isinstance(reasons, list)
        assert len(reasons) > 0, "Should have at least one reason"
        
    def test_feature_schema_compliance(self):
        """Test that features comply with frozen schema."""
        from features.tech import TECH_FEATURE_SCHEMA, validate_tech_features
        
        # Test Ethereum
        eth_facts = ethereum.get_tech_facts("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "mainnet")
        eth_features = build_tech_features(eth_facts, "ethereum", "mainnet")
        assert validate_tech_features(eth_features), "Ethereum features should be valid"
        
        # Test Hedera
        hed_facts = hedera.get_tech_facts("0.0.107594", "mainnet")
        hed_features = build_tech_features(hed_facts, "hedera", "mainnet")
        assert validate_tech_features(hed_features), "Hedera features should be valid"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
