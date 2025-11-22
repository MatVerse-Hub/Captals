---
title: Omega Capitals
emoji: 🎯
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.16.0
app_file: app.py
pinned: false
license: mit
---

# Ω Omega Capitals

Portfolio Risk Management & Evidence System powered by blockchain.

## Features

- **Ω-Score Calculator:** Compute risk scores from portfolio metrics
- **Evidence NFT Minting:** Create immutable on-chain strategy records
- **Pool Statistics:** Real-time liquidity pool data

## Formula

```
Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem
```

Where:
- **CVaR:** Conditional Value at Risk (95% confidence)
- **β:** Beta coefficient (market correlation)
- **ERR₅m:** Maximum 5-minute error ratio
- **Idem:** Idempotency score (strategy consistency)

## Deployment

This Space connects to the Omega Capitals backend API deployed on Polygon Amoy Testnet.

Set `API_URL` environment variable to your backend endpoint.
