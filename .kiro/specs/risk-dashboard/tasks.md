# Implementation Plan

- [x] 1. Set up project structure and protocol configuration
  - Create `dashboard/` directory with `__init__.py` for dashboard-specific modules
  - Create `dashboard/components/` subdirectory with `__init__.py` for UI components
  - Create `api_clients/` directory with `__init__.py` for external API integrations
  - Create `dashboard/protocols.json` configuration file with 5 MVP protocols (Aave V3, Uniswap V3, Compound V3, MakerDAO, Curve)
  - Add new environment variables to `.env.example` for API keys and cache settings
  - _Requirements: 1.1, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 2. Implement base API client infrastructure
  - [x] 2.1 Create `api_clients/base.py` with BaseAPIClient class
    - Implement GET request method with timeout handling (10 seconds)
    - Implement in-memory caching with 5-minute TTL using dictionary with timestamps
    - Implement retry logic with exponential backoff (2 retries)
    - Add error logging for failed requests
    - _Requirements: 4.5, 8.1, 8.3, 8.4, 10.4_

  - [x] 2.2 Create `api_clients/coingecko.py` for market data
    - Implement CoinGeckoClient extending BaseAPIClient
    - Implement `get_token_data()` method to fetch price, market cap, volume, and price change
    - Handle API rate limiting and errors gracefully
    - _Requirements: 4.2_

  - [x] 2.3 Create `api_clients/defillama.py` for TVL data
    - Implement DefiLlamaClient extending BaseAPIClient
    - Implement `get_protocol_tvl()` method to fetch TVL and chain-specific data
    - Handle missing protocol data gracefully
    - _Requirements: 4.3_

- [x] 3. Implement multi-dimensional risk scoring engine
  - [x] 3.1 Create `engine/risk_aggregator.py` with RiskAggregator class
    - Define class structure with methods for each risk category
    - Implement score normalization to 0-100 range
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 3.2 Implement security risk scoring
    - Integrate existing `tech_baseline()` function for contract verification scoring
    - Add audit status evaluation (placeholder for MVP - return neutral score)
    - Calculate security score with plain language reasons
    - _Requirements: 1.1, 1.3, 3.1, 3.3, 3.4, 3.5_

  - [x] 3.3 Implement financial risk scoring
    - Calculate score based on TVL size (higher TVL = lower risk)
    - Evaluate price volatility from 24h price change
    - Evaluate trading volume relative to market cap
    - Generate plain language explanations for financial risks
    - _Requirements: 1.1, 1.4, 3.1, 3.3, 3.4, 3.5_

  - [x] 3.4 Implement operational risk scoring
    - Create basic scoring based on protocol maturity (placeholder for MVP - return neutral score)
    - Add governance structure evaluation (placeholder for MVP - return neutral score)
    - Generate plain language explanations for operational risks
    - _Requirements: 1.1, 1.5, 3.1, 3.3, 3.4, 3.5_

  - [x] 3.5 Implement market risk scoring
    - Calculate score based on market position and adoption metrics
    - Evaluate competitive landscape (placeholder for MVP - return neutral score)
    - Generate plain language explanations for market risks
    - _Requirements: 1.1, 1.6, 3.1, 3.3, 3.4, 3.5_

  - [x] 3.6 Implement overall risk score calculation
    - Apply weighted formula: Security (40%) + Financial (30%) + Operational (20%) + Market (10%)
    - Determine traffic light indicator based on overall score (Green: 70+, Yellow: 40-69, Red: <40)
    - Aggregate reasons from all categories (max 3 per category)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4_

- [ ] 4. Implement protocol data management
  - [x] 4.1 Create `dashboard/protocol_manager.py` with ProtocolManager class
    - Implement protocol configuration loading from JSON file
    - Initialize all API clients (CoinGecko, DeFi Llama)
    - Initialize RiskAggregator
    - Implement error handling for missing configuration
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 4.2 Implement protocol data aggregation
    - Create `get_protocol_risk_data()` method to fetch and combine data from all sources
    - Integrate with existing Ethereum adapter for on-chain data
    - Integrate with CoinGecko client for market data
    - Integrate with DeFi Llama client for TVL data
    - Call RiskAggregator to calculate all risk scores
    - Handle partial data availability when APIs fail
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.1, 8.2, 8.5_

  - [x] 4.3 Implement data caching and refresh logic
    - Add timestamp tracking for last data update in protocol data dictionary
    - Implement 15-minute refresh interval for protocol data
    - Create `refresh_protocol_data()` method to force cache bypass
    - Implement helper function to display data age in human-readable format
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 4.4 Implement batch protocol data fetching
    - Create `get_all_protocols()` method to fetch data for all configured protocols
    - Implement sequential API requests (parallel can be added later)
    - Handle individual protocol failures without blocking others
    - _Requirements: 5.5, 8.1, 8.5_

