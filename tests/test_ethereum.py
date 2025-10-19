"""
Automated tests for Ethereum adapter.
Run with: pytest tests/test_ethereum.py -v
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from adapters.ethereum import get_tech_facts


class TestEthereumAdapter:
    """Test suite for Ethereum adapter functionality."""
    
    def test_weth_verification(self):
        """Test WETH contract verification and properties."""
        weth_addr = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        facts = get_tech_facts(weth_addr, "mainnet")
        
        # Basic structure checks
        assert "verified" in facts
        assert "governance_flags" in facts
        assert "explorer_url" in facts
        
        # WETH specific checks
        assert facts["verified"] is True, "WETH should be verified"
        assert facts["governance_flags"]["upgradeable"] is False, "WETH should not be upgradeable"
        assert facts["explorer_url"].startswith("https://etherscan.io/address/")
        
    def test_usdc_proxy_detection(self):
        """Test USDC proxy contract detection."""
        usdc_addr = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        facts = get_tech_facts(usdc_addr, "mainnet")
        
        # Basic structure checks
        assert "verified" in facts
        assert "governance_flags" in facts
        
        # USDC specific checks
        assert facts["verified"] is True, "USDC should be verified"
        assert facts["governance_flags"]["upgradeable"] is True, "USDC should be detected as upgradeable proxy"
        
    def test_invalid_address_format(self):
        """Test handling of invalid address format."""
        with pytest.raises(ValueError, match="Invalid input"):
            get_tech_facts("invalid_address", "mainnet")
            
    def test_invalid_address_length(self):
        """Test handling of incorrect address length."""
        with pytest.raises(ValueError, match="Invalid input"):
            get_tech_facts("0x123", "mainnet")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
