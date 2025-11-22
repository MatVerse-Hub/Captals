#!/usr/bin/env node
/**
 * IA-MetaMask - Autonomous MetaMask AI
 * Auto-signs transactions, commits, and messages without user interaction
 *
 * Usage:
 *   node ia-metamask.js
 *
 * This creates a WalletConnect session that auto-approves all signature requests.
 * Scan the QR code with MetaMask mobile to connect.
 */

import { ethers } from 'ethers';
import { Web3Wallet } from '@walletconnect/web3wallet';
import dotenv from 'dotenv';
import qrcode from 'qrcode-terminal';

// Load environment variables
dotenv.config();

// Configuration
const PROJECT_ID = process.env.WALLETCONNECT_PROJECT_ID || 'e542ff314e26ff34de2d4fba98db70bb';
const RPC = process.env.RPC || 'https://rpc-amoy.polygon.technology';
const PRIV = process.env.PRIVATE_KEY;
const DEBUG = process.env.DEBUG === 'true';

// Validate configuration
if (!PRIV) {
  console.error('❌ ERROR: PRIVATE_KEY not found in .env file');
  console.error('');
  console.error('Create a .env file with:');
  console.error('  PRIVATE_KEY=your_metamask_private_key_without_0x');
  console.error('');
  console.error('See .env.example for full configuration options');
  process.exit(1);
}

// Setup provider and signer
const provider = new ethers.JsonRpcProvider(RPC);
const signer = new ethers.Wallet(PRIV, provider);

// Stats tracking
const stats = {
  startTime: new Date(),
  signaturesProcessed: 0,
  transactionsSent: 0,
  errors: 0
};

console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║          🤖 IA-MetaMask - Autonomous Signing AI           ║');
console.log('╚════════════════════════════════════════════════════════════╝');
console.log('');
console.log(`📍 Network:  ${RPC}`);
console.log(`🔑 Address:  ${signer.address}`);
console.log('');

// Initialize WalletConnect Web3Wallet
let wallet;

async function initializeWallet() {
  try {
    wallet = await Web3Wallet.init({
      projectId: PROJECT_ID,
      metadata: {
        name: 'IA-MetaMask',
        description: 'Autonomous MetaMask AI - Auto-signs without clicks',
        url: 'https://matverse.sh',
        icons: ['https://matverse.sh/icon.png']
      }
    });

    console.log('✅ WalletConnect initialized');
    console.log('');

    // Setup event handlers
    setupEventHandlers();

    // Create pairing URI
    const { uri, approval } = await wallet.pair();

    console.log('📱 Scan this QR code with MetaMask mobile:');
    console.log('');
    qrcode.generate(uri, { small: true });
    console.log('');
    console.log('Or use this URI:');
    console.log(uri);
    console.log('');
    console.log('⏳ Waiting for connection...');

  } catch (error) {
    console.error('❌ Failed to initialize WalletConnect:', error.message);
    if (DEBUG) console.error(error);
    process.exit(1);
  }
}

