# Risk Dashboard Design Document

## Overview

The Risk Dashboard is a web-based application that provides comprehensive risk assessments for DeFi protocols by aggregating data from multiple external APIs. The system builds upon the existing multi-chain technical risk scoring infrastructure, extending it to support multiple protocols simultaneously with enhanced visualization and comparative analysis capabilities.

The dashboard transforms complex on-chain and off-chain data into clear, actionable risk insights through a multi-dimensional scoring system that evaluates Security, Financial, Operational, and Market risk categories.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Protocol List│  │ Detail View  │  │ Methodology  │      │
│  │    View      │  │              │  │     Page     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Risk Aggregation Engine                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Multi-Dimensional Risk Scorer                       │   │
│  │  - Security (40%)  - Financial (30%)                 │   │
│  │  - Operational (20%)  - Market (10%)                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  API Aggregator Layer                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Security │  │Financial │  │On-Chain  │  │Governance│   │
│  │   APIs   │  │   APIs   │  │   APIs   │  │   APIs   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              External Data Sources                           │
│  CoinGecko │ DeFi Llama │ Etherscan │ Existing Adapters     │
└─────────────────────────────────────────────────────────────┘
```

### Integration with Existing System

The Risk Dashboard extends the existing multi-chain technical risk scoring system:

1. **Reuses Existing Components**:
   - `adapters/ethereum.py` - For on-chain data and contract verification
   - `engine/tech_baseline.py` - As foundation for Security risk scoring
   - `features/tech.py` - For technical feature extraction
   - `utils/io.py` - For caching and data persistence

2. **New Components**:
   - `dashboard/` - New module for dashboard-specific functionality
   - `api_clients/` - External API integration layer
   - `engine/risk_aggregator.py` - Multi-dimensional risk scoring
   - `dashboard_app.py` - New Streamlit application for dashboard UI

## Components and Interfaces

### 1. API Client Layer (`api_clients/`)

Handles communication with external APIs, implementing retry logic, caching, and error handling.

#### `api_clients/base.py`
```python
class BaseAPIClient:
    """Base class for all API clients with common functionality."""
    
    def __init__(self, base_url: str, timeout: int = 10, cache_ttl: int = 300):
        self.base_url = base_url
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.cache = {}  # Simple in-memory cache
    
    def get(self, endpoint: str, params: dict = None) -> dict:
        """Make GET request with caching and retry logic."""
        pass
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        pass
```

#### `api_clients/coingecko.py`
```python
class CoinGeckoClient(BaseAPIClient):
    """Client for CoinGecko API - market data and token information."""
    
    def get_token_data(self, contract_address: str) -> dict:
        """
        Fetch token market data.
        Returns: {
            "price_usd": float,
            "market_cap": float,
            "volume_24h": float,
            "price_change_24h": float
        }
        """
        pass
```

#### `api_clients/defillama.py`
```python
class DefiLlamaClient(BaseAPIClient):
    """Client for DeFi Llama API - TVL and protocol metrics."""
    
    def get_protocol_tvl(self, protocol_slug: str) -> dict:
        """
        Fetch protocol TVL data.
        Returns: {
            "tvl": float,
            "tvl_change_24h": float,
            "chain_tvls": dict
        }
        """
        pass
```

### 2. Risk Aggregation Engine (`engine/risk_aggregator.py`)

Implements the multi-dimensional risk scoring algorithm.

```python
class RiskAggregator:
    """
    Multi-dimensional risk scoring engine.
    
    Calculates risk scores across four categories:
    - Security (40% weight): Based on audits, code quality, centralization
    - Financial (30% weight): Based on TVL, volatility, liquidity
    - Operational (20% weight): Based on team, governance, transparency
    - Market (10% weight): Based on adoption, competition, trends
    """
    
    def calculate_security_score(self, tech_features: dict, audit_data: dict) -> tuple:
        """
        Calculate security risk score (0-100).
        
        Factors:
        - Contract verification (from existing tech_baseline)
        - Audit status and scores
        - Admin key presence
        - Upgradeability
        
        Returns: (score, reasons)
        """
        pass
    
    def calculate_financial_score(self, market_data: dict, tvl_data: dict) -> tuple:
        """
        Calculate financial risk score (0-100).
        
        Factors:
        - TVL size and stability
        - Trading volume
        - Price volatility
        - Liquidity depth
        
        Returns: (score, reasons)
        """
        pass
    
    def calculate_operational_score(self, protocol_info: dict) -> tuple:
        """
        Calculate operational risk score (0-100).
        
        Factors:
        - Team transparency
        - Governance structure
        - Documentation quality
        - Community engagement
        
        Returns: (score, reasons)
        """
        pass
    
    def calculate_market_score(self, market_data: dict) -> tuple:
        """
        Calculate market risk score (0-100).
        
        Factors:
        - Protocol adoption
        - Market position
        - Competitive landscape
        - Growth trends
        
        Returns: (score, reasons)
        """
        pass
    
    def calculate_overall_score(self, category_scores: dict) -> tuple:
        """
        Calculate weighted overall risk score.
        
        Args:
            category_scores: {
                "security": (score, reasons),
                "financial": (score, reasons),
                "operational": (score, reasons),
                "market": (score, reasons)
            }
        
        Returns: (overall_score, risk_level, all_reasons)
        """
        pass
