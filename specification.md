# 📘 **Technical Risk Scoring System — Hedera Prototype Specification**

### Version 0.2 – Tech-Only (Testnet)

---

## 🧭 **Overview**

This prototype measures **technical risk** for Hedera-based tokens or contracts.

It checks how much control the creator still has (pause, wipe, etc.), and whether the code is public and verified.

It’s the foundation of the future *Combined Risk System* — the **Market Risk** part will plug in later without changes.

---

## 🧱 **Architecture Summary**

```
[Streamlit UI]
     ↓
[app.py Orchestrator]
     ↓
 ┌───────────────┐
 │  Fetchers     │
 │ mirror.py     │→ contract & token info
 │ hashscan.py   │→ verification & links
 └───────────────┘
     ↓
[features.tech] → builds standardized feature dict
     ↓
[engine.tech_baseline] → applies scoring rules
     ↓
[utils.io] → saves JSON receipt
     ↓
[Streamlit UI] → displays score, reasons, link

```

Everything runs read-only on **Hedera testnet**.

---

## 🔐 **Security & Testnet Rules**

1. **Default network:** `testnet`
    
    ```
    NETWORK=testnet
    MIRROR_API=https://testnet.mirrornode.hedera.com/api/v1
    HASHSCAN_BASE=https://hashscan.io/testnet
    ALLOW_TX=false
    
    ```
    
2. **All fetches** use testnet Mirror Node endpoints.
3. **Any transaction code** must call `assert_testnet_tx()` — it aborts if not testnet.
4. **Explorer links** always use `https://hashscan.io/testnet`.
5. **Test wallets only**, never real HBAR keys.

---

## ⚙️ **Main Components**

### 1. **Fetchers**

### `mirror.py`

Reads from the Mirror Node REST API.

- Gets contract or token facts: type, keys, holders, etc.
- Uses 4-second timeout, 2 retries.
- Returns plain dicts — no complex objects.

Example output:

```json
{
  "type": "FUNGIBLE",
  "keys": {
    "admin": true,
    "supply": true,
    "pause": false,
    "freeze": true,
    "wipe": false,
    "kyc": false,
    "fee": false
  },
  "holders_estimate": 523,
  "hashscan_url": "https://hashscan.io/testnet/token/0.0.12345"
}

```

### `hashscan.py`

Checks verification and builds explorer links.

- Calls Sourcify endpoint (if verified)
- Returns `verified`, `bytecode_only`, `hashscan_url`

Example output:

```json
{
  "verified": true,
  "bytecode_only": false,
  "admin_keys_present": true,
  "hashscan_url": "https://hashscan.io/testnet/contract/0.0.54321"
}

```

---

### 2. **Feature Builder**

### `features/tech.py`

Turns raw data → clean, AI-ready features.

**Frozen keys** (never rename/remove):

| Key | Meaning |
| --- | --- |
| verified | code public on Sourcify |
| bytecode_only | no verified source |
| has_admin_key | admin rights exist |
| has_supply_key | can mint/burn |
| has_pause_key | can pause transfers |
| has_freeze_key | can freeze accounts |
| has_wipe_key | can delete balances |
| has_kyc_key | requires KYC approval |
| has_fee_key | custom fee structure |
| holders_estimate | number of holders |

Example output:

```json
{
  "verified": true,
  "bytecode_only": false,
  "has_admin_key": true,
  "has_supply_key": true,
  "has_pause_key": false,
  "has_freeze_key": true,
  "has_wipe_key": false,
  "has_kyc_key": false,
  "has_fee_key": false,
  "holders_estimate": 523
}

```

---

### 3. **Engine — Technical Risk Logic**

### `engine/tech_baseline.py`

**Purpose:** compute a score (0–100) + human-readable reasons.

**Algorithm:**

1. If unverified → score = 40, reason = “Contract unverified”.
2. If verified → start = 85.
3. For each key in `[admin, supply, pause, freeze, wipe, kyc, fee]`
    
    → −8 points per key found (max −32).
    
4. Clip between 10 and 95.
5. Return final score + reasons (max 3).

Example code:

```python
def tech_baseline(f):
    if not f.get("verified", False):
        return 40, ["Contract unverified"]
    score, reasons = 85, []
    penalties = 0
    for k in ["has_admin_key","has_supply_key","has_pause_key",
              "has_freeze_key","has_wipe_key","has_kyc_key","has_fee_key"]:
        if f.get(k):
            penalties += 8
            reasons.append(k.replace("has_","").replace("_key","").capitalize()+" key present")
            if penalties >= 32:
                break
    score -= penalties
    score = max(10, min(95, score))
    if not reasons:
        reasons.append("Verified source; no risky keys")
    return score, reasons[:3]

```

