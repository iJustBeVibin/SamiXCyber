"""
Risk Radar Chart Component.
Renders an interactive radar chart showing risk scores across categories.
"""

import plotly.graph_objects as go
from typing import Dict


def render_risk_radar_chart(category_scores: Dict[str, int]) -> go.Figure:
    """
    Render radar chart showing risk scores across categories.
    
    Creates an interactive radar chart with:
    - Four axes (Security, Financial, Operational, Market)
    - Color-coded risk levels
    - Hover tooltips with score details
    
    Args:
        category_scores: Dictionary with keys 'security', 'financial', 
                        'operational', 'market' and integer scores 0-100
    
    Returns:
        Plotly Figure object
    """
    # Define categories in display order
    categories = ['Security', 'Financial', 'Operational', 'Market']
    
    # Extract scores in the same order
    scores = [
        category_scores.get('security', 0),
        category_scores.get('financial', 0),
        category_scores.get('operational', 0),
        category_scores.get('market', 0)
    ]
    
    # Close the radar chart by repeating the first value
    scores_closed = scores + [scores[0]]
    categories_closed = categories + [categories[0]]
    
    # Determine overall color based on average score
    avg_score = sum(scores) / len(scores)
    if avg_score >= 70:
        fill_color = 'rgba(0, 200, 0, 0.3)'  # Green
        line_color = 'rgb(0, 150, 0)'
    elif avg_score >= 40:
        fill_color = 'rgba(255, 165, 0, 0.3)'  # Orange
        line_color = 'rgb(255, 140, 0)'
    else:
        fill_color = 'rgba(255, 0, 0, 0.3)'  # Red
        line_color = 'rgb(200, 0, 0)'
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor=fill_color,
        line=dict(color=line_color, width=2),
        name='Risk Scores',
        hovertemplate='<b>%{theta}</b><br>Score: %{r}/100<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=25,
                showticklabels=True,
                ticks='outside'
            ),
            angularaxis=dict(
                direction='clockwise',
                period=4
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    return fig
