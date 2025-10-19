Perfect.
You’ve now expanded your prototype to **support both Hedera and Ethereum mainnets** — still **read-only**, still **tech-risk only**, and still **AI-ready**.
Here’s your complete, clear, non-jargon specification document for this **multi-chain technical risk scoring system**.

---

# 📘 **Specification Document — Multi-Chain Technical Risk Scoring System**

### Version 0.3 — Hedera + Ethereum (Read-Only, Tech-Only)

---

## 🧭 **Purpose**

This prototype evaluates the **technical risk** of blockchain assets (smart contracts or tokens) across **Hedera Hashgraph** and **Ethereum** networks.

It checks:

* Whether the smart contract is **verified** (source code public).
* Whether any **admin or control privileges** exist.
* Whether it uses risky features (pause, freeze, upgrade, etc.).

It’s designed to:

* Work **read-only** — no real transactions.
* Run on **mainnet** and **testnet** safely.
* Allow future **AI model integration** without breaking existing code.

---

## ⚙️ **Supported Networks**

| Chain        | Networks          | Data Sources                            |
| ------------ | ----------------- | --------------------------------------- |
| **Hedera**   | testnet / mainnet | Mirror Node, HashScan, Sourcify         |
| **Ethereum** | mainnet           | Etherscan API, Sourcify, ABI heuristics |

---

## 🔐 **Security & Safety Rules**

1. **Read-Only Only:**
   No write, transfer, or creation transactions are executed anywhere.

2. **Testnet Default:**

   * Default environment = Hedera testnet.
   * Explicit config required to switch to mainnet.

3. **Guard Clause:**

   ```python
   if cfg.ALLOW_TX.lower() != "false":
       raise RuntimeError("TX disabled: read-only mode enforced")
   ```

4. **Environment Configuration**

   ```env
   # Global
   ALLOW_TX=false
   ACTIVE_CHAIN=hedera        # hedera | ethereum
   ACTIVE_NETWORK=testnet     # testnet | mainnet

   # Hedera
   HEDERA_MIRROR_TESTNET=https://testnet.mirrornode.hedera.com/api/v1
   HEDERA_MIRROR_MAINNET=https://mainnet-public.mirrornode.hedera.com/api/v1
   HASHSCAN_TESTNET=https://hashscan.io/testnet
   HASHSCAN_MAINNET=https://hashscan.io/mainnet

   # Ethereum
   ETHERSCAN_API_KEY=YOUR_API_KEY
   ETHERSCAN_BASE=https://api.etherscan.io/api
   SOURCIFY_API=https://sourcify.dev/server
   ETHERSCAN_EXPLORER=https://etherscan.io
   ```

---

## 🧱 **Architecture Overview**

```
[Streamlit UI]
     ↓
[app.py Orchestrator]
     ↓
 ┌──────────────┐
 │ Adapters     │
 │ hedera.py    │   → Hedera Mirror + HashScan
 │ ethereum.py  │   → Etherscan + Sourcify
 └──────────────┘
     ↓
[features.tech]     → unified feature schema (chain-agnostic)
     ↓
[engine.tech_baseline]  → same scoring logic for both
     ↓
[utils.io]          → save JSON receipt
     ↓
[Streamlit UI]      → display results
```

---

## 🧩 **Core Modules**

### 1. `adapters/hedera.py`

Fetches contract/token facts from the Hedera network.

**Sources:**

* Mirror Node REST API (contracts, tokens, holders)
* HashScan (explorer + Sourcify verification)

**Output (TechFacts):**

```json
{
  "verified": true,
  "bytecode_only": false,
  "admin_keys_present": true,
  "governance_flags": {
    "admin": true,
    "supply": true,
    "pause": false,
    "freeze": true,
    "wipe": false,
    "kyc": false,
    "fee": false
  },
  "holders_estimate": 523,
  "explorer_url": "https://hashscan.io/mainnet/token/0.0.12345"
}
```

**Timeout:** 4 s per call
**Retries:** 2
**Fallback:** Returns partial data with “Data unavailable” message.

---

### 2. `adapters/ethereum.py`

Fetches contract info from Ethereum.

**Sources:**

* Etherscan API (verification status, ABI)
* Sourcify (source code match)
* Bytecode pattern scan for roles and upgradeability

