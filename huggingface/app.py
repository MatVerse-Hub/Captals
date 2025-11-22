"""
Omega Capitals Dashboard - Hugging Face Spaces
A Gradio-based interface for viewing platform metrics
"""

import gradio as gr
import requests
import plotly.graph_objects as go
from datetime import datetime

# API endpoint (update with your deployed backend URL)
API_URL = "https://api.omega-capitals.com/api"  # Change to your actual API

def get_platform_metrics():
    """Fetch platform-wide metrics"""
    try:
        response = requests.get(f"{API_URL}/metrics/dashboard", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "tvl": 4700000,
                "total_users": 1250,
                "volume_24h": 450000,
                "avg_omega_score": 8500
            }
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        # Return mock data as fallback
        return {
            "tvl": 4700000,
            "total_users": 1250,
            "volume_24h": 450000,
            "avg_omega_score": 8500
        }

def get_funds():
    """Fetch available funds"""
    try:
        response = requests.get(f"{API_URL}/funds/", timeout=10)
        if response.status_code == 200:
            return response.json().get("funds", [])
    except Exception:
        pass

    # Mock data
    return [
        {
            "name": "Omega Growth Fund",
            "symbol": "OGF",
            "totalAUM": 1500000,
            "navPerShare": 1.15,
            "performance": {"yearly": 45.2},
            "omegaScore": 8500
        },
        {
            "name": "Omega Stable Fund",
            "symbol": "OSF",
            "totalAUM": 3200000,
            "navPerShare": 1.08,
            "performance": {"yearly": 12.3},
            "omegaScore": 9200
        }
    ]

def create_metrics_chart():
    """Create TVL chart"""
    # Mock historical data
    dates = ["Nov 15", "Nov 16", "Nov 17", "Nov 18", "Nov 19", "Nov 20", "Nov 21"]
    tvl_data = [4500000, 4535000, 4550000, 4585000, 4610000, 4650000, 4700000]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=tvl_data,
        mode='lines+markers',
        name='TVL',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="Total Value Locked (7 Days)",
        xaxis_title="Date",
        yaxis_title="TVL (USD)",
        template="plotly_dark",
        height=400
    )

    return fig

def create_fund_comparison():
    """Create fund comparison chart"""
    funds = get_funds()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[f["name"] for f in funds],
        y=[f["totalAUM"] for f in funds],
        name="AUM",
        marker_color='#667eea'
    ))

    fig.update_layout(
        title="Fund Assets Under Management",
        xaxis_title="Fund",
        yaxis_title="AUM (USD)",
        template="plotly_dark",
        height=400
    )

    return fig

def display_dashboard():
    """Main dashboard display"""
    metrics = get_platform_metrics()
    funds = get_funds()

    # Format metrics
    tvl_str = f"${metrics['tvl']:,}"
    users_str = f"{metrics['total_users']:,}"
    volume_str = f"${metrics['volume_24h']:,}"
    score_str = f"{metrics['avg_omega_score']}"

    # Format funds
    funds_table = []
    for fund in funds:
        funds_table.append([
            fund["name"],
            fund["symbol"],
            f"${fund['totalAUM']:,}",
            f"${fund['navPerShare']:.2f}",
            f"+{fund['performance']['yearly']}%",
            fund["omegaScore"]
        ])

    return (
        tvl_str,
        users_str,
        volume_str,
        score_str,
        funds_table,
        create_metrics_chart(),
        create_fund_comparison()
    )

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Soft(), title="Omega Capitals Dashboard") as demo:
    gr.Markdown("""
    # 🎯 Omega Capitals Dashboard
    ### Advanced DeFi Ecosystem with Ω-Score Governance
    """)

    with gr.Row():
        with gr.Column():
            tvl_display = gr.Textbox(label="Total Value Locked", interactive=False)
            users_display = gr.Textbox(label="Total Users", interactive=False)
        with gr.Column():
            volume_display = gr.Textbox(label="24h Volume", interactive=False)
            score_display = gr.Textbox(label="Avg Ω-Score", interactive=False)

    gr.Markdown("## 📊 Platform Analytics")

    with gr.Row():
        tvl_chart = gr.Plot(label="TVL Trend")

    with gr.Row():
        fund_chart = gr.Plot(label="Fund Comparison")

    gr.Markdown("## 🏦 Investment Funds")

    funds_table = gr.Dataframe(
        headers=["Fund Name", "Symbol", "AUM", "NAV", "Yearly Return", "Ω-Score"],
        label="Available Funds",
        interactive=False
    )

    refresh_btn = gr.Button("🔄 Refresh Data", variant="primary")

    gr.Markdown("""
    ---
    ### About Omega Capitals

    Omega Capitals uses the proprietary **Ω-Score** metric to evaluate and govern DeFi assets:

    ```
    Ω = (Ψ × Θ) / (CVaR + 1) + PoLE
    ```

    - **Ψ (Psi)**: Asset quality metrics
    - **Θ (Theta)**: Risk-adjusted returns
    - **CVaR**: Conditional Value at Risk
    - **PoLE**: Proof of Liquidity Efficiency

    **Higher Ω-Score = Better risk-adjusted performance**

    ---

    📚 [Whitepaper](https://github.com/omega-capitals/docs/whitepaper.md) |
    🌐 [Website](https://omega-capitals.com) |
    💬 [Discord](https://discord.gg/omegacapitals) |
    🐦 [Twitter](https://twitter.com/OmegaCapitals)
    """)

    # Event handlers
    refresh_btn.click(
        fn=display_dashboard,
        outputs=[
            tvl_display,
            users_display,
            volume_display,
            score_display,
            funds_table,
            tvl_chart,
            fund_chart
        ]
    )

    # Load initial data
    demo.load(
        fn=display_dashboard,
        outputs=[
            tvl_display,
            users_display,
            volume_display,
            score_display,
            funds_table,
            tvl_chart,
            fund_chart
        ]
    )

if __name__ == "__main__":
    demo.launch()
