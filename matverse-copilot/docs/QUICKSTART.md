# 🚀 MatVerse-Copilot Quick Start Guide

## Installation (8-10 minutes)

### One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/MatVerse-Hub/test/main/matverse-copilot/install-quick.sh | bash
```

This will:
- Install Python dependencies
- Create ~/deploy-queue/ directory
- Set up the matverse-copilot CLI
- Create systemd service

## Configuration

### 1. Get Your Credentials

#### Polygon Wallet
1. Open MetaMask
2. Click Account → Settings → Security & Privacy
3. Click "Show private key"
4. Copy your private key

#### Twitter API (Optional)
1. Go to https://developer.twitter.com/
2. Create an app
3. Get API keys and tokens

#### GitHub Token (Optional)
1. GitHub → Settings → Developer Settings
2. Personal Access Tokens → Generate new token
3. Select `repo` scope

### 2. Configure .env

```bash
cd ~/matverse-copilot
nano .env
```

**Minimal config for NFT minting:**

```bash
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology/
WALLET_PRIVATE_KEY=0x...your_key...
NFT_CONTRACT_ADDRESS=0x...contract_address...
DEPLOY_QUEUE_PATH=/home/user/deploy-queue
```

**Full config with all features:**

```bash
# Blockchain
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology/
WALLET_PRIVATE_KEY=0x...
NFT_CONTRACT_ADDRESS=0x...

# Twitter (optional)
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...
TWITTER_BEARER_TOKEN=...

# GitHub (optional)
GITHUB_TOKEN=ghp_...
GITHUB_USERNAME=MatVerse-Hub

# HuggingFace (optional)
HUGGINGFACE_TOKEN=hf_...

# Queue
DEPLOY_QUEUE_PATH=/home/user/deploy-queue
LOG_LEVEL=INFO
```

## Usage

### Start the Monitor

```bash
# Foreground (see logs in real-time)
matverse-copilot start

# Background (daemon mode)
matverse-copilot start -d
```

### Check Status

```bash
matverse-copilot status
```

### Test NFT Minting (First Time)

```bash
# Create a test image
echo "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" | base64 -d > /tmp/test.png

# Mint NFT
cp /tmp/test.png ~/deploy-queue/now_evidence-000_nft.png

# Watch logs
matverse-copilot logs -f
```

Wait ~60 seconds, then check:
- https://testnets.opensea.io/account
- https://amoy.polygonscan.com/address/YOUR_WALLET_ADDRESS

### Test Twitter Bot

```bash
# Post a test tweet
echo "MatVerse-Copilot is live! 🚀 $(date)" > ~/deploy-queue/now_tweet.txt

# Check logs
matverse-copilot logs -f
```

## Common Tasks

### Mint NFT Evidence Note

```bash
# Immediate mint
cp my-image.png ~/deploy-queue/now_evidence-001_nft.png

# Scheduled for tomorrow at 9 AM
cp my-image.png ~/deploy-queue/2025-11-23_09h00_evidence-001_nft.png
```

### Post Tweet

```bash
# Immediate post
echo "New MatVerse release! 🎉" > ~/deploy-queue/now_tweet.txt

# Scheduled for Friday at 5 PM
echo "Weekend drop! 🚀" > ~/deploy-queue/2025-11-28_17h00_tweet.txt
```

### Deploy Paper

```bash
# Deploy to GitHub + arXiv
cp paper.pdf ~/deploy-queue/now_QFCT-paper.pdf
```

### Batch Mint NFTs

```bash
# Mint 10 evidence notes
for i in {1..10}; do
  cp note-$i.png ~/deploy-queue/now_evidence-$(printf "%03d" $i)_nft.png
  sleep 2  # Wait 2 seconds between mints
done
```

## Troubleshooting

### Monitor Not Starting

```bash
# Check status
matverse-copilot status

# Check logs
matverse-copilot logs

# Restart
matverse-copilot restart
```

### NFT Minting Fails

1. **Check wallet balance**
   ```bash
   # You need MATIC on Polygon Amoy testnet
   # Get free testnet MATIC: https://faucet.polygon.technology/
   ```

2. **Check RPC connection**
   ```bash
   matverse-copilot test nft
   ```

3. **Verify contract address**
   ```bash
   # Check .env has correct NFT_CONTRACT_ADDRESS
   grep NFT_CONTRACT ~/.env
   ```

### Twitter Posts Fail

```bash
# Test Twitter config
matverse-copilot test twitter

# Check API keys in .env
grep TWITTER ~/.env
```

## Advanced Features

### Scheduled Deployments

Format: `YYYY-MM-DD_HHhMM_name`

```bash
# Deploy SymbiOS v2 tomorrow at 9 PM
cp -r SymbiOS-v2/ ~/deploy-queue/2025-11-23_21h00_SymbiOS-v2/

# Post announcement Friday at 10:30 AM
echo "Big announcement!" > ~/deploy-queue/2025-11-28_10h30_announcement.txt
```

### View Queue

```bash
matverse-copilot queue
```

### Real-Time Logs

```bash
matverse-copilot logs -f
```

### System Service (Auto-Start on Boot)

```bash
# Enable auto-start
systemctl --user enable matverse-copilot

# Start service
systemctl --user start matverse-copilot

# Check service status
systemctl --user status matverse-copilot
```

## Best Practices

1. **Test First**: Always test with small files first
2. **Monitor Logs**: Keep `matverse-copilot logs -f` running when testing
3. **Check Status**: Run `matverse-copilot status` regularly
4. **Backup Keys**: Keep your .env file backed up securely
5. **Use Testnet**: Test on Polygon Amoy before mainnet

## Resources

- OpenSea Testnet: https://testnets.opensea.io
- Polygon Amoy Faucet: https://faucet.polygon.technology/
- Polygon Amoy Explorer: https://amoy.polygonscan.com
- Twitter Developer: https://developer.twitter.com
- Full Docs: [../README.md](../README.md)

---

**Happy deploying! 🚀**
