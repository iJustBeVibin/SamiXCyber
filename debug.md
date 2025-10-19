You’re getting 40 because your pipeline thinks **everything is unverified**. If you want to fix it fast, run this **brutal checklist** top-to-bottom. And no—the symbol isn’t enough; you must use a **contract address**. Symbols are **not unique** and **not accepted** by your spec.

## A) Inputs (stop here if this fails)

1. **Do NOT use symbols.** Use a 42-char **EVM address**: `^0x[0-9a-fA-F]{40}$`.

   * Print the raw input before any call.
   * Reject anything else with: “Invalid input. Provide a 0x… address.”
2. **Lowercase the address** before any Sourcify call.
3. **Sanity test addresses** (copy/paste exactly):

   * WETH: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
   * USDC (proxy): `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`

## B) Config & Environment

4. `ACTIVE_CHAIN=ethereum`, `ACTIVE_NETWORK=mainnet` at runtime (log them on app start).
5. `ETHERSCAN_API_KEY` is **present** and **not empty**. Log the first 4 chars + key length.
6. `ETHERSCAN_BASE` and `SOURCIFY_API` are set to the expected hosts.
7. **Never** set `ALLOW_TX=true`. Abort if so (even though you’re read-only).

## C) Etherscan “getsourcecode” call

8. Log the **full URL** (without key) + **HTTP status** + first 200 chars of response.
9. If status ≠ 200, print the body; don’t swallow it.
10. Confirm `result[0]` exists. If not, log the full JSON and stop with “Data unavailable”.
11. Inspect fields: `Proxy`, `Implementation`, `ContractName`, `SourceCode`, `ABI`.

    * If `Proxy=="1"` but `Implementation` empty → you’re rate-limited or keyless; fix that first.

## D) Proxy hop (most common failure)

12. If `Proxy=="1"` and `Implementation` is a 0x address, **re-query** `getsourcecode` on the **implementation address**.
13. Log **both** addresses and **which one** you used for final verdict.
14. If after hop `ABI == "Contract source code not verified"` and `SourceCode` empty: mark `etherscan_verified=False` and proceed to Sourcify (next section).

## E) Sourcify fallback (second common failure)

15. Call:

```
GET {SOURCIFY_API}/check-by-addresses?addresses=<lowercase-addr>&chainIds=1
```

16. Log status code + response.
17. If any item has `"status": "perfect"` or `"partial"`, set `verified=True`.
18. If Sourcify 404/empty, keep `verified=False` **only if** Etherscan also said unverified.

## F) Rate limiting & API key issues

19. If Etherscan returns 403/429 or `"Max rate limit reached"`:

* Backoff (e.g., 200ms → 500ms → 1s) and retry up to 2 times.
* If still failing, print a **clear** message: “Etherscan unavailable (429/403) — using Sourcify only.”

20. If Sourcify fails too, set: `verified=False`, `bytecode_only=True`, and add reason `"Data unavailable (Etherscan/Sourcify)"`.

## G) ABI handling (don’t block yourself)

21. **Only require ABI when Etherscan verified.** Don’t tie verification to ABI parsing success.
22. If ABI is present (string), run **case-insensitive** checks for:

* `owner`, `transferOwnership` → `admin=True`
* `pause`, `unpause` → `pause=True`
* `grantRole` → `admin=True`
* `mint`, `burn` → `supply=True`

23. If ABI missing (unverified) → leave all feature flags **False**; that’s fine.

## H) Feature mapping (unified schema)

24. Build exactly these keys (no renames):
    `verified, bytecode_only, has_admin_key, has_supply_key, has_pause_key, has_freeze_key, has_wipe_key, has_kyc_key, has_fee_key, upgradeable, holders_estimate, chain, network`.
25. **Ethereum only:** set `holders_estimate=None` (not 0). Zero is misleading.
26. `upgradeable=True` if original address was a proxy (`Proxy=="1"`), regardless of implementation verification.

## I) Scorer (don’t accidentally zero it)

27. If `verified=False` → score **must** be 40 with reason “Contract unverified”.
28. If `verified=True`: start 85; −8 per True among
    `{has_admin_key, has_supply_key, has_pause_key, has_freeze_key, has_wipe_key, has_kyc_key, has_fee_key}` capped at −32.
29. Optional but recommended: if `upgradeable` **and** `has_admin_key` → −8 extra (“Upgradeable + admin control”).
30. Clip to [10,95]. Keep **max 3 reasons**.
31. **Print** the final score + reasons and the source address (proxy vs implementation) for each run.

## J) Logging (make bugs obvious)

32. On every run, log:

* Input, chain, network
* Etherscan status + `Proxy/Implementation` values
* Sourcify status + response statuses
* Final `verified`, `bytecode_only`, `governance_flags`, `upgradeable`
* Chosen address for the explorer link

33. Save the **raw Etherscan JSON** for failing cases into `/runs/debug/…json`.

## K) Minimal manual tests (must pass)

34. **WETH** (`0xC02a...C756Cc2`):

* Expect `verified=True`, `upgradeable=False`, admin/pause/supply usually False → **high score (>80)**.

35. **USDC (proxy)** (`0xA0b8...6eB48`):

* Expect `Proxy=="1"`, hop to implementation; `verified=True`, `upgradeable=True`, `has_admin_key=True` → **lower score (60–70 range depending on penalties)**.

36. **Random unverified** (any with “Contract source code not verified”):

* Expect **40** with reason “Contract unverified”.

## L) Common foot-guns (fix or you’ll be stuck at 40 forever)

37. **You passed a symbol** (e.g., `USDC`) instead of an address. Your code should *reject symbols outright*.
38. You never hopped to `Implementation`. Proxies will always look unverified if you don’t.
39. Sourcify call used **uppercase** address or wrong param. Convert to lowercase; include `chainIds=1`.
40. You swallowed Etherscan 403/429 and silently defaulted to “unverified”. Log it and try Sourcify.
41. You forced `holders_estimate=0` on Ethereum. Stop. Use `None`.
42. You tied `verified=True` to **both** Etherscan and Sourcify returning true (AND). It should be **OR**.

## M) One quick self-check (asserts)

Drop this block after your adapter returns facts for WETH:

```python
facts = get_tech_facts("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2","mainnet")
assert facts["explorer_url"].startswith("https://etherscan.io/address/")
assert facts["verified"] is True, facts
assert facts["governance_flags"]["upgradeable"] is False, facts
```

And for USDC:

```python
facts = get_tech_facts("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48","mainnet")
assert facts["verified"] is True, facts
assert facts["governance_flags"]["upgradeable"] is True, facts  # proxy
assert any([facts["governance_flags"]["admin"], facts["governance_flags"]["pause"]]), facts
```

---

Run the list. If you still get 40 on WETH or USDC after fixing **proxy hop** and **Sourcify fallback**, the bug is in your **input (symbol)**, your **env key**, or you’re **eating API errors**.