function setupEventHandlers() {

  // Handle session proposals (connection requests)
  wallet.on('session_proposal', async (proposal) => {
    try {
      const { id, params } = proposal;

      console.log('');
      console.log('🔗 Connection request received');
      if (DEBUG) {
        console.log('   Proposer:', params.proposer.metadata.name);
        console.log('   URL:', params.proposer.metadata.url);
      }

      // Auto-approve all session proposals
      const session = await wallet.approveSession({
        id,
        namespaces: {
          eip155: {
            methods: [
              'eth_sendTransaction',
              'eth_signTransaction',
              'personal_sign',
              'eth_sign',
              'eth_signTypedData',
              'eth_signTypedData_v4'
            ],
            chains: ['eip155:80002'], // Polygon Amoy
            events: ['chainChanged', 'accountsChanged'],
            accounts: [`eip155:80002:${signer.address}`]
          }
        }
      });

      console.log('✅ Session approved automatically');
      console.log(`   Address: ${signer.address}`);
      console.log('');
      console.log('🚀 IA-MetaMask is now ACTIVE');
      console.log('   All signature requests will be auto-approved');
      console.log('   Press Ctrl+C to stop');
      console.log('');

    } catch (error) {
      console.error('❌ Error approving session:', error.message);
      if (DEBUG) console.error(error);
      stats.errors++;
    }
  });

  // Handle session requests (signature/transaction requests)
  wallet.on('session_request', async (event) => {
    try {
      const { topic, params, id } = event;
      const { request } = params;

      const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
      console.log(`[${timestamp}] 📝 Request: ${request.method}`);

      let result;

      switch (request.method) {
        case 'personal_sign': {
          const [messageHex, address] = request.params;
          // Convert hex to string for display
          let message = messageHex;
          try {
            message = ethers.toUtf8String(messageHex);
          } catch {
            // Keep as hex if not valid UTF-8
          }

          if (DEBUG) console.log('   Message:', message.substring(0, 100));

          result = await signer.signMessage(messageHex);
          stats.signaturesProcessed++;
          console.log('   ✅ Signed:', result.substring(0, 16) + '...');
          break;
        }

        case 'eth_sign': {
          const [address, messageHex] = request.params;
          result = await signer.signMessage(messageHex);
          stats.signaturesProcessed++;
          console.log('   ✅ Signed:', result.substring(0, 16) + '...');
          break;
        }

        case 'eth_signTypedData':
        case 'eth_signTypedData_v4': {
          const [address, typedData] = request.params;
          const data = typeof typedData === 'string' ? JSON.parse(typedData) : typedData;

          if (DEBUG) console.log('   TypedData:', JSON.stringify(data).substring(0, 100));

          // Note: ethers v6 uses signTypedData
          result = await signer.signTypedData(
            data.domain,
            data.types,
            data.message
          );
          stats.signaturesProcessed++;
          console.log('   ✅ Signed:', result.substring(0, 16) + '...');
          break;
        }

        case 'eth_sendTransaction': {
          const [txParams] = request.params;

          if (DEBUG) {
            console.log('   To:', txParams.to);
            console.log('   Value:', txParams.value || '0');
          }

          // Populate transaction
          const tx = await signer.populateTransaction({
            to: txParams.to,
            value: txParams.value || 0,
            data: txParams.data || '0x',
            gasLimit: txParams.gas,
            gasPrice: txParams.gasPrice
          });

          const sentTx = await signer.sendTransaction(tx);
          result = sentTx.hash;
          stats.transactionsSent++;

          console.log('   ✅ TX sent:', result);
          console.log(`   🔍 View: https://amoy.polygonscan.com/tx/${result}`);
          break;
        }

        case 'eth_signTransaction': {
          const [txParams] = request.params;
          const tx = await signer.populateTransaction(txParams);
          const signedTx = await signer.signTransaction(tx);
          result = signedTx;
          stats.signaturesProcessed++;
          console.log('   ✅ Transaction signed');
          break;
        }

        default:
          console.log('   ⚠️  Unknown method:', request.method);
          result = '0x';
      }

      // Respond to the session request
      await wallet.respondSessionRequest({
        topic,
        response: {
          id,
          jsonrpc: '2.0',
          result
        }
      });

      console.log('');

    } catch (error) {
      console.error('   ❌ Error processing request:', error.message);
      if (DEBUG) console.error(error);
      stats.errors++;

      // Send error response
      try {
        await wallet.respondSessionRequest({
          topic: event.topic,
          response: {
            id: event.id,
            jsonrpc: '2.0',
            error: {
              code: -32000,
              message: error.message
            }
          }
        });
      } catch (respondError) {
        console.error('   ❌ Failed to send error response:', respondError.message);
      }

      console.log('');
    }
  });

  // Handle session deletion
  wallet.on('session_delete', (session) => {
    console.log('');
    console.log('🔌 Session disconnected');
    console.log('');
    printStats();
    console.log('Exiting...');
    process.exit(0);
  });
}

function printStats() {
  const uptime = Math.floor((new Date() - stats.startTime) / 1000);
  const hours = Math.floor(uptime / 3600);
  const minutes = Math.floor((uptime % 3600) / 60);
  const seconds = uptime % 60;

  console.log('📊 Session Statistics:');
  console.log(`   Uptime: ${hours}h ${minutes}m ${seconds}s`);
  console.log(`   Signatures: ${stats.signaturesProcessed}`);
  console.log(`   Transactions: ${stats.transactionsSent}`);
  console.log(`   Errors: ${stats.errors}`);
  console.log('');
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('');
  console.log('🛑 Shutting down IA-MetaMask...');
  console.log('');
  printStats();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('');
  console.log('🛑 Shutting down IA-MetaMask...');
  console.log('');
  printStats();
  process.exit(0);
});

// Start the wallet
initializeWallet().catch(error => {
  console.error('❌ Fatal error:', error.message);
  if (DEBUG) console.error(error);
  process.exit(1);
});

// Keep process alive
setInterval(() => {}, 1000000);
