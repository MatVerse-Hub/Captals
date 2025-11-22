import React, { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import axios from 'axios'

const MetricsChart: React.FC = () => {
  const [data, setData] = useState<any[]>([])
  const [metric, setMetric] = useState<string>('tvl')
  const [period, setPeriod] = useState<string>('7d')

  useEffect(() => {
    fetchChartData()
  }, [metric, period])

  const fetchChartData = async () => {
    try {
      const response = await axios.get('/api/metrics/analytics/historical', {
        params: { metric, period }
      })

      // Transform data for Recharts
      const chartData = response.data.data.map((point: any) => ({
        date: new Date(point.timestamp * 1000).toLocaleDateString(),
        value: point.value
      }))

      setData(chartData)
    } catch (error) {
      console.error('Error fetching chart data:', error)
      // Use mock data on error
      setData([
        { date: '11/15', value: 4500000 },
        { date: '11/16', value: 4535000 },
        { date: '11/17', value: 4550000 },
        { date: '11/18', value: 4585000 },
        { date: '11/19', value: 4610000 },
        { date: '11/20', value: 4650000 },
        { date: '11/21', value: 4700000 }
      ])
    }
  }

  const getMetricLabel = (m: string) => {
    switch (m) {
      case 'tvl':
        return 'Total Value Locked ($)'
      case 'omega_score':
        return 'Average Ω-Score'
      case 'volume':
        return '24h Volume ($)'
      default:
        return m
    }
  }

  return (
    <div className="metrics-chart">
      <div className="chart-controls">
        <div className="metric-selector">
          <label>Metric:</label>
          <select value={metric} onChange={(e) => setMetric(e.target.value)}>
            <option value="tvl">Total Value Locked</option>
            <option value="omega_score">Ω-Score</option>
            <option value="volume">Volume</option>
          </select>
        </div>

        <div className="period-selector">
          <label>Period:</label>
          <select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
            <option value="90d">90 Days</option>
          </select>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="date"
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '0.9rem' }}
          />
          <YAxis
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '0.9rem' }}
            tickFormatter={(value) => {
              if (metric === 'tvl' || metric === 'volume') {
                return `$${(value / 1000000).toFixed(1)}M`
              }
              return value.toLocaleString()
            }}
          />
          <Tooltip
            contentStyle={{
              background: 'rgba(26, 26, 26, 0.95)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px'
            }}
            labelStyle={{ color: 'rgba(255, 255, 255, 0.9)' }}
            formatter={(value: any) => {
              if (metric === 'tvl' || metric === 'volume') {
                return `$${value.toLocaleString()}`
              }
              return value
            }}
          />
          <Legend
            wrapperStyle={{ color: 'rgba(255, 255, 255, 0.9)' }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#667eea"
            strokeWidth={3}
            dot={{ fill: '#667eea', r: 4 }}
            activeDot={{ r: 6 }}
            name={getMetricLabel(metric)}
          />
        </LineChart>
      </ResponsiveContainer>

      <style>{`
        .metrics-chart {
          width: 100%;
        }

        .chart-controls {
          display: flex;
          gap: 2rem;
          margin-bottom: 2rem;
          justify-content: center;
        }

        .metric-selector, .period-selector {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }

        .chart-controls label {
          color: rgba(255, 255, 255, 0.7);
          font-size: 0.9rem;
        }

        .chart-controls select {
          padding: 0.5rem 1rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 6px;
          color: white;
          font-size: 0.9rem;
          cursor: pointer;
        }

        .chart-controls select:hover {
          background: rgba(255, 255, 255, 0.15);
        }
      `}</style>
    </div>
  )
}

export default MetricsChart
