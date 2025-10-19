"""
Risk Dashboard Application.
Main Streamlit application for the DeFi Protocol Risk Dashboard.
"""

import streamlit as st
import logging
from dashboard.protocol_manager import ProtocolManager
from dashboard.components import (
    render_protocol_card,
    render_protocol_detail,
    render_methodology_page
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="DeFi Risk Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'list'

if 'selected_protocol' not in st.session_state:
    st.session_state.selected_protocol = None

if 'protocol_manager' not in st.session_state:
    try:
        st.session_state.protocol_manager = ProtocolManager()
        logger.info("ProtocolManager initialized successfully")
    except Exception as e:
        st.error(f"Failed to initialize Protocol Manager: {e}")
        logger.error(f"Failed to initialize Protocol Manager: {e}")
        st.stop()

# Sidebar navigation
with st.sidebar:
    st.title("🛡️ Risk Dashboard")
    st.markdown("---")
    
    # Navigation buttons
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_view = 'list'
        st.rerun()
    
    if st.button("📖 Methodology", use_container_width=True):
        st.session_state.current_view = 'methodology'
        st.rerun()
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh All Data", use_container_width=True):
        # Clear cache by forcing refresh
        st.cache_data.clear()
        st.success("Data refreshed!")
        st.rerun()
    
    st.markdown("---")
    
    # App info
    st.caption("**Version:** 1.0 MVP")
    st.caption("**Protocols:** 5 Ethereum DeFi")
    st.caption("**Data Sources:** Etherscan, CoinGecko, DeFi Llama")


# Main content area
def render_protocol_list():
    """Render the protocol list view."""
    st.title("DeFi Protocol Risk Dashboard")
    st.markdown("Comprehensive risk assessments for major DeFi protocols")
    
    # Fetch all protocol data
    with st.spinner("Loading protocol data..."):
        try:
            protocols_data = st.session_state.protocol_manager.get_all_protocols()
            logger.info(f"Loaded {len(protocols_data)} protocols")
        except Exception as e:
            st.error(f"Failed to load protocol data: {e}")
            logger.error(f"Failed to load protocol data: {e}")
            return
    
    if not protocols_data:
        st.warning("No protocols configured. Please check your configuration.")
        return
    
    # Display protocols in a grid layout (3 columns)
    st.markdown("---")
    
    # Create rows of 3 columns each
    num_protocols = len(protocols_data)
    num_cols = 3
    
    for i in range(0, num_protocols, num_cols):
        cols = st.columns(num_cols)
        
        for j in range(num_cols):
            idx = i + j
            if idx < num_protocols:
                with cols[j]:
                    render_protocol_card(
                        protocols_data[idx],
                        key_prefix=f"list_{idx}_"
                    )


def render_detail_view():
    """Render the protocol detail view."""
    protocol_id = st.session_state.selected_protocol
    
    if not protocol_id:
        st.error("No protocol selected")
        return
    
    # Fetch protocol data
    with st.spinner("Loading protocol details..."):
        try:
            protocol_data = st.session_state.protocol_manager.get_protocol_risk_data(protocol_id)
            logger.info(f"Loaded details for {protocol_id}")
        except Exception as e:
            st.error(f"Failed to load protocol details: {e}")
            logger.error(f"Failed to load protocol details: {e}")
            return
    
    # Render detail view
    render_protocol_detail(protocol_data)


# Route to appropriate view
if st.session_state.current_view == 'list':
    render_protocol_list()
elif st.session_state.current_view == 'detail':
    render_detail_view()
elif st.session_state.current_view == 'methodology':
    render_methodology_page()
else:
    st.error(f"Unknown view: {st.session_state.current_view}")
