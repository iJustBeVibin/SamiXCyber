"""
Automated tests for Hedera adapter.
Run with: pytest tests/test_hedera.py -v
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adapters.hedera import get_tech_facts


class TestHederaAdapter:
    """Test suite for Hedera adapter functionality."""
    
    def test_valid_token_mainnet(self):
        """Test valid Hedera mainnet token."""
        token_id = "0.0.107594"
        facts = get_tech_facts(token_id, "mainnet")
        
        # Basic structure checks
        assert "verified" in facts
        assert "governance_flags" in facts
        assert "explorer_url" in facts
        assert "token_info" in facts
        
        # Hedera specific checks
        assert facts["governance_flags"]["admin"] is True, "Token should have admin key"
        assert facts["explorer_url"].startswith("https://hashscan.io/mainnet/")
        assert facts["token_info"]["token_id"] == token_id
        
    def test_governance_flags_structure(self):
        """Test that all governance flags are present."""
        token_id = "0.0.107594"
        facts = get_tech_facts(token_id, "mainnet")
        
        required_flags = ["admin", "supply", "pause", "freeze", "wipe", "kyc", "fee"]
        for flag in required_flags:
            assert flag in facts["governance_flags"], f"Missing governance flag: {flag}"
            
    def test_nonexistent_token(self):
        """Test handling of non-existent token."""
        # Use a very high token ID that likely doesn't exist
        token_id = "0.0.999999999"
        facts = get_tech_facts(token_id, "mainnet")
        
        # Should return error state gracefully
        assert "error" in facts or facts["token_info"]["type"] == "UNKNOWN"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
