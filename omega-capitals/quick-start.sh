#!/bin/bash

# Omega Capitals Quick Start Script
# This script sets up the entire Omega Capitals ecosystem

set -e

echo "🎯 Omega Capitals - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your keys!"
    echo "   Required: PRIVATE_KEY, PUBLIC_KEY, TELEGRAM_BOT_TOKEN"
    echo ""
    read -p "Press Enter after editing .env..."
fi

# Install contract dependencies
echo "📦 Installing contract dependencies..."
cd contracts
npm install
echo "✅ Contract dependencies installed"
echo ""

# Compile contracts
echo "🔨 Compiling smart contracts..."
npx hardhat compile
echo "✅ Contracts compiled"
echo ""

# Deploy to testnet
echo "🚀 Deploying to Polygon Amoy Testnet..."
read -p "Deploy contracts now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npx hardhat run ../scripts/deploy-testnet.js --network amoy
    echo "✅ Contracts deployed!"
    echo "⚠️  Update .env with contract addresses from backend/abis/deployment-amoy.json"
    echo ""
fi

cd ..

# Start Docker services
echo "🐳 Starting Docker services..."
read -p "Start all services with docker-compose? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose up --build -d
    echo "✅ Services started!"
    echo ""
    echo "📍 Access points:"
    echo "   - Frontend:      http://localhost:3000"
    echo "   - Backend API:   http://localhost:8000"
    echo "   - API Docs:      http://localhost:8000/docs"
    echo "   - Hugging Face:  http://localhost:7860"
    echo "   - Telegram Bot:  Active (check @your_bot)"
    echo ""
fi

echo "✨ Omega Capitals is ready!"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 to see the dashboard"
echo "2. Visit http://localhost:8000/docs for API documentation"
echo "3. Use Telegram bot for on-the-go access"
echo "4. Deploy to Hugging Face Spaces for public access"
echo ""
echo "📖 Full documentation: README.md"
echo "🆘 Need help? Open an issue on GitHub"
echo ""
