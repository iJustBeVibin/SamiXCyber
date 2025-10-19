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
- 🛡️ **Risk Dashboard**: Multi-protocol risk assessment dashboard with comprehensive analytics

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
   # Single protocol analysis
   streamlit run app.py
   
   # Risk Dashboard (multi-protocol)
   streamlit run dashboard_app.py
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
├── app.py                    # Streamlit web interface (single protocol)
├── dashboard_app.py          # Risk Dashboard (multi-protocol)
├── config.py                 # Configuration and safety checks
├── adapters/                 # Chain-specific adapters
│   ├── ethereum.py          # Ethereum/Etherscan integration
│   └── hedera.py            # Hedera Mirror Node integration
├── features/                 # Feature extraction
│   └── tech.py              # Unified technical features
├── engine/                   # Scoring engines
│   ├── tech_baseline.py     # Technical risk algorithm
│   ├── risk_aggregator.py   # Multi-dimensional risk scoring
│   └── combine.py           # Future: combined scoring
├── api_clients/              # External API integrations
│   ├── base.py              # Base API client with caching
│   ├── coingecko.py         # CoinGecko market data
│   └── defillama.py         # DeFi Llama TVL data
├── dashboard/                # Dashboard components
│   ├── protocol_manager.py  # Protocol data management
│   ├── protocols.json       # Protocol configurations
│   └── components/          # UI components
│       ├── protocol_card.py # Protocol summary cards
│       ├── risk_radar.py    # Radar chart visualization
│       ├── detail_view.py   # Protocol detail view
│       └── methodology.py   # Methodology explanation
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

## 🛡️ Risk Dashboard

The Risk Dashboard provides comprehensive risk assessments for multiple DeFi protocols simultaneously, aggregating data from various sources to calculate multi-dimensional risk scores.

### Features

- **Multi-Protocol Analysis**: View risk assessments for 5 major Ethereum DeFi protocols
- **Multi-Dimensional Scoring**: Security (40%), Financial (30%), Operational (20%), Market (10%)
- **Interactive Visualizations**: Radar charts showing risk breakdown across categories
- **Real-Time Data**: Aggregates data from Etherscan, CoinGecko, and DeFi Llama
- **Traffic Light Indicators**: Quick visual risk assessment (🟢 Low, 🟡 Medium, 🔴 High)
- **Detailed Explanations**: Plain language reasons for each risk score
- **Data Freshness**: Displays data age and cache status for transparency

### Running the Dashboard

```bash
streamlit run dashboard_app.py
```

### Supported Protocols (MVP)

1. **Aave V3** - Lending protocol
2. **Uniswap V3** - Decentralized exchange
3. **Compound V3** - Lending protocol
4. **MakerDAO** - Stablecoin protocol
5. **Curve Finance** - Stableswap DEX

### Configuration

Protocol configurations are stored in `dashboard/protocols.json`. Each protocol requires:

```json
{
  "protocol_id": "aave-v3",
  "name": "Aave V3",
  "chain": "ethereum",
  "network": "mainnet",
  "contract_address": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
  "category": "lending",
  "coingecko_id": "aave",
  "defillama_slug": "aave-v3"
}
```

### Environment Variables

```bash
# Optional: CoinGecko API key for higher rate limits
COINGECKO_API_KEY=your_key_here

# API base URLs (defaults provided)
COINGECKO_BASE_URL=https://api.coingecko.com/api/v3
DEFILLAMA_BASE_URL=https://api.llama.fi

# Cache settings
CACHE_TTL_SECONDS=300              # 5 minutes
DASHBOARD_REFRESH_INTERVAL=900     # 15 minutes
```

### Methodology

The dashboard uses a weighted scoring formula:

```
Overall Score = 0.40 × Security + 0.30 × Financial + 0.20 × Operational + 0.10 × Market
```

**Risk Levels:**
- 🟢 **Low Risk (70-100)**: Strong security, stable financials, good operations
- 🟡 **Medium Risk (40-69)**: Some concerns, proceed with caution
- 🔴 **High Risk (0-39)**: Significant risks, exercise extreme caution

For detailed methodology, see the "Methodology" page in the dashboard.

## 📋 Recent Updates

- ✅ Added Risk Dashboard with multi-protocol analysis
- ✅ Implemented multi-dimensional risk scoring engine
- ✅ Integrated CoinGecko and DeFi Llama APIs
- ✅ Created interactive radar chart visualizations
- ✅ Added comprehensive error handling and caching
- ✅ Migrated to Etherscan API V2
- ✅ Fixed proxy contract detection
- ✅ Improved error handling for 404s
- ✅ Added comprehensive test suite
- ✅ Created automated test runner
- ✅ Saved test results for CI/CD

## 🔮 Roadmap

### Phase 1 (Completed - MVP)
- ✅ Multi-protocol risk dashboard
- ✅ Multi-dimensional risk scoring
- ✅ Market data integration (CoinGecko, DeFi Llama)
- ✅ Interactive visualizations

### Phase 2 (Planned)
- [ ] Historical risk tracking and trends
- [ ] Alert system for risk changes
- [ ] Portfolio view (aggregate risk across protocols)
- [ ] Security audit data integration
- [ ] Hedera protocol support
- [ ] Custom risk thresholds

### Phase 3 (Future)
- [ ] AI/ML model integration
- [ ] Comparative protocol analysis
- [ ] API endpoint for programmatic access
- [ ] Support for more chains (Polygon, BSC, etc.)
- [ ] Export functionality (PDF/CSV reports)

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