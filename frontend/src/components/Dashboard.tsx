import { useState, useEffect } from 'react'
import MetricsChart from './MetricsChart'
import LUAPayCheckout from './LUAPayCheckout'
import axios from 'axios'

interface DashboardProps {
  address: string
}

const Dashboard = ({ address }: DashboardProps) => {
  const [metrics, setMetrics] = useState<any>(null)
  const [funds, setFunds] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [address])

  const fetchDashboardData = async () => {
    try {
      // Fetch dashboard metrics
      const metricsRes = await axios.get('/api/metrics/dashboard')
      setMetrics(metricsRes.data)

      // Fetch available funds
      const fundsRes = await axios.get('/api/funds/')
      setFunds(fundsRes.data.funds)

      setLoading(false)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  return (
    <div className="dashboard">
      <h2>Dashboard Overview</h2>

      {/* Platform Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Value Locked</h3>
          <p className="metric-value">${metrics?.tvl?.toLocaleString()}</p>
        </div>
        <div className="metric-card">
          <h3>Total Users</h3>
          <p className="metric-value">{metrics?.total_users?.toLocaleString()}</p>
        </div>
        <div className="metric-card">
          <h3>24h Volume</h3>
          <p className="metric-value">${metrics?.volume_24h?.toLocaleString()}</p>
        </div>
        <div className="metric-card">
          <h3>Avg Ω-Score</h3>
          <p className="metric-value">{metrics?.avg_omega_score}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-section">
        <h3>Performance Analytics</h3>
        <MetricsChart />
      </div>

      {/* Available Funds */}
      <div className="funds-section">
        <h3>Investment Funds</h3>
        <div className="funds-grid">
          {funds.map((fund) => (
            <div key={fund.address} className="fund-card">
              <div className="fund-header">
                <h4>{fund.name}</h4>
                <span className="fund-symbol">{fund.symbol}</span>
              </div>
              <p className="fund-description">{fund.description}</p>

              <div className="fund-metrics">
                <div className="fund-metric">
                  <span className="label">AUM:</span>
                  <span className="value">${fund.totalAUM?.toLocaleString()}</span>
                </div>
                <div className="fund-metric">
                  <span className="label">NAV:</span>
                  <span className="value">${fund.navPerShare?.toFixed(2)}</span>
                </div>
                <div className="fund-metric">
                  <span className="label">Yearly:</span>
                  <span className="value positive">+{fund.performance?.yearly}%</span>
                </div>
                <div className="fund-metric">
                  <span className="label">Ω-Score:</span>
                  <span className="value">{fund.omegaScore}</span>
                </div>
              </div>

              <LUAPayCheckout
                fundAddress={fund.address}
                fundName={fund.name}
                minAmount={fund.minInvestment}
                onSuccess={() => {
                  alert('Investment successful!')
                  fetchDashboardData()
                }}
              />
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .dashboard {
          padding: 2rem;
        }

        .dashboard h2 {
          font-size: 2rem;
          margin-bottom: 2rem;
          text-align: center;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-bottom: 3rem;
        }

        .metric-card {
          padding: 1.5rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          text-align: center;
        }

        .metric-card h3 {
          font-size: 0.9rem;
          color: rgba(255, 255, 255, 0.7);
          margin-bottom: 0.75rem;
        }

        .metric-value {
          font-size: 1.8rem;
          font-weight: bold;
          color: #667eea;
        }

        .charts-section {
          margin: 3rem 0;
          padding: 2rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
        }

        .charts-section h3 {
          margin-bottom: 1.5rem;
        }

        .funds-section {
          margin-top: 3rem;
        }

        .funds-section h3 {
          margin-bottom: 1.5rem;
          font-size: 1.5rem;
        }

        .funds-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 2rem;
        }

        .fund-card {
          padding: 2rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          transition: transform 0.3s ease;
        }

        .fund-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        }

        .fund-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .fund-header h4 {
          font-size: 1.3rem;
        }

        .fund-symbol {
          padding: 0.25rem 0.75rem;
          background: rgba(102, 126, 234, 0.2);
          border-radius: 6px;
          font-size: 0.9rem;
          font-weight: bold;
        }

        .fund-description {
          color: rgba(255, 255, 255, 0.7);
          margin-bottom: 1.5rem;
        }

        .fund-metrics {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .fund-metric {
          display: flex;
          justify-content: space-between;
        }

        .fund-metric .label {
          color: rgba(255, 255, 255, 0.6);
          font-size: 0.9rem;
        }

        .fund-metric .value {
          font-weight: bold;
        }

        .fund-metric .value.positive {
          color: #4ade80;
        }

        .loading {
          text-align: center;
          padding: 4rem;
          font-size: 1.2rem;
        }
      `}</style>
    </div>
  )
}

export default Dashboard