```

### 3. Protocol Data Manager (`dashboard/protocol_manager.py`)

Manages protocol configurations and data aggregation.

```python
class ProtocolManager:
    """
    Manages protocol configurations and coordinates data fetching.
    """
    
    def __init__(self):
        self.protocols = self._load_protocol_configs()
        self.api_clients = self._initialize_api_clients()
    
    def get_protocol_risk_data(self, protocol_id: str) -> dict:
        """
        Fetch and aggregate all risk data for a protocol.
        
        Returns: {
            "protocol_id": str,
            "name": str,
            "contract_address": str,
            "chain": str,
            "scores": {
                "overall": int,
                "security": int,
                "financial": int,
                "operational": int,
                "market": int
            },
            "reasons": {
                "security": [str],
                "financial": [str],
                "operational": [str],
                "market": [str]
            },
            "metadata": {
                "last_updated": timestamp,
                "data_sources": [str]
            }
        }
        """
        pass
    
    def get_all_protocols(self) -> list:
        """Get risk data for all configured protocols."""
        pass
    
    def refresh_protocol_data(self, protocol_id: str) -> dict:
        """Force refresh of protocol data, bypassing cache."""
        pass
```

### 4. Dashboard UI Components (`dashboard/`)

Streamlit-based UI components for visualization.

#### `dashboard/components/protocol_card.py`
```python
def render_protocol_card(protocol_data: dict):
    """
    Render a protocol card with summary information.
    
    Displays:
    - Protocol name and logo
    - Overall risk score with traffic light indicator
    - Key risk factors (top 2-3)
    - Quick stats (TVL, audit status)
    """
    pass
```

#### `dashboard/components/risk_radar.py`
```python
def render_risk_radar_chart(category_scores: dict):
    """
    Render radar chart showing risk scores across categories.
    
    Uses plotly to create interactive radar chart with:
    - Four axes (Security, Financial, Operational, Market)
    - Color-coded risk levels
    - Hover tooltips with details
    """
    pass
```

#### `dashboard/components/detail_view.py`
```python
def render_protocol_detail(protocol_data: dict):
    """
    Render detailed protocol view with:
    - Overall risk score and breakdown
    - Risk radar chart
    - Detailed explanations for each category
    - Specific risk factors and recommendations
    - Historical data (if available)
    - Links to external resources
    """
    pass
```

## Data Models

### Protocol Configuration
```python
{
    "protocol_id": "aave-v3",
    "name": "Aave V3",
    "chain": "ethereum",
    "network": "mainnet",
    "contract_address": "0x...",
    "category": "lending",
    "api_mappings": {
        "coingecko_id": "aave",
        "defillama_slug": "aave-v3",
        "etherscan_address": "0x..."
    }
}
```

### Risk Assessment Result
```python
{
    "protocol_id": "aave-v3",
    "timestamp": 1697712000,
    "scores": {
        "overall": 78,
        "security": 85,
        "financial": 82,
        "operational": 75,
        "market": 70
    },
    "risk_level": "Low Risk",  # Green/Yellow/Red
    "reasons": {
        "security": [
            "Verified smart contracts",
            "Multiple security audits",
            "Time-locked admin controls"
        ],
        "financial": [
            "High TVL ($5.2B)",
            "Stable liquidity",
            "Moderate volatility"
        ],
        "operational": [
            "Active governance",
            "Transparent team",
            "Regular updates"
        ],
        "market": [
            "Leading market position",
            "Strong adoption",
            "Competitive pressure"
        ]
    },
    "metadata": {
        "data_sources": ["etherscan", "coingecko", "defillama"],
        "cache_age_seconds": 120,
        "api_failures": []
    }
}
```

## Error Handling

### API Failure Strategy

1. **Graceful Degradation**: Continue with available data when APIs fail
2. **Timeout Handling**: 10-second timeout per API request
3. **Retry Logic**: 2 retries with exponential backoff
4. **Cache Fallback**: Use cached data if fresh fetch fails
5. **User Notification**: Display "Data Unavailable" indicators for missing data

### Error States

```python
class DataAvailability:
    COMPLETE = "complete"          # All data sources available
    PARTIAL = "partial"            # Some data sources failed
    CACHED = "cached"              # Using cached data due to failures
    UNAVAILABLE = "unavailable"    # No data available
