"""
Omega Capitals Telegram Bot
Provides investment interface and sales agent via Telegram
"""

import os
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import requests
from sales_agent import SalesAgent

# Load environment
load_dotenv()

# Initialize bot
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TOKEN_HERE")
bot = telebot.TeleBot(BOT_TOKEN)

# Backend API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Initialize sales agent
sales_agent = SalesAgent()


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    """Welcome message"""
    welcome_text = """
🌟 Welcome to Omega Capitals Bot! 🌟

Your gateway to advanced DeFi investments.

Available commands:
/invest - Invest in Omega Funds
/funds - View available funds
/portfolio - Check your portfolio
/omega - Learn about Ω-Score
/help - Get help

Or just chat with me to get investment recommendations!
    """

    # Create inline keyboard
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("📊 View Funds", callback_data="view_funds"),
        InlineKeyboardButton("💰 Invest Now", callback_data="invest")
    )
    markup.row(
        InlineKeyboardButton("📈 My Portfolio", callback_data="portfolio")
    )

    bot.reply_to(message, welcome_text, reply_markup=markup)


@bot.message_handler(commands=['help'])
def send_help(message: Message):
    """Help message"""
    help_text = """
📚 *Omega Capitals Bot Help*

*Investment Commands:*
/invest - Start investment process
/funds - List all available funds
/portfolio - View your investments

*Information Commands:*
/omega - Learn about Ω-Score system
/metrics - View platform metrics
/status - Check bot status

*Payment:*
We use LUA-PAY for secure crypto-fiat payments.
You can pay with USDT, ETH, or MATIC.

*Support:*
For assistance, contact @OmegaCapitalsSupport
    """
    bot.reply_to(message, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['funds'])
def show_funds(message: Message):
    """Display available funds"""
    try:
        response = requests.get(f"{API_BASE_URL}/funds/")
        funds = response.json().get('funds', [])

        if not funds:
            bot.reply_to(message, "No funds available at the moment.")
            return

        funds_text = "🏦 *Available Omega Funds:*\n\n"

        for fund in funds:
            funds_text += f"*{fund['name']}* ({fund['symbol']})\n"
            funds_text += f"📊 AUM: ${fund['totalAUM']:,}\n"
            funds_text += f"💎 NAV: ${fund['navPerShare']:.2f}\n"
            funds_text += f"📈 Yearly: +{fund['performance']['yearly']}%\n"
            funds_text += f"🎯 Ω-Score: {fund['omegaScore']}\n"
            funds_text += f"💵 Min Investment: ${fund['minInvestment']}\n"
            funds_text += f"_{fund['description']}_\n\n"

        bot.reply_to(message, funds_text, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"Error fetching funds: {str(e)}")


@bot.message_handler(commands=['invest'])
def start_investment(message: Message):
    """Start investment process"""
    try:
        response = requests.get(f"{API_BASE_URL}/funds/")
        funds = response.json().get('funds', [])

        if not funds:
            bot.reply_to(message, "No funds available for investment.")
            return

        # Create fund selection keyboard
        markup = InlineKeyboardMarkup()
        for fund in funds:
            markup.add(
                InlineKeyboardButton(
                    f"{fund['name']} - Ω:{fund['omegaScore']}",
                    callback_data=f"invest_{fund['address']}"
                )
            )

        bot.send_message(
            message.chat.id,
            "Select a fund to invest in:",
            reply_markup=markup
        )

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")


@bot.message_handler(commands=['omega'])
def explain_omega_score(message: Message):
    """Explain Omega Score"""
    omega_text = """
🎯 *What is Ω-Score?*

The Omega Score (Ω) is our proprietary metric for evaluating DeFi assets and funds.

*Formula:*
```
Ω = (Ψ × Θ) / (CVaR + 1) + PoLE
```

*Components:*
• *Ψ (Psi)*: Asset quality metrics
• *Θ (Theta)*: Risk-adjusted returns
• *CVaR*: Conditional Value at Risk
• *PoLE*: Proof of Liquidity Efficiency

*Score Ratings:*
• 9000+: AAA (Exceptional)
• 8000-8999: AA (Excellent)
• 7000-7999: A (Very Good)
• 6000-6999: BBB (Good)
• Below 6000: Caution advised

Higher Ω-Score = Better risk-adjusted performance!
    """
    bot.reply_to(message, omega_text, parse_mode='Markdown')


