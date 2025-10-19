"""
IO utilities for Hedera Technical Risk Scoring System.
Handles saving and loading JSON receipts of analysis runs.
"""

import os
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from config import PROTOTYPE_VERSION


def save_receipt(entity_id: str, payload: Dict[str, Any]) -> str:
    """
    Save a complete analysis receipt as JSON file.
    
    Args:
        entity_id: Token ID or contract address (e.g., "0.0.12345")
        payload: Complete analysis data including scores, features, etc.
        
    Returns:
        Path to the saved file
        
    Receipt structure matches specification:
    {
        "inputs": {"id": "0.0.12345"},
        "facts": {"contract": {...}, "token": {...}},
        "features": {"tech": {...}},
        "scores": {"tech": 74, "tech_reasons": [...]},
        "links": {"hashscan": "..."},
        "ts": 1739912345,
        "versions": {"proto": "0.2-hed-tech-only"}
    }
    """
    # Ensure runs directory exists
    os.makedirs("runs", exist_ok=True)
    
    # Generate timestamp
    timestamp = int(time.time())
    
    # Clean entity ID for filename (replace dots and slashes)
    clean_id = entity_id.replace(".", "_").replace("/", "_").replace(":", "_")
    filename = f"{clean_id}-{timestamp}.json"
    filepath = os.path.join("runs", filename)
    
    # Build complete receipt structure
    receipt = {
        "inputs": {
            "id": entity_id,
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat()
        },
        "facts": payload.get("facts", {}),
        "features": payload.get("features", {}),
        "scores": payload.get("scores", {}),
        "links": payload.get("links", {}),
        "ts": timestamp,
        "versions": {
            "proto": PROTOTYPE_VERSION
        },
        "metadata": {
            "analysis_duration_ms": payload.get("duration_ms", 0),
            "success": payload.get("success", True),
            "errors": payload.get("errors", [])
        }
    }
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)
    
    return filepath


def load_receipt(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load an analysis receipt from JSON file.
    
    Args:
        filepath: Path to the JSON receipt file
        
    Returns:
        Dictionary with receipt data, or None if file doesn't exist/invalid
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def list_recent_receipts(limit: int = 10) -> list:
    """
    List recent analysis receipts.
    
    Args:
        limit: Maximum number of receipts to return
        
    Returns:
        List of (filename, timestamp, entity_id) tuples, sorted by timestamp desc
    """
    if not os.path.exists("runs"):
        return []
    
    receipts = []
    for filename in os.listdir("runs"):
        if filename.endswith(".json"):
            filepath = os.path.join("runs", filename)
            try:
                # Extract timestamp from filename
                parts = filename.replace(".json", "").split("-")
                if len(parts) >= 2:
                    entity_id = "-".join(parts[:-1]).replace("_", ".")
                    timestamp = int(parts[-1])
                    receipts.append((filename, timestamp, entity_id))
            except ValueError:
                continue
    
    # Sort by timestamp descending and limit
    receipts.sort(key=lambda x: x[1], reverse=True)
    return receipts[:limit]


def get_receipt_summary(receipt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a summary of a receipt for display.
    
    Args:
        receipt: Receipt dictionary
        
    Returns:
        Summary dictionary with key information
    """
    summary = {
        "entity_id": receipt.get("inputs", {}).get("id", "Unknown"),
        "timestamp": receipt.get("ts", 0),
        "datetime": receipt.get("inputs", {}).get("datetime", "Unknown"),
        "success": receipt.get("metadata", {}).get("success", True),
        "tech_score": receipt.get("scores", {}).get("tech", "N/A"),
        "version": receipt.get("versions", {}).get("proto", "Unknown")
    }
    
    # Get primary risk reasons
    tech_reasons = receipt.get("scores", {}).get("tech_reasons", [])
    if tech_reasons:
        summary["primary_risk"] = tech_reasons[0]
    else:
        summary["primary_risk"] = "No specific risks identified"
    
    return summary


def cleanup_old_receipts(days_to_keep: int = 30) -> int:
    """
    Clean up old receipt files.
    
    Args:
        days_to_keep: Number of days to keep receipts
        
    Returns:
        Number of files deleted
    """
    if not os.path.exists("runs"):
        return 0
    
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    deleted_count = 0
    
    for filename in os.listdir("runs"):
        if filename.endswith(".json"):
            filepath = os.path.join("runs", filename)
            try:
                # Get file modification time
                file_time = os.path.getmtime(filepath)
                if file_time < cutoff_time:
                    os.remove(filepath)
                    deleted_count += 1
            except OSError:
                continue
    
    return deleted_count


if __name__ == "__main__":
    # Test the IO utilities
    print("Testing IO utilities...")
    
    # Test saving a receipt
    test_payload = {
        "facts": {
            "contract": {"verified": True, "admin_keys_present": True},
            "token": {"type": "FUNGIBLE", "keys": {"admin": True, "supply": True}}
        },
        "features": {
            "tech": {
                "verified": True,
                "has_admin_key": True,
                "has_supply_key": True,
                "holders_estimate": 100
            }
        },
        "scores": {
            "tech": 69,
            "tech_reasons": ["Admin key present", "Supply key present"]
        },
        "links": {
            "hashscan": "https://hashscan.io/testnet/token/0.0.12345"
        },
        "success": True,
        "duration_ms": 1250
    }
    
    # Save receipt
    test_id = "0.0.12345"
    saved_path = save_receipt(test_id, test_payload)
    print(f"Saved receipt to: {saved_path}")
    
    # Load receipt back
    loaded_receipt = load_receipt(saved_path)
    if loaded_receipt:
        print(f"Successfully loaded receipt for entity: {loaded_receipt['inputs']['id']}")
        print(f"Tech score: {loaded_receipt['scores']['tech']}")
    
    # Get summary
    summary = get_receipt_summary(loaded_receipt)
    print(f"Receipt summary: {summary}")
    
    # List recent receipts
    recent = list_recent_receipts(5)
    print(f"Found {len(recent)} recent receipts")
    for filename, timestamp, entity_id in recent:
        print(f"  {filename}: {entity_id} at {datetime.fromtimestamp(timestamp)}")
    
    print("\\nIO utilities tests completed!")