**Output (TechFacts):**

```json
{
  "verified": true,
  "bytecode_only": false,
  "admin_keys_present": true,
  "governance_flags": {
    "admin": true,
    "pause": true,
    "supply": false,
    "freeze": false,
    "wipe": false,
    "kyc": false,
    "fee": false,
    "upgradeable": true
  },
  "holders_estimate": null,
  "explorer_url": "https://etherscan.io/address/0xABCDEF..."
}
```

**Heuristics Used:**

| Feature            | Detection Method                               |
| ------------------ | ---------------------------------------------- |
| Ownable (admin)    | `owner()` + `transferOwnership(address)`       |
| Pausable           | `pause()` + `unpause()`                        |
| Access control     | `grantRole(bytes32,address)`                   |
| Upgradeable        | `upgradeTo(address)` or storage slot `eip1967` |
| Mint/Burn (supply) | `mint(address,uint256)` or `burn(uint256)`     |

---

### 3. **Unified Interface**

Both adapters implement:

```python
def get_tech_facts(id_or_addr: str, network: str) -> dict
```

This allows a single pipeline to work with both chains.

---

### 4. **Feature Builder — `features/tech.py`**

Turns chain-specific data into a **unified feature set**.

**Frozen Keys (do not rename):**

| Feature          | Description                                  |
| ---------------- | -------------------------------------------- |
| verified         | Source code verified                         |
| bytecode_only    | Not verified                                 |
| has_admin_key    | Owner or admin privileges                    |
| has_supply_key   | Mint/burn capabilities                       |
| has_pause_key    | Can pause transactions                       |
| has_freeze_key   | Freeze ability (Hedera only)                 |
| has_wipe_key     | Can delete tokens                            |
| has_kyc_key      | Requires KYC approval                        |
| has_fee_key      | Has custom fee mechanism                     |
| holders_estimate | Number of holders                            |
| upgradeable      | Can upgrade contract (Ethereum + Hedera EVM) |
| chain            | "hedera" / "ethereum"                        |
| network          | "testnet" / "mainnet"                        |

**Example:**

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
  "holders_estimate": 523,
  "upgradeable": false,
  "chain": "hedera",
  "network": "mainnet"
}
```

---

### 5. **Scoring Logic — `engine/tech_baseline.py`**

Same logic for all chains.

**Algorithm:**

1. If unverified → score = 40, reason = “Contract unverified.”
2. If verified → start at 85.
3. For each risky key in
   `[admin, supply, pause, freeze, wipe, kyc, fee]` → −8 points each (max −32).
4. If `upgradeable` and `has_admin_key` → −8 additional.
5. Clip result to [10, 95].
6. Keep top 3 reasons.

**Example output:**

```json
{
  "tech_score": 69,
  "tech_reasons": [
    "Pause key present",
    "Upgradeable + admin control",
    "Verified source"
  ]
}
```

---

### 6. **Receipt System — `utils/io.py`**

Writes one JSON report per run under `/runs/`.

**Structure:**

```json
{
  "inputs": { "id": "0xABCDEF", "chain": "ethereum", "network": "mainnet" },
  "facts": { ... },              // raw adapter output
  "features": { "tech": { ... } },
  "scores": { "tech": 69, "tech_reasons": ["Pause key present","Verified source"] },
  "links": { "explorer": "https://etherscan.io/address/0xABCDEF..." },
  "ts": 1739912345,
  "versions": { "proto": "0.3-multichain-tech" }
}
```

---

### 7. **UI — `app.py` (Streamlit)**

Purpose: demo, testing, and validation.

**Interface:**

* Chain selector: Hedera / Ethereum
* Network selector: testnet / mainnet
* Address input
* “Run” button

**Display:**

* Score (number)
* Reasons (list)
* Explorer link
* Download JSON

**Example flow:**

1. Select **Ethereum → Mainnet**
2. Enter `0x...` address
3. Click **Run**
4. See score, reasons, and link to Etherscan.

---

## 🧱 **Phases of Development**

### **Phase 1 — Setup (1–2 h)**

* Add `.env` configuration (above).
* Add `ACTIVE_CHAIN` and `ACTIVE_NETWORK` logic to `config.py`.
* Implement validation: reject mainnet TXs.

### **Phase 2 — Chain Adapters (3–4 h)**

* Refactor your Hedera fetchers into `adapters/hedera.py`.
* Build `adapters/ethereum.py` with Etherscan + Sourcify API calls.
* Normalize both to `get_tech_facts()` format.
* Add caching for repeat calls (optional).

### **Phase 3 — Unified Feature Builder (1 h)**

* Merge both adapters into single `build_tech_features()`.
* Add `chain` and `network` as static fields.
* Validate sample runs on both chains.

### **Phase 4 — Scoring Engine (1 h)**

* Keep the same logic for both chains.
* Add small penalty for upgradeable + admin combos.
* Test all combinations.

### **Phase 5 — UI Update (1 h)**

* Add dropdowns for chain/network in Streamlit.
* Auto-route to correct adapter.
* Include the proper explorer link.
* Display results and export JSON.

### **Phase 6 — Testing & Validation (2 h)**

Test both chains:

* **Hedera mainnet/testnet:**

  * Tokens with different key sets.
  * Verified and unverified contracts.
* **Ethereum mainnet:**

  * Standard ERC-20 (Ownable).
  * Pausable token.
  * Upgradeable proxy.

Confirm:

* Scores and reasons align with expectations.
* Explorer links point to correct networks.
* JSON receipts are valid.

---

## 🧪 **Validation Dataset (examples)**

| Purpose         | Chain            | Example                                             | Expected                       |
| --------------- | ---------------- | --------------------------------------------------- | ------------------------------ |
| Safe token      | Hedera mainnet   | `0.0.4810450`                                       | High score (no risky keys)     |
| Risky token     | Hedera testnet   | Custom created                                      | Low score (admin+freeze)       |
| ERC-20 verified | Ethereum mainnet | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` (USDC) | Medium (verified + admin)      |
| Upgradeable     | Ethereum mainnet | Proxy contract                                      | Lower score (upgradeable flag) |
| Unverified      | Ethereum mainnet | Random small token                                  | 40 (“unverified”)              |

