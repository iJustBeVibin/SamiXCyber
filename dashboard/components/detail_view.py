"""
Protocol Detail View Component.
Renders detailed risk assessment for a single protocol.
"""

import streamlit as st
from typing import Dict, Any
from .risk_radar import render_risk_radar_chart
from dashboard.protocol_manager import ProtocolManager


def render_protocol_detail(protocol_data: Dict[str, Any]):
    """
    Render detailed protocol view with comprehensive risk information.
    
    Displays:
    - Protocol name in header with back navigation button
    - Overall risk score with traffic light indicator
    - Risk radar chart
    - Detailed breakdown for each risk category with scores and reasons
    - Data freshness timestamp
    - Link to protocol explorer
    
    Args:
        protocol_data: Protocol risk data dictionary
    """
    # Header with back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back", key="back_button"):
            st.session_state.current_view = 'list'
            st.rerun()
    
    with col2:
        st.title(protocol_data['name'])
    
    # Overall risk score section
    overall_score = protocol_data['scores']['overall']
    risk_indicator = protocol_data['risk_indicator']
    
    # Determine traffic light emoji and color
    if overall_score >= 70:
        traffic_light = "🟢"
        risk_color = "green"
    elif overall_score >= 40:
        traffic_light = "🟡"
        risk_color = "orange"
    else:
        traffic_light = "🔴"
        risk_color = "red"
    
    # Display overall score prominently
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px; margin: 20px 0;">
            <div style="font-size: 3em;">{traffic_light}</div>
            <div style="font-size: 2.5em; font-weight: bold; color: {risk_color};">
                {overall_score}/100
            </div>
            <div style="font-size: 1.5em; color: {risk_color}; font-weight: bold;">
                {risk_indicator}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Risk radar chart
    st.subheader("Risk Category Breakdown")
    category_scores = {
        'security': protocol_data['scores']['security'],
        'financial': protocol_data['scores']['financial'],
        'operational': protocol_data['scores']['operational'],
        'market': protocol_data['scores']['market']
    }
    
    fig = render_risk_radar_chart(category_scores)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed category breakdowns
    st.subheader("Detailed Risk Analysis")
    
    categories = [
        ('Security', 'security', '🔒'),
        ('Financial', 'financial', '💰'),
        ('Operational', 'operational', '⚙️'),
        ('Market', 'market', '📈')
    ]
    
    for display_name, key, emoji in categories:
        score = protocol_data['scores'][key]
        reasons = protocol_data['reasons'].get(key, [])
        
        # Determine score color
        if score >= 70:
            score_color = "green"
        elif score >= 40:
            score_color = "orange"
        else:
            score_color = "red"
        
        with st.expander(f"{emoji} {display_name} Risk: {score}/100", expanded=True):
            st.markdown(f"**Score:** <span style='color: {score_color}; font-weight: bold; font-size: 1.2em;'>{score}/100</span>", unsafe_allow_html=True)
            
            if reasons:
                st.markdown("**Key Factors:**")
                for reason in reasons:
                    st.markdown(f"• {reason}")
            else:
                st.markdown("*No specific risk factors identified*")
    
    # Protocol information section
    st.subheader("Protocol Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Chain:** {protocol_data['chain'].capitalize()}")
        st.markdown(f"**Category:** {protocol_data.get('category', 'Unknown').capitalize()}")
    
    with col2:
        st.markdown(f"**Contract:** `{protocol_data['contract_address'][:10]}...{protocol_data['contract_address'][-8:]}`")
        
        # Explorer link
        explorer_url = f"https://etherscan.io/address/{protocol_data['contract_address']}"
        st.markdown(f"[View on Etherscan]({explorer_url})")
    
    # Data freshness section
    st.divider()
    
    metadata = protocol_data.get('metadata', {})
    last_updated = metadata.get('last_updated', 0)
    data_sources = metadata.get('data_sources', [])
    data_availability = metadata.get('data_availability', 'unknown')
    api_failures = metadata.get('api_failures', [])
    
    # Display data age
    if last_updated:
        data_age = ProtocolManager.format_data_age(last_updated)
        st.caption(f"📅 Last updated: {data_age}")
    
    # Display data sources
    if data_sources:
        sources_text = ", ".join(data_sources)
        st.caption(f"📊 Data sources: {sources_text}")
    
    # Display data availability status
    if data_availability == 'complete':
        st.success("✅ All data sources available")
    elif data_availability == 'partial':
        st.warning(f"⚠️ Partial data available ({len(data_sources)}/3 sources)")
    elif data_availability == 'unavailable':
        st.error("❌ Data unavailable")
    
    # Display API failures if any
    if api_failures:
        with st.expander("⚠️ API Issues", expanded=False):
            for failure in api_failures:
                st.caption(f"• {failure}")
