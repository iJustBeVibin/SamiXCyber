"""
Streamlit Web Application for Multi-Chain Technical Risk Scoring System.
"""

import streamlit as st
import json
import re
from typing import Dict, Any

# Import updated modules
from adapters import hedera, ethereum
from features.tech import build_tech_features
from engine.tech_baseline import tech_baseline, get_risk_category
from utils.io import save_receipt
from config import PROTOTYPE_VERSION

# Mapping chains to their adapter modules
ADAPTERS = {
    "hedera": hedera,
    "ethereum": ethereum,
}

def run_analysis(entity_id: str, chain: str, network: str) -> Dict[str, Any]:
    """
    Run the complete analysis pipeline for a given entity.
    """
    try:
        st.write(f"🔍 Fetching data from {chain.capitalize()} {network.capitalize()}...")
        adapter = ADAPTERS[chain]
        tech_facts = adapter.get_tech_facts(entity_id, network)

        if "error" in tech_facts:
            raise RuntimeError(f"Adapter error: {tech_facts['error']}")

        st.write("⚙️ Extracting technical features...")
        tech_features = build_tech_features(tech_facts, chain, network)

        st.write("📊 Calculating technical risk score...")
        tech_score, tech_reasons = tech_baseline(tech_features)

        payload = {
            "inputs": {"id": entity_id, "chain": chain, "network": network},
            "facts": tech_facts,
            "features": {"tech": tech_features},
            "scores": {"tech": tech_score, "tech_reasons": tech_reasons},
            "links": {"explorer": tech_facts.get("explorer_url", "")},
            "versions": {"proto": PROTOTYPE_VERSION},
        }
        
        receipt_path = save_receipt(entity_id, payload)
        payload["receipt_path"] = receipt_path
        
        return payload

    except Exception as e:
        st.error(f"Analysis failed: {e}")
        return {"error": str(e)}

def display_results(results: Dict[str, Any]):
    """Render the analysis results in Streamlit."""
    if "error" in results:
        return

    score = results["scores"]["tech"]
    reasons = results["scores"]["tech_reasons"]
    explorer_url = results["links"]["explorer"]
    risk_category = get_risk_category(score)

    # Score display
    color_map = {"Low Risk": "🟢", "Medium Risk": "🟡", "High Risk": "🟠", "Very High Risk": "🔴"}
    st.metric("Technical Risk Score", f"{color_map.get(risk_category, '⚪️')} {score}/95", help="Higher score = lower risk")
    st.write(f"**Risk Category:** {risk_category}")
    
    if explorer_url:
        st.link_button(f"🔍 View on Explorer", explorer_url)

    # Reasons
    st.subheader("Risk Factors")
    for reason in reasons:
        st.write(f"- {reason}")

    # Details expander
    with st.expander("🔧 Technical Details"):
        st.json(results["features"]["tech"])

    # Download receipt
    receipt_path = results.get("receipt_path")
    if receipt_path:
        try:
            with open(receipt_path, "r") as f:
                st.download_button(
                    "📁 Download JSON Receipt",
                    data=f.read(),
                    file_name=receipt_path.split("/")[-1],
                    mime="application/json",
                )
        except Exception as e:
            st.error(f"Could not load receipt: {e}")

def main():
    """Main Streamlit application."""
    st.set_page_config(page_title="Multi-Chain Risk Scorer", page_icon="🔗")
    st.title("🔗 Multi-Chain Technical Risk Prototype")
    st.markdown(f"**Version {PROTOTYPE_VERSION}**")

    # --- Inputs ---
    st.header("📋 Analysis Input")
    chain = st.selectbox("Select Blockchain", ("hedera", "ethereum"))
    
    network_options = ["mainnet", "testnet"]
    if chain == "ethereum":
        network_options = ["mainnet"] # Ethereum adapter only supports mainnet
    
    network = st.selectbox("Select Network", network_options)
    
    entity_id = st.text_input("Enter Address or ID", placeholder="0x... or 0.0....")

    if st.button("🚀 Run Analysis", type="primary"):
        if not entity_id:
            st.warning("Please enter an address or ID.")
        # Input validation based on selected chain
        elif chain == "ethereum" and (not entity_id.startswith("0x") or len(entity_id) != 42):
            st.error("Invalid input. Provide a 0x... address.")
        elif chain == "hedera" and not re.match(r"^\d+\.\d+\.\d+$", entity_id):
            st.error("Invalid input. Provide a Hedera ID (e.g., 0.0.12345).")
        else:
            with st.spinner("Analyzing..."):
                results = run_analysis(entity_id, chain, network)
                st.header("📊 Analysis Results")
                display_results(results)

    # --- Sidebar ---
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown(
            "This tool provides a technical risk score for smart contracts and tokens "
            "on Hedera and Ethereum."
        )
        st.header("🧪 Validation Examples")
        st.json({
            "Hedera (mainnet)": "0.0.4810450",
            "Ethereum (mainnet)": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        })

if __name__ == "__main__":
    main()