*(IDs may change — check explorer if outdated.)*

---

## 🧰 **File Tree**

```
/risk-multichain-tech
  app.py
  adapters/
    hedera.py
    ethereum.py
  features/
    tech.py
  engine/
    tech_baseline.py
  utils/
    io.py
    config.py
  runs/
  .env.example
  requirements.txt
  README.md
```

---

## 🧭 **Data Flow Recap**

```
Input (ID or Address)
   ↓
Adapter (hedera.py / ethereum.py)
   ↓
Unified feature builder (features.tech)
   ↓
Scorer (engine.tech_baseline)
   ↓
Receipt writer (utils.io)
   ↓
UI display + JSON export
```

---

## 📋 **Success Criteria**

| Metric                                      | Goal |
| ------------------------------------------- | ---- |
| Input → Output under 10 s                   | ✅    |
| Runs on both chains without code changes    | ✅    |
| No crashes on invalid input                 | ✅    |
| Links match selected chain/network          | ✅    |
| Scores reproducible, same logic both chains | ✅    |
| JSON receipts valid and complete            | ✅    |

---

## 🧱 **Future Extensions**

| Planned Module              | Description                                  |
| --------------------------- | -------------------------------------------- |
| `engine/market_baseline.py` | Market risk scoring logic (team-owned)       |
| `models/tech_model.py`      | AI model to replace rule-based logic         |
| `combine.py`                | Weighted merge of Tech + Market risk         |
| Dashboard UI                | Merge both engines into one interactive page |

---

## 📄 **Summary**

You now have a unified, chain-agnostic **Technical Risk Scoring System** that:

* Works on **Hedera** and **Ethereum**, testnet or mainnet.
* Uses **the same scoring rules** for fairness.
* Produces **consistent JSON outputs** ready for model training.
* Stays **safe** (read-only, testnet default).
* Provides a solid base for your teammates to add **Market Risk** later.

---

**Deliverable:**
A minimal Streamlit prototype that reads any **Hedera or Ethereum contract/token**, computes a transparent **Technical Risk Score**, and outputs a full JSON report for audit or AI ingestion.

Freeze this as your v0.3 reference.
