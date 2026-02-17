import React, { useState, useCallback } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Target, Shield, AlertTriangle, Info } from 'lucide-react';
import { Attack, SessionStats } from '../types';
import { imageAssets } from '../config/imageAssets';
import '../styles/Components.css';

interface MetricsPanelProps {
  sessionStats: SessionStats;
  attacks: Attack[];
}

const MetricsPanel: React.FC<MetricsPanelProps> = ({ sessionStats, attacks }) => {
  const [activeTooltip, setActiveTooltip] = useState<string | null>(null);

  const getScoreHistory = () => {
    return attacks.slice(0, 20).reverse().map((attack) => ({
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

  // Colorblind-safe palette using distinct hues and patterns
  const SEVERITY_COLORS = {
    safe: '#0077BB',    // Blue
    low: '#33BBEE',     // Cyan
    medium: '#EE7733',  // Orange
    high: '#CC3311',    // Red
    critical: '#EE3377', // Magenta
  };

  const tooltipInfo = {
    l1: {
      title: 'L1 (Linguistic Safety)',
      description: 'Measures hate speech, PII leakage, and refusal quality. Higher scores indicate potential linguistic safety issues.'
    },
    l2: {
      title: 'L2 (Security Exploitability)',
      description: 'Detects injection attacks, jailbreak attempts, and circumvention strategies. Higher scores indicate security vulnerabilities.'
    },
    l3: {
      title: 'L3 (Cognitive Stability)',
      description: 'Evaluates sycophancy, deception, and chain-of-thought leakage. Higher scores indicate cognitive manipulation risks.'
    }
  };

  const toggleTooltip = useCallback((key: string) => {
    setActiveTooltip(activeTooltip === key ? null : key);
  }, [activeTooltip]);

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
          <div className="chart-legend-info">
            <div className="legend-item-with-tooltip">
              <span className="legend-label">L1</span>
              <button 
                className="tooltip-btn"
                onClick={() => toggleTooltip('l1')}
                aria-label="Info about L1 metric"
              >
                <Info size={14} />
              </button>
              {activeTooltip === 'l1' && (
                <div className="metric-tooltip">
                  <strong>{tooltipInfo.l1.title}</strong>
                  <p>{tooltipInfo.l1.description}</p>
                </div>
              )}
            </div>
            <div className="legend-item-with-tooltip">
              <span className="legend-label">L2</span>
              <button 
                className="tooltip-btn"
                onClick={() => toggleTooltip('l2')}
                aria-label="Info about L2 metric"
              >
                <Info size={14} />
              </button>
              {activeTooltip === 'l2' && (
                <div className="metric-tooltip">
                  <strong>{tooltipInfo.l2.title}</strong>
                  <p>{tooltipInfo.l2.description}</p>
                </div>
              )}
            </div>
            <div className="legend-item-with-tooltip">
              <span className="legend-label">L3</span>
              <button 
                className="tooltip-btn"
                onClick={() => toggleTooltip('l3')}
                aria-label="Info about L3 metric"
              >
                <Info size={14} />
              </button>
              {activeTooltip === 'l3' && (
                <div className="metric-tooltip">
                  <strong>{tooltipInfo.l3.title}</strong>
                  <p>{tooltipInfo.l3.description}</p>
                </div>
              )}
            </div>
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
                <Line type="monotone" dataKey="score" stroke="#EE3377" strokeWidth={2} name="Global" />
                <Line type="monotone" dataKey="l1" stroke="#EE7733" strokeWidth={2} name="L1" strokeDasharray="5 5" />
                <Line type="monotone" dataKey="l2" stroke="#0077BB" strokeWidth={2} name="L2" strokeDasharray="3 3" />
                <Line type="monotone" dataKey="l3" stroke="#33BBEE" strokeWidth={2} name="L3" />
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
                <Bar dataKey="value" fill="#0077BB" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Architecture Visualization */}
      <div className="architecture-visualization glass-panel">
        <div className="viz-header">
          <h3>System Architecture Overview</h3>
          <p className="viz-subtitle">Feedback Loop & Continuous Evolution</p>
        </div>
        <div className="viz-image-container">
          <img
            src={imageAssets.heroes.feedbackLoop}
            alt="Evolving Feedback Loop - System Architecture"
            className="architecture-image"
            loading="lazy"
          />
          <div className="viz-overlay">
            <div className="overlay-badge">
              <span className="badge-icon">⚙️</span>
              <span className="badge-text">Adaptive System</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(MetricsPanel);
