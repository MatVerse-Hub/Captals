import { useState } from 'react'
import { ethers } from 'ethers'
import axios from 'axios'

interface LUAPayCheckoutProps {
  fundAddress: string
  fundName: string
  minAmount: number
  onSuccess: () => void
}

const LUAPayCheckout = ({
  fundAddress,
  fundName,
  minAmount,
  onSuccess
}) => {
  const [amount, setAmount] = useState<string>(minAmount.toString())
  const [invoice, setInvoice] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string>('')

  const handleCreateInvoice = async () => {
    try {
      setLoading(true)
      setStatus('Creating invoice...')

      // Get user address from MetaMask
      if (typeof window.ethereum === 'undefined') {
        alert('Please install MetaMask')
        return
      }

      const provider = new ethers.BrowserProvider(window.ethereum)
      const signer = await provider.getSigner()
      const userAddress = await signer.getAddress()

      // Create invoice via backend
      const response = await axios.post('/api/payments/create-invoice', {
        amount: parseFloat(amount),
        currency: 'USDT',
        description: `Investment in ${fundName}`,
        product_type: 'OmegaFund',
        user_address: userAddress
      })

      setInvoice(response.data)
      setStatus('Invoice created! You can pay via QR code or link.')
      setLoading(false)

      // Start polling for payment confirmation
      pollPaymentStatus(response.data.invoice_id)
    } catch (error: any) {
      console.error('Error creating invoice:', error)
      setStatus(`Error: ${error.response?.data?.detail || error.message}`)
      setLoading(false)
    }
  }

  const pollPaymentStatus = async (invoiceId: string) => {
    const maxAttempts = 60 // Poll for 5 minutes
    let attempts = 0

    const interval = setInterval(async () => {
      attempts++

      try {
        const response = await axios.get(`/api/payments/invoice/${invoiceId}/status`)

        if (response.data.status === 'confirmed') {
          clearInterval(interval)
          setStatus('Payment confirmed! Processing...')
          setTimeout(() => {
            setStatus('Investment successful!')
            onSuccess()
            setInvoice(null)
          }, 2000)
        } else if (attempts >= maxAttempts) {
          clearInterval(interval)
          setStatus('Payment timeout. Please check your payment status.')
        }
      } catch (error) {
        console.error('Error checking payment status:', error)
      }
    }, 5000) // Check every 5 seconds
  }

  const handlePayWithMetaMask = async () => {
    try {
      setLoading(true)
      setStatus('Preparing MetaMask transaction...')

      if (typeof window.ethereum === 'undefined') {
        alert('Please install MetaMask')
        return
      }

      const provider = new ethers.BrowserProvider(window.ethereum)
      const signer = await provider.getSigner()

      // In production, this would interact with LUA-PAY contract
      // For now, we'll show a simplified version
      const amountWei = ethers.parseEther(amount)

      const tx = await signer.sendTransaction({
        to: fundAddress,
        value: amountWei
      })

      setStatus('Transaction sent! Waiting for confirmation...')

      await tx.wait()

      setStatus('Payment confirmed!')
      setTimeout(() => {
        onSuccess()
        setInvoice(null)
      }, 2000)

      setLoading(false)
    } catch (error: any) {
      console.error('Error with MetaMask payment:', error)
      setStatus(`Error: ${error.message}`)
      setLoading(false)
    }
  }

  return (
    <div className="lua-pay-checkout">
      {!invoice ? (
        <div className="invest-form">
          <div className="amount-input">
            <label>Amount (USDT):</label>
            <input
              type="number"
              min={minAmount}
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder={`Min: ${minAmount}`}
            />
          </div>

          <button
            onClick={handleCreateInvoice}
            disabled={loading || parseFloat(amount) < minAmount}
            className="invest-btn"
          >
            {loading ? 'Processing...' : 'Invest Now'}
          </button>

          {status && <p className="status-message">{status}</p>}
        </div>
      ) : (
        <div className="invoice-display">
          <h4>Payment Invoice</h4>
          <p>Amount: {invoice.amount} {invoice.currency}</p>

          {invoice.qr_code_url && (
            <div className="qr-code">
              <img src={invoice.qr_code_url} alt="QR Code" />
              <p>Scan with mobile wallet</p>
            </div>
          )}

          <div className="payment-options">
            <a
              href={invoice.payment_url}
              target="_blank"
              rel="noopener noreferrer"
              className="payment-link-btn"
            >
              Pay via LUA-PAY
            </a>

            <button onClick={handlePayWithMetaMask} className="metamask-btn">
              Pay with MetaMask
            </button>
          </div>

          <p className="status-message">{status}</p>

          <button
            onClick={() => setInvoice(null)}
            className="cancel-btn"
          >
            Cancel
          </button>
        </div>
      )}

      <style>{`
        .lua-pay-checkout {
          margin-top: 1.5rem;
        }

        .invest-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .amount-input {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .amount-input label {
          color: rgba(255, 255, 255, 0.7);
          font-size: 0.9rem;
        }

        .amount-input input {
          padding: 0.75rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 6px;
          color: white;
          font-size: 1rem;
        }

        .invest-btn, .payment-link-btn, .metamask-btn, .cancel-btn {
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .invest-btn {
          background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
          border: none;
          color: white;
        }

        .invest-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        .invest-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .invoice-display {
          text-align: center;
          padding: 1.5rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
        }

        .invoice-display h4 {
          margin-bottom: 1rem;
        }

        .qr-code {
          margin: 1.5rem 0;
        }

        .qr-code img {
          max-width: 200px;
          border-radius: 8px;
        }

        .payment-options {
          display: flex;
          gap: 1rem;
          margin: 1.5rem 0;
          justify-content: center;
        }

        .payment-link-btn, .metamask-btn {
          flex: 1;
          text-decoration: none;
          display: inline-block;
        }

        .payment-link-btn {
          background: #667eea;
          color: white;
          border: none;
        }

        .metamask-btn {
          background: #f6851b;
          color: white;
          border: none;
        }

        .cancel-btn {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          color: white;
          margin-top: 1rem;
        }

        .status-message {
          margin-top: 1rem;
          padding: 0.75rem;
          background: rgba(102, 126, 234, 0.1);
          border-radius: 6px;
          color: #667eea;
          font-size: 0.9rem;
        }
      `}</style>
    </div>
  )
}

export default LUAPayCheckout