**Outputs:**

```json
{
  "tech_score": 74,
  "tech_reasons": ["Pause key present", "Freeze key present"]
}

```

---

### 4. **Combine & Save**

### `engine/combine.py`

For now, only passes through the tech score (placeholder for future combined logic).

### `utils/io.py`

Writes a full JSON receipt per run.

```python
def save_receipt(id_or_addr:str, payload:dict)->str

```

Creates:

```
runs/0.0.12345-1739912345.json

```

**Receipt structure:**

```json
{
  "inputs": {"id": "0.0.12345"},
  "facts": {"contract": {...}, "token": {...}},
  "features": {"tech": {...}},
  "scores": {"tech": 74, "tech_reasons": ["Pause key present","Freeze key present"]},
  "links": {"hashscan": "https://hashscan.io/testnet/token/0.0.12345"},
  "ts": 1739912345,
  "versions": {"proto": "0.2-hed-tech-only"}
}

```

---

### 5. **UI (Streamlit)**

Purpose: testing and validation only.

- One text field → token ID or EVM address
- “Run” button triggers full pipeline
- Displays:
    - **Tech Score**
    - **Reasons (list)**
    - **HashScan Link**
    - **Download JSON** button
- Fails gracefully: if data missing, prints “Data unavailable.”

Minimal code outline:

```python
import streamlit as st
from fetch.mirror import hedera_token
from fetch.hashscan import hedera_contract
from features.tech import build_tech_features
from engine.tech_baseline import tech_baseline
from utils.io import save_receipt

st.title("Hedera Technical Risk Prototype")

token_id = st.text_input("Token ID or Contract (testnet)")
if st.button("Run") and token_id:
    token = hedera_token(token_id)
    contract = hedera_contract(token_id)
    feats = build_tech_features(contract, token)
    score, reasons = tech_baseline(feats)
    st.metric("Technical Score", score)
    for r in reasons: st.write(f"- {r}")
    st.link_button("View on HashScan", contract["hashscan_url"])
    path = save_receipt(token_id, {...})
    st.download_button("Download JSON", open(path,"rb").read(), file_name=path.split("/")[-1])

```

---

## 🧩 **Data Flow Recap**

```
Input: 0.0.12345 or 0xABC...
 ↓
mirror.py + hashscan.py → facts
 ↓
build_tech_features() → frozen dict
 ↓
tech_baseline() → score + reasons
 ↓
save_receipt() → JSON
 ↓
Streamlit → display + download

```

---

## 🧱 **Phases of Development**

### **Phase 1 — Setup (1–2 h)**

- Create repo & folders.
- Add `.env.example`, `requirements.txt`, `README.md`.
- Implement `config.py` and test Mirror Node ping.

### **Phase 2 — Fetchers (2 h)**

- Implement `mirror.py` and `hashscan.py`.
- Test both with real testnet IDs.
- Handle timeouts (4 s) and retries (2).

### **Phase 3 — Features (1 h)**

- Build the fixed `tech` feature map.
- Validate outputs with a few token examples.

### **Phase 4 — Engine (1 h)**

- Code baseline logic exactly as specified.
- Test edge cases (unverified, all keys present, no keys).

### **Phase 5 — UI (1 h)**

- Add minimal Streamlit interface.
- Test valid and invalid inputs.

### **Phase 6 — Polish (1 h)**

- Add error messages, ensure receipt always saves.
- Verify all links go to **testnet**.
- Write quickstart instructions in README.

Total ≈ 6 h of real work — fits a hackathon sprint.

---

## 🎯 **Success Criteria**

| Goal | Target |
| --- | --- |
| Input → Score in under 10 s | ✅ |
| Never crashes (graceful errors) | ✅ |
| Testnet only (no mainnet calls) | ✅ |
| JSON receipt always saved | ✅ |
| Feature keys fixed & AI-ready | ✅ |
| Easy extension for Market Risk | ✅ |

---

## 🚀 **Next Steps (for later phases)**

1. **Market Risk Team** — add `saucerswap.py`, `features/market.py`, and `engine/market_baseline.py`.
2. **AI Integration** — replace baseline with `tech_model.predict(features)`.
3. **Combined Score** — extend `combine.py` once both sides exist.
4. **Dashboard UI** — after validation, merge into a single polished view.

---

## 📄 **Summary**

This document defines everything you need to:

- Build a working **Hedera tech-risk scorer**.
- Keep your team aligned (same feature schema).
- Stay safe on **testnet**.
- Be ready for AI models later without re-architecting.

**Deliverable:**

A small Streamlit app that outputs a verified, repeatable **Technical Risk Score** for any Hedera testnet token or contract — complete with reasons and a downloadable JSON report.

---