# 🔐 Hedera Technical Risk Scoring System

A prototype system for evaluating the technical risk of Hedera tokens and contracts based on key permissions, verification status, and other technical factors.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd tech
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for testnet)
   ```

3. **Test configuration**:
   ```bash
   python3 config.py
   ```

4. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

## 🏗️ Architecture

```
[Streamlit UI] → [app.py] → [Fetchers] → [Features] → [Engine] → [Results]
                               ↓           ↓          ↓
                          mirror.py    tech.py   tech_baseline.py
                          hashscan.py                ↓
                                                utils/io.py
```

## 🧪 Testing

Test with example testnet tokens:
- Token ID format: `0.0.12345`
- Contract address format: `0x...` (EVM address)

## 📊 Scoring Algorithm

The technical risk score (0-100) is calculated as:

1. **Unverified contracts**: Score = 40
2. **Verified contracts**: Start with 85, subtract 8 points per risky key:
   - Admin key (-8)
   - Supply key (-8) 
   - Pause key (-8)
   - Freeze key (-8)
   - Wipe key (-8)
   - KYC key (-8)
   - Fee key (-8)
3. **Final score**: Clamped between 10-95

## 🔒 Safety Features

- **Testnet only**: All API calls go to Hedera testnet
- **No transactions**: Read-only operations only
- **Error handling**: Graceful failures with detailed error messages
- **Rate limiting**: Built-in request delays and retries

## 📁 Project Structure

```
├── app.py              # Streamlit UI
├── config.py           # Configuration and safety checks
├── fetch/              # Data fetchers
│   ├── mirror.py       # Hedera Mirror Node API
│   └── hashscan.py     # HashScan verification API
├── features/           # Feature extraction
│   └── tech.py         # Technical features
├── engine/             # Scoring engines
│   ├── tech_baseline.py # Technical risk scoring
│   └── combine.py      # Future: combined scoring
├── utils/              # Utilities
│   └── io.py           # JSON receipt generation
└── runs/               # Saved analysis results
```

## 🛠️ Development

### Running tests:
```bash
pytest
```

### Code formatting:
```bash
black .
flake8 .
```

## 📋 Status

- [x] ✅ Implement fetchers (mirror.py, hashscan.py)
- [x] ✅ Build feature extraction (tech.py)
- [x] ✅ Create scoring engine (tech_baseline.py)
- [x] ✅ Build Streamlit UI (app.py)
- [x] ✅ Add utilities (io.py)
- [x] ✅ Add error handling and JSON receipts

**Status: 🎉 COMPLETE - Ready for testing!**

## 🔮 Future Features

- Market risk scoring integration
- AI/ML model integration
- Combined risk scoring
- Enhanced dashboard UI

## 📄 License

MIT License - see LICENSE file for details.