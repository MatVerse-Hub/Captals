#!/bin/bash

# Omega Capitals Quick Deploy Script
# This script sets up the entire Omega Capitals ecosystem

echo "🚀 Omega Capitals Quick Deploy"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before continuing"
    echo "Press any key to continue after editing .env..."
    read -n 1 -s
fi

# Check for required tools
echo ""
echo "🔍 Checking required tools..."

command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "⚠️  Node.js not found. You'll need it for contract deployment." >&2; }
command -v python3 >/dev/null 2>&1 || { echo "⚠️  Python3 not found. You'll need it for backend." >&2; }

echo "✅ Required tools check complete"

# Start Docker services
echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

echo "⏳ Waiting for services to be ready..."
sleep 10

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
fi
cd ..

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
cd frontend
if [ -f "package.json" ]; then
    npm install
fi
cd ..

# Setup bot
echo ""
echo "🤖 Setting up Telegram bot..."
cd bot
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
fi
cd ..

# Start all services
echo ""
echo "🚀 Starting all services..."
docker-compose up -d

echo ""
echo "✨ Deployment complete!"
echo ""
echo "📊 Services Status:"
echo "  - Backend API: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "📝 Next steps:"
echo "  1. Deploy smart contracts: npx hardhat run scripts/deploy-testnet.js --network sepolia"
echo "  2. Update .env with contract addresses"
echo "  3. Start Telegram bot: cd bot && python bot.py"
echo ""
echo "🎯 View logs: docker-compose logs -f"
echo "🛑 Stop services: docker-compose down"
echo ""
echo "Happy deploying! 🚀"
