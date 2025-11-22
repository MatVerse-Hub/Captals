import { useState, useEffect } from 'react'
import { ethers } from 'ethers'

interface WalletConnectProps {
  onConnect: (address: string) => void
  onDisconnect: () => void
}

const WalletConnect: React.FC<WalletConnectProps> = ({ onConnect, onDisconnect }) => {
  const [address, setAddress] = useState<string | null>(null)
  const [balance, setBalance] = useState<string>('0')
  const [network, setNetwork] = useState<string>('')

  useEffect(() => {
    checkConnection()
  }, [])

  const checkConnection = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const provider = new ethers.BrowserProvider(window.ethereum)
        const accounts = await provider.listAccounts()

        if (accounts.length > 0) {
          const addr = accounts[0].address
          setAddress(addr)
          onConnect(addr)
          await updateBalance(provider, addr)
          await updateNetwork(provider)
        }
      } catch (error) {
        console.error('Error checking connection:', error)
      }
    }
  }

  const connectWallet = async () => {
    if (typeof window.ethereum === 'undefined') {
      alert('Please install MetaMask to use this dApp')
      return
    }

    try {
      const provider = new ethers.BrowserProvider(window.ethereum)
      const accounts = await provider.send('eth_requestAccounts', [])

      if (accounts.length > 0) {
        const addr = accounts[0]
        setAddress(addr)
        onConnect(addr)
        await updateBalance(provider, addr)
        await updateNetwork(provider)
      }
    } catch (error) {
      console.error('Error connecting wallet:', error)
      alert('Failed to connect wallet. Please try again.')
    }
  }

  const disconnectWallet = () => {
    setAddress(null)
    setBalance('0')
    setNetwork('')
    onDisconnect()
  }

  const updateBalance = async (provider: ethers.BrowserProvider, addr: string) => {
    try {
      const balanceWei = await provider.getBalance(addr)
      const balanceEth = ethers.formatEther(balanceWei)
      setBalance(parseFloat(balanceEth).toFixed(4))
    } catch (error) {
      console.error('Error getting balance:', error)
    }
  }

  const updateNetwork = async (provider: ethers.BrowserProvider) => {
    try {
      const network = await provider.getNetwork()
      setNetwork(network.name)
    } catch (error) {
      console.error('Error getting network:', error)
    }
  }

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  }

  return (
    <div className="wallet-connect">
      {address ? (
        <div className="wallet-info">
          <div className="address-display">
            <span className="label">Connected:</span>
            <span className="address">{formatAddress(address)}</span>
          </div>
          <div className="balance-display">
            <span className="balance">{balance} MATIC</span>
            {network && <span className="network">({network})</span>}
          </div>
          <button onClick={disconnectWallet} className="disconnect-btn">
            Disconnect
          </button>
        </div>
      ) : (
        <button onClick={connectWallet} className="connect-btn">
          Connect Wallet
        </button>
      )}

      <style>{`
        .wallet-connect {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 1rem;
        }

        .wallet-info {
          display: flex;
          gap: 1.5rem;
          align-items: center;
          padding: 0.75rem 1.5rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .address-display, .balance-display {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
        }

        .label {
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.6);
          margin-bottom: 0.25rem;
        }

        .address {
          font-family: monospace;
          font-size: 1rem;
          color: #667eea;
        }

        .balance {
          font-size: 1rem;
          font-weight: bold;
        }

        .network {
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.6);
        }

        .connect-btn, .disconnect-btn {
          padding: 0.75rem 1.5rem;
          font-size: 1rem;
          font-weight: 600;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .connect-btn {
          background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
          border: none;
          color: white;
        }

        .connect-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .disconnect-btn {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
        }

        .disconnect-btn:hover {
          background: rgba(255, 69, 58, 0.2);
          border-color: rgba(255, 69, 58, 0.5);
        }
      `}</style>
    </div>
  )
}

export default WalletConnect
