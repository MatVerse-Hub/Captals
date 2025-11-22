import gradio as gr
import requests
import os
from typing import Tuple

# API configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

def compute_omega_score(
    cvar: float,
    beta: float,
    err5m: float,
    idem: float
) -> Tuple[str, str]:
    """Compute Ω-Score from risk metrics"""
    try:
        # Validate inputs
        for val, name in [(cvar, "CVaR"), (beta, "Beta"), (err5m, "ERR5m"), (idem, "Idem")]:
            if not 0 <= val <= 1:
                return f"❌ Error: {name} must be between 0.0 and 1.0", ""

        # Call API
        response = requests.post(
            f"{API_URL}/api/omega/compute",
            json={
                "cvar": cvar,
                "beta": beta,
                "err5m": err5m,
                "idem": idem
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            # Format main result
            result = f"""
# 📊 Ω-Score Analysis

**Score:** {data['omega_score']}
**Risk Tier:** {data['risk_tier']}

## Metric Contributions

- **CVaR Contribution:** {data['breakdown']['cvar_contribution']:.2f}
- **Beta Contribution:** {data['breakdown']['beta_contribution']:.2f}
- **ERR₅m Contribution:** {data['breakdown']['err5m_contribution']:.2f}
- **Idempotency Contribution:** {data['breakdown']['idem_contribution']:.2f}

## Input Metrics

- CVaR: {cvar:.3f}
- β: {beta:.3f}
- ERR₅m: {err5m:.3f}
- Idem: {idem:.3f}
"""

            # Format breakdown
            breakdown = f"""
## Ω-Score Breakdown

The final score is computed as:

**Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem**

- 0.4 × (1 - {cvar:.3f}) = {data['breakdown']['cvar_contribution']:.2f}
- 0.3 × (1 - {beta:.3f}) = {data['breakdown']['beta_contribution']:.2f}
- 0.2 × (1 - {err5m:.3f}) = {data['breakdown']['err5m_contribution']:.2f}
- 0.1 × {idem:.3f} = {data['breakdown']['idem_contribution']:.2f}

**Total:** {data['omega_score']}

## Risk Tiers

🟢 **Low Risk:** Ω ≥ 800
🟡 **Medium Risk:** 600 ≤ Ω < 800
🟠 **High Risk:** 400 ≤ Ω < 600
🔴 **Critical Risk:** Ω < 400
"""

            return result, breakdown
        else:
            return f"❌ API Error: {response.status_code}", ""

    except Exception as e:
        return f"❌ Error: {str(e)}", ""

def mint_evidence_nft(wallet: str, uri: str) -> str:
    """Mint Evidence NFT"""
    try:
        # Validate wallet address
        if not wallet.startswith("0x") or len(wallet) != 42:
            return "❌ Error: Invalid wallet address format (should be 0x... with 42 characters)"

        # Call API
        response = requests.post(
            f"{API_URL}/api/nft/mint",
            json={"to": wallet, "uri": uri},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return f"""
# ✅ NFT Minted Successfully!

**Transaction Hash:** `{data['tx_hash']}`

**Recipient:** `{wallet}`

**Metadata URI:** `{uri}`

**Explorer:** [View on PolygonScan]({data['explorer_url']})

The Evidence NFT has been minted and transferred to the specified wallet.
"""
            else:
                return f"❌ Minting failed: {data}"
        else:
            return f"❌ API Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_pool_stats() -> str:
    """Get pool statistics"""
    try:
        response = requests.get(f"{API_URL}/api/pool/tvl", timeout=5)

        if response.status_code == 200:
            data = response.json()
            return f"""
# 💰 Omega Pool Statistics

**Total Value Locked (TVL):** ${data['tvl']:.2f} {data['currency']}

**Network:** Polygon Amoy Testnet

**Minimum Ω-Score:** 600

**Performance Fee:** 20%

---

Only strategies with Ω-Score ≥ 600 qualify for pool allocation.
Profits are distributed proportionally based on strategy performance.
"""
        else:
            return f"❌ API Error: {response.status_code}"

    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio Interface
with gr.Blocks(title="Ω Omega Capitals", theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("""
    # 🎯 Ω OMEGA CAPITALS
    ### Portfolio Risk Management & Evidence System

    Compute Ω-Scores, mint Evidence NFTs, and manage portfolio strategies on-chain.
    """)

    with gr.Tab("📊 Compute Ω-Score"):
        gr.Markdown("""
        ### Ω-Score Calculator

        Enter your portfolio risk metrics (values between 0.0 and 1.0):

        **Formula:** Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem
        """)

        with gr.Row():
            with gr.Column():
                cvar_input = gr.Slider(
                    minimum=0, maximum=1, value=0.15, step=0.01,
                    label="CVaR (Conditional Value at Risk)",
                    info="Lower is better (0-1)"
                )
                beta_input = gr.Slider(
                    minimum=0, maximum=1, value=0.6, step=0.01,
                    label="β (Beta Coefficient)",
                    info="Market correlation (0-1)"
                )
                err5m_input = gr.Slider(
                    minimum=0, maximum=1, value=0.05, step=0.01,
                    label="ERR₅m (Maximum 5-minute Error)",
                    info="Lower is better (0-1)"
                )
                idem_input = gr.Slider(
                    minimum=0, maximum=1, value=0.95, step=0.01,
                    label="Idem (Idempotency Score)",
                    info="Strategy consistency, higher is better (0-1)"
                )

                compute_btn = gr.Button("🧮 Compute Ω-Score", variant="primary")

            with gr.Column():
                score_output = gr.Markdown(label="Result")
                breakdown_output = gr.Markdown(label="Breakdown")

        compute_btn.click(
            fn=compute_omega_score,
            inputs=[cvar_input, beta_input, err5m_input, idem_input],
            outputs=[score_output, breakdown_output]
        )

        gr.Examples(
            examples=[
                [0.15, 0.6, 0.05, 0.95],   # Good score
                [0.3, 0.8, 0.1, 0.7],       # Medium score
                [0.5, 0.9, 0.2, 0.5],       # Low score
            ],
            inputs=[cvar_input, beta_input, err5m_input, idem_input],
            label="Example Scenarios"
        )

    with gr.Tab("🏆 Mint Evidence NFT"):
        gr.Markdown("""
        ### Mint Evidence NFT

        Create an immutable on-chain record of your portfolio strategy.
        Evidence NFTs are ERC-721 tokens deployed on Polygon.
        """)

        wallet_input = gr.Textbox(
            label="Recipient Wallet Address",
            placeholder="0x742d35Cc6634C0532925a3b844Bc9e7bb337ab...",
            info="Polygon wallet address (0x...)"
        )
        uri_input = gr.Textbox(
            label="Metadata URI",
            placeholder="ipfs://QmXyz... or https://...",
            info="IPFS/Arweave URI containing strategy evidence"
        )

        mint_btn = gr.Button("🎨 Mint NFT", variant="primary")
        mint_output = gr.Markdown(label="Result")

        mint_btn.click(
            fn=mint_evidence_nft,
            inputs=[wallet_input, uri_input],
            outputs=mint_output
        )

    with gr.Tab("💰 Pool Stats"):
        gr.Markdown("""
        ### Omega Pool Statistics

        View real-time statistics for the Omega Pool liquidity system.
        """)

        stats_btn = gr.Button("📊 Refresh Stats", variant="primary")
        stats_output = gr.Markdown(label="Statistics")

        stats_btn.click(fn=get_pool_stats, outputs=stats_output)

        # Load stats on page load
        demo.load(fn=get_pool_stats, outputs=stats_output)

    gr.Markdown("""
    ---

    ### 📖 About Omega Capitals

    Omega Capitals is a decentralized portfolio risk management system that uses the **Ω-Score** metric
    to evaluate and rank investment strategies based on:

    - **CVaR (Conditional Value at Risk):** Tail risk measure at 95% confidence
    - **β (Beta Coefficient):** Market correlation and systematic risk
    - **ERR₅m (5-minute Error):** Maximum short-term deviation
    - **Idem (Idempotency):** Strategy consistency and reproducibility

    **Network:** Polygon Amoy Testnet
    **Contracts:** Verified on [PolygonScan](https://amoy.polygonscan.com)

    ---

    *Powered by Solidity, FastAPI, React & Web3*
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
