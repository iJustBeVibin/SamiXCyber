"""
Configuration module for Multi-Chain Technical Risk Scoring System.
Handles environment variables and network settings with safety enforcements.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global settings
ALLOW_TX = os.getenv("ALLOW_TX", "false").lower() == "true"
ACTIVE_CHAIN = os.getenv("ACTIVE_CHAIN", "hedera").lower()
ACTIVE_NETWORK = os.getenv("ACTIVE_NETWORK", "testnet").lower()

# Hedera configuration
HEDERA_MIRROR_TESTNET = os.getenv("HEDERA_MIRROR_TESTNET", "https://testnet.mirrornode.hedera.com/api/v1")
HEDERA_MIRROR_MAINNET = os.getenv("HEDERA_MIRROR_MAINNET", "https://mainnet-public.mirrornode.hedera.com/api/v1")
HASHSCAN_TESTNET = os.getenv("HASHSCAN_TESTNET", "https://hashscan.io/testnet")
HASHSCAN_MAINNET = os.getenv("HASHSCAN_MAINNET", "https://hashscan.io/mainnet")

# Ethereum configuration
# ETHERSCAN_API_KEY is required for Ethereum support.
# For testing purposes, a placeholder is used if not provided.
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YOUR_PLACEHOLDER_API_KEY")
# Use Etherscan API V2 endpoint
ETHERSCAN_BASE = os.getenv("ETHERSCAN_BASE", "https://api.etherscan.io/v2/api")
SOURCIFY_API = os.getenv("SOURCIFY_API", "https://sourcify.dev/server")
ETHERSCAN_EXPLORER = os.getenv("ETHERSCAN_EXPLORER", "https://etherscan.io")

# API settings
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
API_RETRIES = int(os.getenv("API_RETRIES", "2"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.1"))

# Dashboard API configuration
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "")  # Optional, for higher rate limits
COINGECKO_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
DEFILLAMA_BASE_URL = os.getenv("DEFILLAMA_BASE_URL", "https://api.llama.fi")

# Cache settings
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes
DASHBOARD_REFRESH_INTERVAL = int(os.getenv("DASHBOARD_REFRESH_INTERVAL", "900"))  # 15 minutes

# Version info
PROTOTYPE_VERSION = "0.3-multichain-tech"


def assert_read_only():
    """
    Safety check to enforce read-only operations.
    Must be called by any code that could potentially send transactions.
    """
    if ALLOW_TX:
        raise RuntimeError(
            "TX disabled: read-only mode enforced. ALLOW_TX must be false."
        )


def get_chain_config(chain: str = None, network: str = None) -> dict:
    """
    Get configuration for specific chain and network.
    
    Args:
        chain: 'hedera' or 'ethereum' (defaults to ACTIVE_CHAIN)
        network: 'testnet' or 'mainnet' (defaults to ACTIVE_NETWORK)
        
    Returns:
        Dictionary with chain-specific configuration
    """
    chain = chain or ACTIVE_CHAIN
    network = network or ACTIVE_NETWORK
    
    if chain == "hedera":
        if network == "testnet":
            return {
                "mirror_api": HEDERA_MIRROR_TESTNET,
                "explorer_base": HASHSCAN_TESTNET,
                "explorer_name": "HashScan"
            }
        elif network == "mainnet":
            return {
                "mirror_api": HEDERA_MIRROR_MAINNET,
                "explorer_base": HASHSCAN_MAINNET,
                "explorer_name": "HashScan"
            }
    elif chain == "ethereum":
        return {
            "etherscan_api": ETHERSCAN_BASE,
            "etherscan_key": ETHERSCAN_API_KEY,
            "sourcify_api": SOURCIFY_API,
            "explorer_base": ETHERSCAN_EXPLORER,
            "explorer_name": "Etherscan"
        }
    
    raise ValueError(f"Unsupported chain/network combination: {chain}/{network}")


def get_mirror_endpoint(path: str, network: str = None) -> str:
    """Construct Hedera Mirror Node API endpoint."""
    config = get_chain_config("hedera", network)
    return f"{config['mirror_api'].rstrip('/')}/{path.lstrip('/')}"


def get_explorer_url(chain: str, entity_type: str, entity_id: str, network: str = None) -> str:
    """
    Construct explorer URL for any supported chain.
    
    Args:
        chain: 'hedera' or 'ethereum'
        entity_type: 'token', 'contract', 'address'
        entity_id: Entity ID or address
        network: Network (optional, uses active network)
    """
    config = get_chain_config(chain, network)
    
    if chain == "hedera":
        return f"{config['explorer_base']}/{entity_type}/{entity_id}"
    elif chain == "ethereum":
        return f"{config['explorer_base']}/address/{entity_id}"
    
    raise ValueError(f"Unsupported chain: {chain}")


def validate_config():
    """Validate configuration for active chain/network."""
    import requests
    
    # Enforce read-only mode
    assert_read_only()
    
    # Validate chain/network combination
    supported_combinations = [
        ("hedera", "testnet"),
        ("hedera", "mainnet"),
        ("ethereum", "mainnet")
    ]
    
    if (ACTIVE_CHAIN, ACTIVE_NETWORK) not in supported_combinations:
        raise ValueError(f"Unsupported chain/network: {ACTIVE_CHAIN}/{ACTIVE_NETWORK}")
    
    # Test connectivity based on active chain
    if ACTIVE_CHAIN == "hedera":
        try:
            test_url = get_mirror_endpoint("network/exchangerate")
            response = requests.get(test_url, timeout=API_TIMEOUT)
            response.raise_for_status()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Hedera Mirror Node: {e}")
    
    elif ACTIVE_CHAIN == "ethereum":
        if not ETHERSCAN_API_KEY:
            raise ValueError("ETHERSCAN_API_KEY is required for Ethereum support")
        
        try:
            # Test Etherscan API
            config = get_chain_config("ethereum")
            test_url = f"{config['etherscan_api']}?module=stats&action=ethsupply&apikey={config['etherscan_key']}"
            response = requests.get(test_url, timeout=API_TIMEOUT)
            response.raise_for_status()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Etherscan API: {e}")
    
    return True


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    logging.info(f"Active Chain: {ACTIVE_CHAIN}")
    logging.info(f"Active Network: {ACTIVE_NETWORK}")
    logging.info(f"Read-only Mode: {not ALLOW_TX}")
    
    if ETHERSCAN_API_KEY:
        logging.info(f"Etherscan API Key: {ETHERSCAN_API_KEY[:4]}... (length: {len(ETHERSCAN_API_KEY)})")
    else:
        logging.warning("Etherscan API Key is NOT set.")

    try:
        validate_config()
        logging.info("✅ Configuration valid and services accessible")
    except Exception as e:
        logging.error(f"❌ Configuration error: {e}")