- [ ] 5. Create dashboard UI components
  - [x] 5.1 Create `dashboard/components/protocol_card.py`
    - Implement `render_protocol_card()` function
    - Display protocol name and overall risk score
    - Show traffic light indicator using colored emoji (🟢🟡🔴)
    - Display top 2 risk factors
    - Use Streamlit button for navigation to detail view
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1_

  - [x] 5.2 Create `dashboard/components/risk_radar.py`
    - Implement `render_risk_radar_chart()` function using plotly
    - Create radar chart with four axes (Security, Financial, Operational, Market)
    - Color-code risk levels on the chart
    - Add hover tooltips with score details
    - _Requirements: 3.2, 3.3_

  - [x] 5.3 Create `dashboard/components/detail_view.py`
    - Implement `render_protocol_detail()` function
    - Display protocol name in header with back navigation button
    - Show overall risk score with traffic light indicator
    - Render risk radar chart
    - Display detailed breakdown for each risk category with scores and reasons
    - Show data freshness timestamp
    - Add link to protocol explorer
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.5, 10.2, 10.3_

  - [x] 5.4 Create `dashboard/components/methodology.py`
    - Implement `render_methodology_page()` function
    - Document the multi-dimensional scoring formula
    - Explain weighting for each risk category
    - List all data sources used
    - Describe traffic light threshold values
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 6. Implement main dashboard application
  - [x] 6.1 Create `dashboard_app.py` as new Streamlit application
    - Set up page configuration with title and icon
    - Initialize ProtocolManager
    - Implement session state for navigation (current_view, selected_protocol)
    - _Requirements: 5.5, 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.2 Implement protocol list view
    - Display all protocols in a grid layout using Streamlit columns
    - Render protocol cards for each protocol
    - Handle loading states while fetching data using st.spinner
    - Display error messages for protocols with unavailable data
    - Add refresh button to force data update
    - _Requirements: 2.5, 5.5, 8.2, 10.1_

  - [x] 6.3 Implement protocol detail view navigation
    - Handle protocol card button clicks to navigate to detail view
    - Store selected protocol in session state
    - Implement back button to return to list view
    - Update session state to switch between views
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 6.4 Implement responsive layout
    - Use Streamlit columns for desktop layout (3 columns for protocol cards)
    - Use st.columns with responsive column counts
    - Ensure all UI elements are readable on different screen sizes
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 6.5 Add navigation menu
    - Create sidebar with navigation options
    - Add "Dashboard" button to protocol list view
    - Add "Methodology" button to methodology page
    - Display app version and last global refresh time
    - _Requirements: 9.1_

- [ ] 7. Implement error handling and data availability indicators
  - [x] 7.1 Add API failure handling in UI
    - Display "Data Unavailable" badges for missing risk categories
    - Show warning messages when APIs fail using st.warning
    - Indicate which data sources are unavailable
    - Allow partial risk calculation with available data only
    - _Requirements: 8.1, 8.2, 8.5_

  - [x] 7.2 Implement timeout and retry feedback
    - Log API timeouts with timestamps in BaseAPIClient
    - Display user-friendly error messages for timeouts
    - _Requirements: 8.3, 8.4_

  - [x] 7.3 Add data freshness indicators
    - Display "Last updated: X minutes ago" for each protocol
    - Highlight stale data (older than 30 minutes) with warning color
    - Show cache status (fresh/cached/unavailable)
    - _Requirements: 10.2, 10.3_

- [ ] 8. Configuration and deployment setup
  - [x] 8.1 Update configuration files
    - Add CoinGecko API configuration to `config.py`
    - Add DeFi Llama API configuration to `config.py`
    - Add cache TTL settings to `config.py`
    - Update `.env.example` with new environment variables
    - _Requirements: 4.2, 4.3, 10.4_

  - [x] 8.2 Create protocol configuration file
    - Create `dashboard/protocols.json` with 5 MVP protocols
    - Include contract addresses, API mappings (coingecko_id, defillama_slug), and metadata
    - Validate JSON structure
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 8.3 Update dependencies
    - Add plotly to requirements.txt for radar charts
    - Update requirements.txt with any other new dependencies
    - _Requirements: 3.2_

  - [x] 8.4 Update README documentation
    - Add section for Risk Dashboard feature
    - Document how to run the dashboard application
    - List required environment variables
    - Provide example protocol configuration
    - _Requirements: 9.1, 9.2, 9.3_

- [ ]* 9. Testing and validation
  - [ ]* 9.1 Create unit tests for API clients
    - Write tests for BaseAPIClient caching logic
    - Write tests for CoinGeckoClient data fetching
    - Write tests for DefiLlamaClient data fetching
    - Mock external API responses
    - Test retry and timeout behavior
    - _Requirements: 4.2, 4.3, 4.5, 8.3, 8.4_

  - [ ]* 9.2 Create unit tests for risk aggregator
    - Test security score calculation with various inputs
    - Test financial score calculation with various inputs
    - Test operational score calculation with various inputs
    - Test market score calculation with various inputs
    - Test overall score weighting formula
    - Test traffic light indicator logic
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.2, 2.3, 2.4_

  - [ ]* 9.3 Create integration tests for protocol manager
    - Test end-to-end data flow from APIs to risk scores
    - Test cache behavior and refresh logic
    - Test handling of API failures
    - Test batch protocol data fetching
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.1, 8.5, 10.1, 10.4, 10.5_