```

## Testing Strategy

### Unit Tests

1. **API Client Tests** (`tests/test_api_clients.py`)
   - Mock external API responses
   - Test retry logic and timeout handling
   - Verify cache behavior
   - Test error handling

2. **Risk Aggregator Tests** (`tests/test_risk_aggregator.py`)
   - Test scoring algorithms for each category
   - Verify weighted overall score calculation
   - Test edge cases (missing data, extreme values)
   - Validate score ranges (0-100)

3. **Protocol Manager Tests** (`tests/test_protocol_manager.py`)
   - Test protocol data aggregation
   - Verify cache management
   - Test refresh logic

### Integration Tests

1. **End-to-End Data Flow** (`tests/test_integration_dashboard.py`)
   - Test complete data pipeline from API to UI
   - Verify data transformations
   - Test with real API responses (using VCR.py for recording)

2. **UI Component Tests**
   - Test protocol card rendering
   - Test detail view navigation
   - Test responsive layout

### Manual Testing Checklist

- [ ] Verify all 5 MVP protocols display correctly
- [ ] Test navigation between list and detail views
- [ ] Verify responsive design on mobile/tablet/desktop
- [ ] Test with API failures (disconnect network)
- [ ] Verify cache behavior and data freshness indicators
- [ ] Test methodology page content

## Performance Considerations

### Caching Strategy

1. **API Response Cache**: 5-minute TTL for external API responses
2. **Computed Score Cache**: 15-minute TTL for risk calculations
3. **Protocol List Cache**: 15-minute TTL for dashboard list view

### Optimization Techniques

1. **Parallel API Requests**: Fetch data from multiple APIs concurrently
2. **Lazy Loading**: Load detail view data only when protocol is selected
3. **Batch Processing**: Pre-compute scores for all protocols on startup
4. **Incremental Updates**: Refresh individual protocols without full reload

## Security Considerations

1. **API Key Management**: Store API keys in environment variables
2. **Rate Limiting**: Respect external API rate limits
3. **Input Validation**: Validate all protocol addresses and IDs
4. **Read-Only Operations**: Maintain existing read-only enforcement
5. **No User Data**: Dashboard does not collect or store user information

## Deployment Configuration

### Environment Variables

```bash
# Existing variables (reused)
ETHERSCAN_API_KEY=your_key_here
API_TIMEOUT=10
API_RETRIES=2

# New variables for dashboard
COINGECKO_API_KEY=optional_key_here
DEFILLAMA_API_KEY=not_required
CACHE_TTL_SECONDS=300
DASHBOARD_REFRESH_INTERVAL=900
```

### Protocol Configuration File

Location: `dashboard/protocols.json`

```json
{
  "protocols": [
    {
      "protocol_id": "aave-v3",
      "name": "Aave V3",
      "chain": "ethereum",
      "network": "mainnet",
      "contract_address": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
      "category": "lending",
      "api_mappings": {
        "coingecko_id": "aave",
        "defillama_slug": "aave-v3"
      }
    },
    {
      "protocol_id": "uniswap-v3",
      "name": "Uniswap V3",
      "chain": "ethereum",
      "network": "mainnet",
      "contract_address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
      "category": "dex",
      "api_mappings": {
        "coingecko_id": "uniswap",
        "defillama_slug": "uniswap-v3"
      }
    },
    {
      "protocol_id": "compound-v3",
      "name": "Compound V3",
      "chain": "ethereum",
      "network": "mainnet",
      "contract_address": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
      "category": "lending",
      "api_mappings": {
        "coingecko_id": "compound-governance-token",
        "defillama_slug": "compound-v3"
      }
    }
  ]
}
```

## Future Enhancements

### Phase 2 Features (Post-MVP)

1. **Historical Risk Tracking**: Store and visualize risk score changes over time
2. **Alert System**: Notify users of significant risk changes
3. **Portfolio View**: Aggregate risk across multiple protocols
4. **Custom Thresholds**: Allow users to set personal risk tolerance levels
5. **Hedera Integration**: Extend to Hedera protocols using existing adapter
6. **Comparative Analysis**: Side-by-side protocol comparison
7. **Export Functionality**: Download risk reports as PDF/CSV

### Scalability Considerations

1. **Database Integration**: Move from file-based to database storage
2. **Background Workers**: Separate data fetching from UI rendering
3. **API Gateway**: Centralized API management and rate limiting
4. **CDN Integration**: Cache static assets and protocol logos
5. **Multi-User Support**: Session management and user preferences

## Migration Path

### From Existing System

1. **Phase 1**: Create new dashboard app alongside existing `app.py`
2. **Phase 2**: Share common components (adapters, engine, utils)
3. **Phase 3**: Unified navigation between single-entity and dashboard views
4. **Phase 4**: Deprecate or merge applications based on user feedback

### Backward Compatibility

- Existing `app.py` continues to function independently
- Shared modules maintain existing interfaces
- New features are additive, not breaking changes
- Receipt format remains compatible with existing tools
