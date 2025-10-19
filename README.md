# 🔐 Multi-Chain Technical Risk Scoring System

A production-ready system for evaluating the technical risk of smart contracts and tokens across **Ethereum** and **Hedera** networks. Analyzes verification status, governance permissions, and upgradeability to provide transparent risk scores.

## ✨ Features

- 🔷 **Ethereum Support**: Mainnet contract analysis with Etherscan API V2
- 🔶 **Hedera Support**: Mainnet/testnet token analysis via Mirror Node
- 🔍 **Proxy Detection**: Identifies upgradeable contracts (EIP-1967, etc.)
- 🔐 **Governance Analysis**: Detects admin, pause, freeze, wipe, and other control keys
- 📊 **Transparent Scoring**: Rule-based algorithm (10-95 scale) with explanations
- 🧪 **Comprehensive Tests**: Automated test suite with pytest
- 🎨 **Interactive UI**: Streamlit web interface for easy analysis
- 📄 **JSON Receipts**: Exportable analysis reports for auditing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or pip3
- (Optional) Etherscan API key for Ethereum analysis

### Installation

1. **Clone and setup**:
   ```bash
   git clone https://github.com/yourusername/tech-risk-scorer.git
   cd tech-risk-scorer
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Etherscan API key (optional but recommended)
   ```

3. **Test configuration**:
   ```bash
   python3 config.py
   ```

4. **Run automated tests**:
   ```bash
   ./run_tests.sh
   ```

5. **Launch the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

## 🏗️ Architecture

```
[Streamlit UI]
     ↓
[app.py Orchestrator]
     ↓
 ┌──────────────┐
 │ Adapters     │
 │ hedera.py    │   → Hedera Mirror + HashScan
 │ ethereum.py  │   → Etherscan + Sourcify
 └──────────────┘
     ↓
[features.tech]     → Unified feature schema (chain-agnostic)
     ↓
[engine.tech_baseline]  → Scoring algorithm (same for both chains)
     ↓
[utils.io]          → JSON receipt generation
     ↓
[Streamlit UI]      → Display results + download
```

## 🧪 Testing

### Automated Tests
```bash
# Run all tests
./run_tests.sh

# Run specific test suites
pytest tests/test_ethereum.py -v
pytest tests/test_hedera.py -v
pytest tests/test_integration.py -v
```

### Manual Testing Examples

**Ethereum Mainnet:**
- WETH: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
- USDC (Proxy): `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`

**Hedera Mainnet:**
- Token: `0.0.107594`

## 📊 Scoring Algorithm

The technical risk score (10-95, higher = safer) is calculated as:

1. **Unverified contracts**: Score = 40
2. **Verified contracts**: Start with 85, subtract 8 points per risky key:
   - Admin key (-8)
   - Supply key (-8) 
   - Pause key (-8)
   - Freeze key (-8)
   - Wipe key (-8)
   - KYC key (-8)
   - Fee key (-8)
   - Upgradeable + Admin (-8 additional)
3. **Final score**: Clamped between 10-95

### Risk Categories
- **80-95**: Low Risk (verified, minimal permissions)
- **60-79**: Medium Risk (some control keys present)
- **40-59**: High Risk (multiple risky permissions)
- **10-39**: Very High Risk (unverified or extensive control)

## 🔒 Safety Features

- **Read-only**: No transaction capabilities
- **Testnet default**: Safe testing environment
- **Error handling**: Graceful failures with detailed messages
- **Rate limiting**: Built-in delays and retries
- **API V2**: Updated to latest Etherscan API

## 📁 Project Structure

```
├── app.py                    # Streamlit web interface
├── config.py                 # Configuration and safety checks
├── adapters/                 # Chain-specific adapters
│   ├── ethereum.py          # Ethereum/Etherscan integration
│   └── hedera.py            # Hedera Mirror Node integration
├── features/                 # Feature extraction
│   └── tech.py              # Unified technical features
├── engine/                   # Scoring engines
│   ├── tech_baseline.py     # Technical risk algorithm
│   └── combine.py           # Future: combined scoring
├── utils/                    # Utilities
│   └── io.py                # JSON receipt generation
├── tests/                    # Automated test suite
│   ├── test_ethereum.py     # Ethereum adapter tests
│   ├── test_hedera.py       # Hedera adapter tests
│   └── test_integration.py  # End-to-end tests
├── runs/                     # Analysis results & logs
└── run_tests.sh             # Automated test runner
```

## 🛠️ Development

### Running tests:
```bash
# All tests
./run_tests.sh

# Specific tests
pytest tests/test_ethereum.py -v
pytest tests/test_hedera.py -v
```

### Code formatting:
```bash
black .
flake8 .
```

### Adding a new chain:
1. Create adapter in `adapters/new_chain.py`
2. Implement `get_tech_facts()` returning unified format
3. Add tests in `tests/test_new_chain.py`
4. Update `app.py` to include new chain option

## 📋 Recent Updates

- ✅ Migrated to Etherscan API V2
- ✅ Fixed proxy contract detection
- ✅ Improved error handling for 404s
- ✅ Added comprehensive test suite
- ✅ Created automated test runner
- ✅ Saved test results for CI/CD

## 🔮 Roadmap

- [ ] Market risk scoring integration
- [ ] AI/ML model integration
- [ ] Combined risk scoring (tech + market)
- [ ] Enhanced dashboard with charts
- [ ] API endpoint for programmatic access
- [ ] Support for more chains (Polygon, BSC, etc.)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check `FIXES_SUMMARY.md` for recent fixes
- Review test logs in `runs/` directory