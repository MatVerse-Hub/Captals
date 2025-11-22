import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# API endpoints
API_URL = os.getenv("API_URL", "http://backend:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with main menu"""
    keyboard = [
        [InlineKeyboardButton("📊 Compute Ω-Score", callback_data="compute_omega")],
        [InlineKeyboardButton("🏆 Mint Evidence NFT", callback_data="mint_nft")],
        [InlineKeyboardButton("💰 Pool Stats", callback_data="pool_stats")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎯 *Welcome to Omega Capitals Bot!*\n\n"
        "Ω-Score Portfolio Risk Management System\n\n"
        "Select an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    if query.data == "compute_omega":
        await query.edit_message_text(
            "📊 *Compute Ω-Score*\n\n"
            "Use: `/omega <cvar> <beta> <err5m> <idem>`\n\n"
            "Example:\n"
            "`/omega 0.15 0.6 0.05 0.95`\n\n"
            "Where values are between 0.0 and 1.0",
            parse_mode="Markdown"
        )

    elif query.data == "mint_nft":
        await query.edit_message_text(
            "🏆 *Mint Evidence NFT*\n\n"
            "Use: `/mint <wallet_address> <ipfs_uri>`\n\n"
            "Example:\n"
            "`/mint 0x742d35... ipfs://Qm...`",
            parse_mode="Markdown"
        )

    elif query.data == "pool_stats":
        try:
            response = requests.get(f"{API_URL}/api/pool/tvl", timeout=5)
            data = response.json()

            await query.edit_message_text(
                f"💰 *Omega Pool Statistics*\n\n"
                f"📈 TVL: ${data['tvl']:.2f} {data['currency']}\n"
                f"🔗 Network: Polygon Amoy\n"
                f"⚡ Min Ω-Score: 600\n"
                f"💵 Performance Fee: 20%",
                parse_mode="Markdown"
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error fetching pool stats: {str(e)}")

    elif query.data == "help":
        await query.edit_message_text(
            "ℹ️ *Omega Capitals Help*\n\n"
            "*Commands:*\n"
            "/start - Main menu\n"
            "/omega - Compute Ω-Score\n"
            "/mint - Mint Evidence NFT\n"
            "/pool - Pool statistics\n"
            "/help - Show this help\n\n"
            "*Formula:*\n"
            "Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem\n\n"
            "*Risk Tiers:*\n"
            "🟢 Low Risk: Ω ≥ 800\n"
            "🟡 Medium Risk: 600 ≤ Ω < 800\n"
            "🟠 High Risk: 400 ≤ Ω < 600\n"
            "🔴 Critical: Ω < 400",
            parse_mode="Markdown"
        )

async def omega_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Compute Ω-Score from user input"""
    if len(context.args) != 4:
        await update.message.reply_text(
            "❌ Usage: /omega <cvar> <beta> <err5m> <idem>\n"
            "Example: /omega 0.15 0.6 0.05 0.95"
        )
        return

    try:
        cvar, beta, err5m, idem = [float(arg) for arg in context.args]

        # Validate inputs
        for val in [cvar, beta, err5m, idem]:
            if not 0 <= val <= 1:
                raise ValueError("Values must be between 0.0 and 1.0")

        # Call API
        response = requests.post(
            f"{API_URL}/api/omega/compute",
            json={"cvar": cvar, "beta": beta, "err5m": err5m, "idem": idem},
            timeout=10
        )
        data = response.json()

        # Format response
        tier_emoji = {
            "Low Risk": "🟢",
            "Medium Risk": "🟡",
            "High Risk": "🟠",
            "Critical Risk": "🔴"
        }

        await update.message.reply_text(
            f"📊 *Ω-Score Analysis*\n\n"
            f"*Score:* {data['omega_score']}\n"
            f"*Tier:* {tier_emoji.get(data['risk_tier'], '')} {data['risk_tier']}\n\n"
            f"*Contributions:*\n"
            f"CVaR: {data['breakdown']['cvar_contribution']:.1f}\n"
            f"Beta: {data['breakdown']['beta_contribution']:.1f}\n"
            f"ERR₅m: {data['breakdown']['err5m_contribution']:.1f}\n"
            f"Idem: {data['breakdown']['idem_contribution']:.1f}\n\n"
            f"*Input Metrics:*\n"
            f"CVaR: {cvar:.2f}\n"
            f"β: {beta:.2f}\n"
            f"ERR₅m: {err5m:.2f}\n"
            f"Idem: {idem:.2f}",
            parse_mode="Markdown"
        )

    except ValueError as e:
        await update.message.reply_text(f"❌ Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error computing omega: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def mint_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mint Evidence NFT"""
    if len(context.args) != 2:
        await update.message.reply_text(
            "❌ Usage: /mint <wallet_address> <ipfs_uri>\n"
            "Example: /mint 0x742d35Cc6634C0532925a3b844Bc... ipfs://QmXyz..."
        )
        return

    try:
        to_address, uri = context.args

        # Validate address format
        if not to_address.startswith("0x") or len(to_address) != 42:
            raise ValueError("Invalid wallet address format")

        # Call API
        response = requests.post(
            f"{API_URL}/api/nft/mint",
            json={"to": to_address, "uri": uri},
            timeout=30
        )
        data = response.json()

        if data.get("success"):
            await update.message.reply_text(
                f"✅ *NFT Minted Successfully!*\n\n"
                f"🔗 Transaction: `{data['tx_hash']}`\n"
                f"📍 Recipient: `{to_address}`\n"
                f"📄 URI: `{uri}`\n\n"
                f"[View on Explorer]({data['explorer_url']})",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ Mint failed: {data}")

    except ValueError as e:
        await update.message.reply_text(f"❌ Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error minting NFT: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def pool_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get pool statistics"""
    try:
        response = requests.get(f"{API_URL}/api/pool/tvl", timeout=5)
        data = response.json()

        await update.message.reply_text(
            f"💰 *Omega Pool Statistics*\n\n"
            f"📈 Total Value Locked: ${data['tvl']:.2f} {data['currency']}\n"
            f"🔗 Network: Polygon Amoy Testnet\n"
            f"⚡ Minimum Ω-Score: 600\n"
            f"💵 Performance Fee: 20%\n\n"
            f"Only strategies with Ω-Score ≥ 600 qualify for pool allocation.",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error fetching pool stats: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message"""
    await update.message.reply_text(
        "ℹ️ *Omega Capitals Bot - Help*\n\n"
        "*Available Commands:*\n"
        "/start - Main menu\n"
        "/omega <cvar> <beta> <err5m> <idem> - Compute Ω-Score\n"
        "/mint <wallet> <uri> - Mint Evidence NFT\n"
        "/pool - Pool statistics\n"
        "/help - Show this message\n\n"
        "*Ω-Score Formula:*\n"
        "Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem\n\n"
        "*Risk Classification:*\n"
        "🟢 Low Risk: Ω ≥ 800\n"
        "🟡 Medium Risk: 600 ≤ Ω < 800\n"
        "🟠 High Risk: 400 ≤ Ω < 600\n"
        "🔴 Critical: Ω < 400\n\n"
        "For more info: https://omega-capitals.io",
        parse_mode="Markdown"
    )

def main() -> None:
    """Start the bot"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    # Create application
    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("omega", omega_command))
    app.add_handler(CommandHandler("mint", mint_command))
    app.add_handler(CommandHandler("pool", pool_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Start bot
    logger.info("🤖 Omega Capitals Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
