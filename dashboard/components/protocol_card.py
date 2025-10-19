"""
Protocol Card Component.
Renders a summary card for a protocol with risk score and key information.
"""

import streamlit as st
from typing import Dict, Any


def render_protocol_card(protocol_data: Dict[str, Any], key_prefix: str = ""):
    """
    Render a protocol card with summary information.
    
    Displays:
    - Protocol name
    - Overall risk score with traffic light indicator
    - Top 2 risk factors
    - Navigation button to detail view
    
    Args:
        protocol_data: Protocol risk data dictionary
        key_prefix: Prefix for Streamlit widget keys to ensure uniqueness
    """
    protocol_id = protocol_data['protocol_id']
    name = protocol_data['name']
    overall_score = protocol_data['scores']['overall']
    risk_indicator = protocol_data['risk_indicator']
    
    # Determine traffic light emoji
    if overall_score >= 70:
        traffic_light = "🟢"
        risk_color = "green"
    elif overall_score >= 40:
        traffic_light = "🟡"
        risk_color = "orange"
    else:
        traffic_light = "🔴"
        risk_color = "red"
    
    # Create card container
    with st.container():
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background-color: #f9f9f9;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h3 style="margin-top: 0;">{traffic_light} {name}</h3>
                <div style="font-size: 2em; font-weight: bold; color: {risk_color}; margin: 10px 0;">
                    {overall_score}/100
                </div>
                <div style="color: {risk_color}; font-weight: bold; margin-bottom: 15px;">
                    {risk_indicator}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Get top 2 risk factors (reasons with lowest scores)
        category_scores = protocol_data['scores']
        categories = ['security', 'financial', 'operational', 'market']
        
        # Sort categories by score (ascending) to get highest risks
        sorted_categories = sorted(
            categories,
            key=lambda c: category_scores[c]
        )
        
        # Display top 2 risk factors
        st.markdown("**Key Risk Factors:**")
        for i, category in enumerate(sorted_categories[:2]):
            reasons = protocol_data['reasons'].get(category, [])
            if reasons:
                reason_text = reasons[0]  # Show first reason
                st.markdown(f"• {category.capitalize()}: {reason_text}")
        
        # Navigation button
        if st.button(
            f"View Details →",
            key=f"{key_prefix}btn_{protocol_id}",
            use_container_width=True
        ):
            st.session_state.current_view = 'detail'
            st.session_state.selected_protocol = protocol_id
            st.rerun()
