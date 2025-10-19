# Risk Dashboard Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Etherscan API key (free from https://etherscan.io/apis)

### Step 1: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Etherscan API key
# Required: ETHERSCAN_API_KEY=your_key_here
# Optional: COINGECKO_API_KEY=your_key_here (for higher rate limits)
```

### Step 3: Launch the Dashboard

```bash
streamlit run dashboard_app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📊 Using the Dashboard

### Main Dashboard View

The main view displays all 5 supported protocols in a grid layout:

1. **Protocol Cards**: Each card shows:
   - Protocol name
   - Overall risk score (0-100)
   - Traffic light indicator (🟢🟡🔴)
   - Top 2 risk factors
   - "View Details" button

2. **Risk Levels**:
   - 🟢 **Green (70-100)**: Low Risk - Strong security and stability
   - 🟡 **Yellow (40-69)**: Medium Risk - Some concerns present
   - 🔴 **Red (0-39)**: High Risk - Significant risks identified

### Protocol Detail View

Click "View Details" on any protocol card to see:

1. **Overall Risk Score**: Large display with traffic light indicator
2. **Risk Radar Chart**: Interactive visualization of all 4 risk categories
3. **Detailed Breakdown**: Expandable sections for each category:
   - Security Risk (40% weight)
   - Financial Risk (30% weight)
   - Operational Risk (20% weight)
   - Market Risk (10% weight)
4. **Protocol Information**: Chain, category, contract address, explorer link
5. **Data Freshness**: Last update time and data source status

### Methodology Page

Click "📖 Methodology" in the sidebar to learn about:
- How risk scores are calculated
- What each risk category measures
- Data sources used
- Traffic light threshold values
- Current limitations

## 🔄 Refreshing Data

- **Automatic**: Data refreshes every 15 minutes
- **Manual**: Click "🔄 Refresh All Data" in the sidebar

## 🛠️ Troubleshooting

### "Failed to initialize Protocol Manager"

**Cause**: Missing or invalid configuration file

**Solution**: Ensure `dashboard/protocols.json` exists and is valid JSON

### "Failed to load protocol data"

**Cause**: API connection issues or rate limiting

**Solutions**:
1. Check your internet connection
2. Verify Etherscan API key is valid
3. Wait a few minutes if rate limited
4. Check the API Issues section in protocol details

### "Data Unavailable" indicators

**Cause**: External API temporarily unavailable

**Impact**: Risk scores calculated with available data only

**Solution**: Wait and refresh - the system will retry automatically

### Slow loading times

**Cause**: First load fetches data from all APIs

**Solutions**:
1. Wait for initial load (30-60 seconds)
2. Subsequent loads use cached data (much faster)
3. Consider adding CoinGecko API key for better rate limits

## 📝 Supported Protocols

The MVP includes 5 major Ethereum DeFi protocols:

1. **Aave V3** - Leading lending protocol
2. **Uniswap V3** - Top decentralized exchange
3. **Compound V3** - Established lending platform
4. **MakerDAO** - Decentralized stablecoin protocol
5. **Curve Finance** - Stableswap DEX

## 🔧 Advanced Configuration

### Adding Custom Protocols

Edit `dashboard/protocols.json` to add new protocols:

```json
{
  "protocol_id": "your-protocol",
  "name": "Your Protocol",
  "chain": "ethereum",
  "network": "mainnet",
  "contract_address": "0x...",
  "category": "lending",
  "coingecko_id": "your-token-id",
  "defillama_slug": "your-protocol-slug"
}
```

### Adjusting Cache Settings

Edit `.env` to change cache behavior:

```bash
# API response cache (default: 5 minutes)
CACHE_TTL_SECONDS=300

# Risk score cache (default: 15 minutes)
DASHBOARD_REFRESH_INTERVAL=900

# API timeout (default: 10 seconds)
API_TIMEOUT=10
```

## 📚 Understanding Risk Scores

### Overall Score Formula

```
Overall = 0.40 × Security + 0.30 × Financial + 0.20 × Operational + 0.10 × Market
```

### Security Risk (40%)
- Contract verification status
- Security audit history
- Admin keys and centralization
- Upgradeability risks

### Financial Risk (30%)
- Total Value Locked (TVL)
- Price volatility
- Trading volume
- Liquidity depth

### Operational Risk (20%)
- Team transparency
- Governance structure
- Documentation quality
- Community engagement

### Market Risk (10%)
- Protocol adoption
- Market position
- Competitive landscape
- Growth trends

## 🆘 Getting Help

### Check Logs

The dashboard logs important events. Look for:
- API connection issues
- Rate limiting warnings
- Data fetch failures

### Common Issues

1. **Rate Limiting**: CoinGecko free tier has strict limits
   - Solution: Add API key or wait between refreshes

2. **Timeout Errors**: Network or API slowness
   - Solution: Increase API_TIMEOUT in .env

3. **Missing Data**: Some APIs may be temporarily down
   - Solution: Dashboard continues with available data

### Report Issues

If you encounter problems:
1. Check the console for error messages
2. Review the API Issues section in protocol details
3. Verify your configuration in .env
4. Check that all dependencies are installed

## 🎯 Next Steps

1. **Explore Protocols**: Click through each protocol to see detailed risk assessments
2. **Compare Risks**: Use the radar charts to compare risk profiles
3. **Read Methodology**: Understand how scores are calculated
4. **Monitor Changes**: Refresh periodically to track risk changes

## 📖 Additional Resources

- **README.md**: Full project documentation
- **DASHBOARD_IMPLEMENTATION.md**: Technical implementation details
- **.kiro/specs/risk-dashboard/**: Complete specifications and design docs

---

**Need more help?** Check the main README.md or review the methodology page in the dashboard.
