import React, { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import WalletConnect from './components/WalletConnect'
import './App.css'

function App() {
  const [connected, setConnected] = useState(false)
  const [address, setAddress] = useState<string | null>(null)

  return (
    <div className="App">
      <header className="App-header">
        <h1>Omega Capitals</h1>
        <p className="subtitle">Advanced DeFi Ecosystem with Ω-Score Governance</p>
        <WalletConnect
          onConnect={(addr) => {
            setConnected(true)
            setAddress(addr)
          }}
          onDisconnect={() => {
            setConnected(false)
            setAddress(null)
          }}
        />
      </header>

      <main className="container">
        {connected && address ? (
          <Dashboard address={address} />
        ) : (
          <div className="welcome-message">
            <h2>Welcome to Omega Capitals</h2>
            <p>Connect your wallet to access the DeFi ecosystem</p>
            <div className="features">
              <div className="feature-card">
                <h3>Ω-Funds</h3>
                <p>Tokenized ETF-like investment funds</p>
              </div>
              <div className="feature-card">
                <h3>Governance</h3>
                <p>Ω-Score based voting system</p>
              </div>
              <div className="feature-card">
                <h3>Evidence Notes</h3>
                <p>Soulbound NFT certifications</p>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Built with ❤️ for the future of DeFi</p>
      </footer>
    </div>
  )
}

export default App