@bot.message_handler(commands=['metrics'])
def show_metrics(message: Message):
    """Show platform metrics"""
    try:
        response = requests.get(f"{API_BASE_URL}/metrics/dashboard")
        metrics = response.json()

        metrics_text = f"""
📊 *Platform Metrics*

💰 Total Value Locked: ${metrics['tvl']:,}
👥 Total Users: {metrics['total_users']:,}
📈 24h Volume: ${metrics['volume_24h']:,}
🎯 Average Ω-Score: {metrics['avg_omega_score']}
🏦 Active Funds: {metrics['active_funds']}
🗳️ Active Proposals: {metrics['active_proposals']}
        """

        bot.reply_to(message, metrics_text, parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"Error fetching metrics: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('invest_'))
def handle_fund_selection(call):
    """Handle fund selection for investment"""
    fund_address = call.data.replace('invest_', '')

    msg = bot.send_message(
        call.message.chat.id,
        "Enter investment amount in USDT (min: 10):"
    )

    bot.register_next_step_handler(msg, process_investment_amount, fund_address)


def process_investment_amount(message: Message, fund_address: str):
    """Process investment amount"""
    try:
        amount = float(message.text)

        if amount < 10:
            bot.reply_to(message, "Minimum investment is $10 USDT")
            return

        # Create LUA-PAY invoice
        response = requests.post(
            f"{API_BASE_URL}/payments/create-invoice",
            json={
                "amount": amount,
                "currency": "USDT",
                "description": f"Investment in fund {fund_address[:8]}...",
                "product_type": "OmegaFund"
            }
        )

        invoice = response.json()

        # Send payment instructions
        payment_text = f"""
💳 *Payment Invoice Created*

Amount: {invoice['amount']} {invoice['currency']}
Invoice ID: `{invoice['invoice_id']}`

*Payment Options:*
1. Pay via link: {invoice.get('payment_url', 'N/A')}
2. Scan QR code (if available)
3. Use /status_{invoice['invoice_id']} to check payment

Payment will be confirmed automatically.
Your Evidence Note NFT will be minted upon confirmation.
        """

        bot.send_message(message.chat.id, payment_text, parse_mode='Markdown')

        # If QR code is available, send it
        if invoice.get('qr_code_url'):
            bot.send_photo(message.chat.id, invoice['qr_code_url'])

    except ValueError:
        bot.reply_to(message, "Please enter a valid number")
    except Exception as e:
        bot.reply_to(message, f"Error creating invoice: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data == 'view_funds')
def callback_view_funds(call):
    """Callback for viewing funds"""
    show_funds(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'portfolio')
def callback_portfolio(call):
    """Callback for portfolio"""
    bot.send_message(
        call.message.chat.id,
        "Portfolio feature coming soon! Connect your wallet via the web app."
    )


# Sales Agent Integration
@bot.message_handler(func=lambda msg: True)
def handle_message(message: Message):
    """Handle all other messages with sales agent"""
    user_message = message.text.lower()

    # Sales agent response
    response = sales_agent.get_response(user_message)

    bot.reply_to(message, response, parse_mode='Markdown')


def main():
    """Start bot"""
    print("🤖 Omega Capitals Bot starting...")
    print(f"Bot token: {BOT_TOKEN[:10]}...")
    print(f"API URL: {API_BASE_URL}")
    print("Bot is running! Press Ctrl+C to stop.")

    bot.infinity_polling()


if __name__ == "__main__":
    main()
