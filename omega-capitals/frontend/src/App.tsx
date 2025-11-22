import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Activity, TrendingUp, Shield, Zap } from "lucide-react";

interface OmegaData {
  omega_score: number;
  risk_tier: string;
  metrics: {
    cvar: number;
    beta: number;
    err5m: number;
    idem: number;
  };
  breakdown: {
    cvar_contribution: number;
    beta_contribution: number;
    err5m_contribution: number;
    idem_contribution: number;
  };
}

interface PoolData {
  tvl: number;
  tvl_wei: number;
  currency: string;
}

function App() {
  const [omegaData, setOmegaData] = useState<OmegaData | null>(null);
  const [poolData, setPoolData] = useState<PoolData | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch demo Ω-Score
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Compute sample Ω-Score
        const omegaRes = await axios.post("/api/omega/compute", {
          cvar: 0.15,
          beta: 0.6,
          err5m: 0.05,
          idem: 0.95,
        });
        setOmegaData(omegaRes.data);

        // Fetch pool TVL
        try {
          const poolRes = await axios.get("/api/pool/tvl");
          setPoolData(poolRes.data);
        } catch (err) {
          console.log("Pool data not available");
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-omega-dark flex items-center justify-center">
        <div className="text-omega-green text-2xl animate-pulse">
          Loading Ω-System...
        </div>
      </div>
    );
  }

  const radarData = omegaData
    ? [
        {
          metric: "CVaR",
          value: (1 - omegaData.metrics.cvar) * 100,
          fullMark: 100,
        },
        {
          metric: "Beta",
          value: (1 - omegaData.metrics.beta) * 100,
          fullMark: 100,
        },
        {
          metric: "ERR5m",
          value: (1 - omegaData.metrics.err5m) * 100,
          fullMark: 100,
        },
        {
          metric: "Idem",
          value: omegaData.metrics.idem * 100,
          fullMark: 100,
        },
      ]
    : [];

  const contributionData = omegaData
    ? [
        { name: "CVaR", value: omegaData.breakdown.cvar_contribution },
        { name: "Beta", value: omegaData.breakdown.beta_contribution },
        { name: "ERR5m", value: omegaData.breakdown.err5m_contribution },
        { name: "Idem", value: omegaData.breakdown.idem_contribution },
      ]
    : [];

  const getTierColor = (tier: string) => {
    switch (tier) {
      case "Low Risk":
        return "#00ff00";
      case "Medium Risk":
        return "#ffff00";
      case "High Risk":
        return "#ff8800";
      case "Critical Risk":
        return "#ff0000";
      default:
        return "#00ff00";
    }
  };

  return (
    <div className="min-h-screen bg-omega-dark text-omega-green p-8">
      {/* Header */}
      <header className="mb-12 border-b border-omega-green pb-6">
        <h1 className="text-5xl font-bold mb-2 flex items-center gap-3">
          <Shield className="w-12 h-12" />
          Ω OMEGA CAPITALS
        </h1>
        <p className="text-xl text-green-500">
          Portfolio Risk Management & Evidence System
        </p>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Omega Score Card */}
        <div className="lg:col-span-1 bg-omega-gray border-2 border-omega-green p-6 rounded-lg">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-6 h-6" />
            <h2 className="text-2xl font-bold">Ω-SCORE</h2>
          </div>

          <div className="text-center my-8">
            <div className="text-7xl font-bold mb-2">
              {omegaData?.omega_score || 0}
            </div>
            <div
              className="text-2xl font-semibold"
              style={{ color: getTierColor(omegaData?.risk_tier || "") }}
            >
              {omegaData?.risk_tier}
            </div>
          </div>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span>CVaR (95%):</span>
              <span className="font-mono">
                {((omegaData?.metrics.cvar || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>Beta (β):</span>
              <span className="font-mono">
                {(omegaData?.metrics.beta || 0).toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>ERR₅m:</span>
              <span className="font-mono">
                {((omegaData?.metrics.err5m || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span>Idempotency:</span>
              <span className="font-mono">
                {((omegaData?.metrics.idem || 0) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="lg:col-span-2 bg-omega-gray border-2 border-omega-green p-6 rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Risk Profile</h2>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#00ff00" />
              <PolarAngleAxis dataKey="metric" stroke="#00ff00" />
              <PolarRadiusAxis stroke="#00ff00" />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#00ff00"
                fill="#00ff00"
                fillOpacity={0.3}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0a0e0a",
                  border: "1px solid #00ff00",
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Contribution Breakdown */}
        <div className="bg-omega-gray border-2 border-omega-green p-6 rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Score Contribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={contributionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#00ff00" opacity={0.2} />
              <XAxis dataKey="name" stroke="#00ff00" />
              <YAxis stroke="#00ff00" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0a0e0a",
                  border: "1px solid #00ff00",
                }}
              />
              <Bar dataKey="value" fill="#00ff00" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pool Stats */}
        <div className="bg-omega-gray border-2 border-omega-green p-6 rounded-lg">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-6 h-6" />
            <h2 className="text-2xl font-bold">Pool Statistics</h2>
          </div>

          <div className="space-y-6">
            <div>
              <div className="text-sm text-green-500 mb-1">Total Value Locked</div>
              <div className="text-4xl font-bold">
                ${poolData ? poolData.tvl.toFixed(2) : "0.00"}
              </div>
              <div className="text-sm text-green-700 mt-1">
                {poolData?.currency || "USDC"}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-omega-green">
              <div>
                <div className="text-sm text-green-500 mb-1">Active Strategies</div>
                <div className="text-2xl font-bold">0</div>
              </div>
              <div>
                <div className="text-sm text-green-500 mb-1">Performance Fee</div>
                <div className="text-2xl font-bold">20%</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-green-500 mb-1">Min Ω-Score</div>
                <div className="text-2xl font-bold">600</div>
              </div>
              <div>
                <div className="text-sm text-green-500 mb-1">Network</div>
                <div className="text-lg font-mono">Polygon</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Formula Display */}
      <div className="bg-omega-gray border-2 border-omega-green p-6 rounded-lg">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-6 h-6" />
          <h2 className="text-2xl font-bold">Ω-Score Formula</h2>
        </div>
        <div className="text-center text-xl font-mono">
          Ω = 0.4(1-CVaR) + 0.3(1-β) + 0.2(1-ERR₅m) + 0.1·Idem
        </div>
        <p className="text-center text-sm text-green-500 mt-4">
          Where higher scores indicate lower risk and better strategy consistency
        </p>
      </div>

      {/* Footer */}
      <footer className="mt-12 text-center text-sm text-green-700">
        <p>Omega Capitals v1.0.0 | Polygon Amoy Testnet</p>
        <p className="mt-2">
          Powered by Solidity, FastAPI, React & Web3
        </p>
      </footer>
    </div>
  );
}

export default App;
