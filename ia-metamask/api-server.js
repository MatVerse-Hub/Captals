#!/usr/bin/env node
/**
 * IA-MetaMask API Server
 * HTTP API for signing messages and sending transactions
 *
 * Usage:
 *   node api-server.js
 *
 * Endpoints:
 *   POST /sign      - Sign a message
 *   POST /tx        - Send a transaction
 *   POST /signTx    - Sign a transaction (without sending)
 *   GET  /address   - Get wallet address
 *   GET  /balance   - Get wallet balance
 *   GET  /status    - Get server status
 */

import { ethers } from 'ethers';
import express from 'express';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Configuration
const RPC = process.env.RPC || 'https://rpc-amoy.polygon.technology';
const PRIV = process.env.PRIVATE_KEY;
const PORT = process.env.API_PORT || 3001;

// Validate configuration
if (!PRIV) {
  console.error('❌ ERROR: PRIVATE_KEY not found in .env file');
  process.exit(1);
}

// Setup provider and signer
const provider = new ethers.JsonRpcProvider(RPC);
const signer = new ethers.Wallet(PRIV, provider);

// Stats tracking
const stats = {
  startTime: new Date(),
  requests: 0,
  signatures: 0,
  transactions: 0,
  errors: 0
};

// Create Express app
const app = express();
app.use(express.json());
app.use(express.text());

// Middleware: logging
app.use((req, res, next) => {
  stats.requests++;
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// GET /status - Server status
app.get('/status', async (req, res) => {
  try {
    const balance = await provider.getBalance(signer.address);
    const uptime = Math.floor((new Date() - stats.startTime) / 1000);

    res.json({
      status: 'online',
      network: RPC,
      address: signer.address,
      balance: ethers.formatEther(balance) + ' MATIC',
      uptime: `${Math.floor(uptime / 3600)}h ${Math.floor((uptime % 3600) / 60)}m`,
      stats: {
        requests: stats.requests,
        signatures: stats.signatures,
        transactions: stats.transactions,
        errors: stats.errors
      }
    });
  } catch (error) {
    stats.errors++;
    res.status(500).json({ error: error.message });
  }
});

// GET /address - Get wallet address
app.get('/address', (req, res) => {
  res.json({ address: signer.address });
});

// GET /balance - Get wallet balance
app.get('/balance', async (req, res) => {
  try {
    const balance = await provider.getBalance(signer.address);
    res.json({
      address: signer.address,
      balance: ethers.formatEther(balance),
      unit: 'MATIC'
    });
  } catch (error) {
    stats.errors++;
    res.status(500).json({ error: error.message });
  }
});

// POST /sign - Sign a message
app.post('/sign', async (req, res) => {
  try {
    const message = req.body.message || req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    const signature = await signer.signMessage(message);
    stats.signatures++;

    console.log(`   ✅ Signed: ${signature.substring(0, 16)}...`);

    res.json({
      message,
      signature,
      address: signer.address
    });
  } catch (error) {
    stats.errors++;
    console.error(`   ❌ Error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// POST /tx - Send transaction
app.post('/tx', async (req, res) => {
  try {
    const { to, value, data } = req.body;

    if (!to) {
      return res.status(400).json({ error: 'Recipient address (to) is required' });
    }

    const tx = await signer.sendTransaction({
      to,
      value: value || 0,
      data: data || '0x'
    });

    stats.transactions++;

    console.log(`   ✅ TX: ${tx.hash}`);
    console.log(`   🔍 https://amoy.polygonscan.com/tx/${tx.hash}`);

    res.json({
      hash: tx.hash,
      from: signer.address,
      to: tx.to,
      value: tx.value.toString(),
      explorer: `https://amoy.polygonscan.com/tx/${tx.hash}`
    });
  } catch (error) {
    stats.errors++;
    console.error(`   ❌ Error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// POST /signTx - Sign transaction (without sending)
app.post('/signTx', async (req, res) => {
  try {
    const { to, value, data } = req.body;

    if (!to) {
      return res.status(400).json({ error: 'Recipient address (to) is required' });
    }

    const tx = await signer.populateTransaction({
      to,
      value: value || 0,
      data: data || '0x'
    });

    const signedTx = await signer.signTransaction(tx);
    stats.signatures++;

    console.log(`   ✅ Transaction signed`);

    res.json({
      signedTransaction: signedTx,
      from: signer.address,
      to: tx.to
    });
  } catch (error) {
    stats.errors++;
    console.error(`   ❌ Error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// POST /signTypedData - Sign EIP-712 typed data
app.post('/signTypedData', async (req, res) => {
  try {
    const { domain, types, message } = req.body;

    if (!domain || !types || !message) {
      return res.status(400).json({
        error: 'domain, types, and message are required'
      });
    }

    const signature = await signer.signTypedData(domain, types, message);
    stats.signatures++;

    console.log(`   ✅ TypedData signed: ${signature.substring(0, 16)}...`);

    res.json({
      signature,
      address: signer.address
    });
  } catch (error) {
    stats.errors++;
    console.error(`   ❌ Error: ${error.message}`);
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║        🤖 IA-MetaMask API Server - ONLINE                 ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`📍 Network:   ${RPC}`);
  console.log(`🔑 Address:   ${signer.address}`);
  console.log(`🌐 API:       http://localhost:${PORT}`);
  console.log('');
  console.log('📋 Endpoints:');
  console.log(`   GET  /status        - Server status & stats`);
  console.log(`   GET  /address       - Wallet address`);
  console.log(`   GET  /balance       - Wallet balance`);
  console.log(`   POST /sign          - Sign message`);
  console.log(`   POST /tx            - Send transaction`);
  console.log(`   POST /signTx        - Sign transaction`);
  console.log(`   POST /signTypedData - Sign EIP-712 data`);
  console.log('');
  console.log('💡 Examples:');
  console.log(`   curl http://localhost:${PORT}/status`);
  console.log(`   curl -X POST http://localhost:${PORT}/sign -H "Content-Type: application/json" -d '{"message":"Hello MatVerse"}'`);
  console.log('');
  console.log('Press Ctrl+C to stop');
  console.log('');
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('');
  console.log('🛑 Shutting down API server...');
  console.log('');
  const uptime = Math.floor((new Date() - stats.startTime) / 1000);
  console.log('📊 Final Statistics:');
  console.log(`   Uptime: ${Math.floor(uptime / 3600)}h ${Math.floor((uptime % 3600) / 60)}m`);
  console.log(`   Total Requests: ${stats.requests}`);
  console.log(`   Signatures: ${stats.signatures}`);
  console.log(`   Transactions: ${stats.transactions}`);
  console.log(`   Errors: ${stats.errors}`);
  console.log('');
  process.exit(0);
});
