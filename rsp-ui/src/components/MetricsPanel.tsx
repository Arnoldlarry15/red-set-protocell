import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Target, Shield, AlertTriangle } from 'lucide-react';
import { Attack, SessionStats } from '../types';
import '../styles/Components.css';

interface MetricsPanelProps {
  sessionStats: SessionStats;
  attacks: Attack[];
}

const MetricsPanel: React.FC<MetricsPanelProps> = ({ sessionStats, attacks }) => {
  const getScoreHistory = () => {
    return attacks.slice(0, 20).reverse().map((attack, index) => ({
      round: attack.round,
      score: attack.score.global * 100,
      l1: attack.score.l1_linguistic * 100,
      l2: attack.score.l2_security * 100,
      l3: attack.score.l3_cognitive * 100,
    }));
  };

  const getSeverityDistribution = () => {
    const distribution = { safe: 0, low: 0, medium: 0, high: 0, critical: 0 };
    attacks.forEach(attack => {
      distribution[attack.severity]++;
    });
    return Object.entries(distribution).map(([name, value]) => ({ name, value }));
  };

  const getDomainDistribution = () => {
    const distribution: { [key: string]: number } = {};
    attacks.forEach(attack => {
      distribution[attack.domain] = (distribution[attack.domain] || 0) + 1;
    });
    return Object.entries(distribution).map(([name, value]) => ({ name, value }));
  };

  const SEVERITY_COLORS = {
    safe: '#22c55e',
    low: '#eab308',
    medium: '#f97316',
    high: '#ef4444',
    critical: '#dc2626',
  };

  return (
    <div className="metrics-panel">
      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card glass-panel">
          <div className="stat-icon stat-icon-primary">
            <Target size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Rounds Completed</div>
            <div className="stat-value">{sessionStats.completedRounds}</div>
            <div className="stat-subtext">of {sessionStats.totalRounds} total</div>
          </div>
        </div>

        <div className="stat-card glass-panel">
          <div className="stat-icon stat-icon-warning">
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Average Score</div>
            <div className="stat-value">{(sessionStats.averageScore * 100).toFixed(1)}%</div>
            <div className="stat-subtext">Global risk level</div>
          </div>
        </div>

        <div className="stat-card glass-panel">
          <div className="stat-icon stat-icon-success">
            <Shield size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Blocked by EGG</div>
            <div className="stat-value">{sessionStats.blockedCount}</div>
            <div className="stat-subtext">Safety violations</div>
          </div>
        </div>

        <div className="stat-card glass-panel">
          <div className="stat-icon stat-icon-critical">
            <AlertTriangle size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Critical Findings</div>
            <div className="stat-value">
              {attacks.filter(a => a.severity === 'critical').length}
            </div>
            <div className="stat-subtext">Severe vulnerabilities</div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        <div className="chart-card glass-panel">
          <div className="chart-header">
            <h3>Score History</h3>
            <span className="chart-subtitle">Last 20 rounds</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={getScoreHistory()}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="round" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(26, 26, 26, 0.95)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }} 
                />
                <Legend />
                <Line type="monotone" dataKey="score" stroke="#ef4444" strokeWidth={2} name="Global" />
                <Line type="monotone" dataKey="l1" stroke="#eab308" strokeWidth={1} name="L1" />
                <Line type="monotone" dataKey="l2" stroke="#f97316" strokeWidth={1} name="L2" />
                <Line type="monotone" dataKey="l3" stroke="#3b82f6" strokeWidth={1} name="L3" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card glass-panel">
          <div className="chart-header">
            <h3>Severity Distribution</h3>
            <span className="chart-subtitle">Attack severity levels</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={getSeverityDistribution()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => entry.value > 0 ? entry.name : ''}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {getSeverityDistribution().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[entry.name as keyof typeof SEVERITY_COLORS]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(26, 26, 26, 0.95)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card glass-panel">
          <div className="chart-header">
            <h3>Attack Domains</h3>
            <span className="chart-subtitle">Domain distribution</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={getDomainDistribution()}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} angle={-45} textAnchor="end" height={80} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(26, 26, 26, 0.95)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }} 
                />
                <Bar dataKey="value" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsPanel;
