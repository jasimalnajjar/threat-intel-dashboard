import React, { useState, useEffect } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, ResponsiveContainer, Legend
} from "recharts";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";
const COLORS = {
  CRITICAL: "#e74c3c",
  HIGH: "#e67e22",
  MEDIUM: "#f1c40f",
  LOW: "#2ecc71",
  Unknown: "#95a5a6"
};

function App() {
  const [threats, setThreats] = useState([]);
  const [stats, setStats] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [filter, setFilter] = useState({ source: "", severity: "" });

  // Fetch threats and stats when the page loads
  useEffect(() => {
    fetchData();
  }, []);

  async function fetchData() {
    try {
  const [threatRes, statsRes] = await Promise.all([
    fetch(`${API_URL}/threats?limit=50`).then(res => res.json()),
    fetch(`${API_URL}/threats/stats`).then(res => res.json()),
]);
setThreats(threatRes);
setStats(statsRes);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      setLoading(false);
    }
  }

  async function runAnalysis() {
    setAnalyzing(true);
    try {
      const res = await fetch(`${API_URL}/analyze?limit=5`);
      const data = await res.json();
      setAnalysis(data);

    } catch (error) {
      console.error("Error running analysis:", error);
    }
    setAnalyzing(false);
  }

  // Apply filters
  const filteredThreats = threats.filter((t) => {
    if (filter.source && t.source !== filter.source) return false;
    if (filter.severity && t.severity !== filter.severity) return false;
    return true;
  });

  if (loading) return <div className="loading">Loading threat data...</div>;

  // Prepare chart data
  const severityData = stats?.by_severity
    ? Object.entries(stats.by_severity).map(([name, value]) => ({ name, value }))
    : [];

  const sourceData = stats?.by_source
    ? Object.entries(stats.by_source).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <div className="app">
      <header className="header">
        <h1>Threat Intelligence Dashboard</h1>
        <p>Real-time cyber threat monitoring and AI-powered analysis</p>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card total">
          <h3>Total Threats</h3>
          <span className="stat-number">{stats?.total_threats || 0}</span>
        </div>
        {Object.entries(stats?.by_severity || {}).map(([level, count]) => (
          <div className="stat-card" key={level} style={{ borderLeftColor: COLORS[level] }}>
            <h3>{level}</h3>
            <span className="stat-number">{count}</span>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Threats by Severity</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={severityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value">
                {severityData.map((entry) => (
                  <Cell key={entry.name} fill={COLORS[entry.name] || COLORS.Unknown} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Threats by Source</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={sourceData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {sourceData.map((_, i) => (
                  <Cell key={i} fill={["#3498db", "#9b59b6", "#1abc9c"][i]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* AI Analysis */}
      <div className="analysis-section">
        <div className="analysis-header">
          <h2>AI Threat Analysis</h2>
          <button onClick={runAnalysis} disabled={analyzing} className="analyze-btn">
            {analyzing ? "Analyzing..." : "Run AI Analysis"}
          </button>
        </div>

        {analysis && (
          <div className="analysis-results">
            <div className="summary-card">
              <h3>Threat Landscape Summary</h3>
              <p>{analysis.summary}</p>
            </div>

            <div className="priority-card">
              <h3>Top Priority</h3>
              <p>{analysis.top_priority}</p>
            </div>

            <div className="analysis-grid">
              {analysis.threats?.map((t) => (
                <div className="analysis-item" key={t.id}>
                  <div className="analysis-item-header">
                    <span className="cve-id">{t.id}</span>
                    <span className={`risk-badge ${t.risk_level?.toLowerCase()}`}>
                      {t.risk_level}
                    </span>
                  </div>
                  <p className="category">{t.category}</p>
                  <p className="plain-summary">{t.plain_summary}</p>
                  <p className="action"><strong>Action:</strong> {t.action}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Threat Table */}
      <div className="table-section">
        <div className="table-header">
          <h2>Threat Feed</h2>
          <div className="filters">
            <select value={filter.source} onChange={(e) => setFilter({ ...filter, source: e.target.value })}>
              <option value="">All Sources</option>
              <option value="NVD">NVD</option>
              <option value="CISA KEV">CISA KEV</option>
            </select>
            <select value={filter.severity} onChange={(e) => setFilter({ ...filter, severity: e.target.value })}>
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>

        <table className="threat-table">
          <thead>
            <tr>
              <th>CVE ID</th>
              <th>Severity</th>
              <th>Score</th>
              <th>Source</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {filteredThreats.map((t) => (
              <tr key={t.id}>
                <td className="cve-id">{t.id}</td>
                <td>
                  <span className={`severity-badge ${t.severity?.toLowerCase()}`}>
                    {t.severity}
                  </span>
                </td>
                <td>{t.score || "N/A"}</td>
                <td>{t.source}</td>
                <td className="description-cell">{t.description?.slice(0, 150)}...</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
