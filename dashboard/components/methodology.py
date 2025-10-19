"""
Methodology Page Component.
Explains the risk scoring methodology and data sources.
"""

import streamlit as st


def render_methodology_page():
    """
    Render methodology explanation page.
    
    Documents:
    - Multi-dimensional scoring formula
    - Weighting for each risk category
    - Data sources used
    - Traffic light threshold values
    """
    st.title("Risk Assessment Methodology")
    
    st.markdown("""
    The Risk Dashboard provides comprehensive risk assessments for DeFi protocols by analyzing 
    multiple dimensions of risk and aggregating data from various trusted sources.
    """)
    
    # Overall scoring formula
    st.header("📊 Overall Risk Score Calculation")
    
    st.markdown("""
    The overall risk score is calculated using a weighted formula that combines four risk categories:
    """)
    
    st.latex(r"""
    \text{Overall Score} = 0.40 \times \text{Security} + 0.30 \times \text{Financial} + 0.20 \times \text{Operational} + 0.10 \times \text{Market}
    """)
    
    st.markdown("""
    **Weighting Rationale:**
    - **Security (40%)**: The most critical factor, as security vulnerabilities can lead to total loss of funds
    - **Financial (30%)**: Financial stability and liquidity are essential for protocol reliability
    - **Operational (20%)**: Good governance and operations reduce long-term risks
    - **Market (10%)**: Market position indicates adoption but is less critical for immediate safety
    """)
    
    # Traffic light indicators
    st.header("🚦 Traffic Light Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🟢 Low Risk
        **Score: 70-100**
        
        Protocols with strong security, 
        stable financials, and good 
        operational practices.
        """)
    
    with col2:
        st.markdown("""
        ### 🟡 Medium Risk
        **Score: 40-69**
        
        Protocols with some concerns 
        in one or more categories. 
        Proceed with caution.
        """)
    
    with col3:
        st.markdown("""
        ### 🔴 High Risk
        **Score: 0-39**
        
        Protocols with significant 
        risks. Exercise extreme 
        caution or avoid.
        """)
    
    # Risk categories
    st.header("📋 Risk Categories")
    
    # Security
    with st.expander("🔒 Security Risk (40% weight)", expanded=True):
        st.markdown("""
        **What we evaluate:**
        - Smart contract verification status
        - Security audit history and quality
        - Presence of admin keys and centralization risks
        - Contract upgradeability and governance controls
        - Historical security incidents
        
        **Scoring criteria:**
        - **High Score (70-100)**: Verified contracts, multiple audits, minimal centralization
        - **Medium Score (40-69)**: Some audits, moderate centralization, time-locked controls
        - **Low Score (0-39)**: Unverified contracts, no audits, significant centralization risks
        """)
    
    # Financial
    with st.expander("💰 Financial Risk (30% weight)", expanded=True):
        st.markdown("""
        **What we evaluate:**
        - Total Value Locked (TVL) and stability
        - Trading volume and liquidity depth
        - Price volatility (24h price changes)
        - Market capitalization
        - Volume-to-market-cap ratio
        
        **Scoring criteria:**
        - **High Score (70-100)**: High TVL (>$1B), stable prices, strong liquidity
        - **Medium Score (40-69)**: Moderate TVL ($100M-$1B), some volatility
        - **Low Score (0-39)**: Low TVL (<$100M), high volatility, thin liquidity
        """)
    
    # Operational
    with st.expander("⚙️ Operational Risk (20% weight)", expanded=True):
        st.markdown("""
        **What we evaluate:**
        - Team transparency and reputation
        - Governance structure and decentralization
        - Documentation quality and completeness
        - Community engagement and activity
        - Protocol maturity and track record
        
        **Scoring criteria:**
        - **High Score (70-100)**: Transparent team, active governance, excellent documentation
        - **Medium Score (40-69)**: Some transparency, developing governance
        - **Low Score (0-39)**: Anonymous team, centralized control, poor documentation
        
        *Note: MVP version uses placeholder scoring for operational risk*
        """)
    
    # Market
    with st.expander("📈 Market Risk (10% weight)", expanded=True):
        st.markdown("""
        **What we evaluate:**
        - Protocol adoption and user base
        - Market position and ranking
        - Competitive landscape
        - Growth trends and momentum
        - Integration with other protocols
        
        **Scoring criteria:**
        - **High Score (70-100)**: Top market position, strong adoption, growing ecosystem
        - **Medium Score (40-69)**: Moderate adoption, competitive position
        - **Low Score (0-39)**: Low adoption, weak market position, declining trends
        """)
    
    # Data sources
    st.header("🔗 Data Sources")
    
    st.markdown("""
    The Risk Dashboard aggregates data from multiple trusted sources to provide comprehensive assessments:
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **On-Chain Data:**
        - **Etherscan API**: Contract verification, source code, transaction history
        - **Ethereum Adapters**: Direct blockchain queries for contract properties
        
        **Market Data:**
        - **CoinGecko API**: Token prices, market cap, trading volume, price changes
        """)
    
    with col2:
        st.markdown("""
        **Protocol Metrics:**
        - **DeFi Llama API**: Total Value Locked (TVL), chain-specific data, protocol rankings
        
        **Security Data:**
        - *Audit data integration planned for future releases*
        """)
    
    # Data freshness
    st.header("⏱️ Data Freshness")
    
    st.markdown("""
    - **API Response Cache**: 5 minutes
    - **Risk Score Cache**: 15 minutes
    - **Automatic Refresh**: Data is automatically refreshed when cache expires
    - **Manual Refresh**: Use the refresh button to force immediate data update
    
    Data age is displayed on each protocol card and detail view to ensure transparency.
    """)
    
    # Error handling
    st.header("⚠️ Error Handling")
    
    st.markdown("""
    The dashboard is designed to handle API failures gracefully:
    
    - **Partial Data**: Risk scores are calculated with available data when some APIs fail
    - **Timeout Protection**: 10-second timeout per API request with automatic retry
    - **Cache Fallback**: Recent cached data is used if fresh data cannot be fetched
    - **Clear Indicators**: Data availability status is clearly displayed for each protocol
    
    When data is unavailable, affected risk categories are marked, and the overall score 
    reflects only the available information.
    """)
    
    # Limitations
    st.header("⚠️ Current Limitations (MVP)")
    
    st.markdown("""
    This is the initial MVP (Minimum Viable Product) release with the following limitations:
    
    - **Audit Data**: Security audit integration is planned but not yet implemented
    - **Operational Scoring**: Uses placeholder logic pending governance data integration
    - **Historical Data**: No historical risk tracking (planned for Phase 2)
    - **Protocol Coverage**: Limited to 5 major Ethereum protocols
    - **Chain Support**: Ethereum only (Hedera integration planned)
    
    Future releases will address these limitations and add additional features.
    """)
    
    # Footer
    st.divider()
    st.caption("Risk Dashboard v1.0 MVP | Data sources: Etherscan, CoinGecko, DeFi Llama")
