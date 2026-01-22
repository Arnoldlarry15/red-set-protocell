import React, { useState, useEffect } from 'react';
import { RefreshCw, Activity, Clock, Database } from 'lucide-react';
import axios from 'axios';
import { LiveSession, HistoricalSession } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const InfraDashboard: React.FC = () => {
  const [liveSessions, setLiveSessions] = useState<LiveSession[]>([]);
  const [historicalSessions, setHistoricalSessions] = useState<HistoricalSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'live' | 'historical'>('live');

  const fetchLiveSessions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/dashboard/live-sessions`);
      setLiveSessions(response.data.sessions);
    } catch (error) {
      console.error('Error fetching live sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalSessions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/dashboard/historical-sessions`);
      setHistoricalSessions(response.data.sessions);
    } catch (error) {
      console.error('Error fetching historical sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'live') {
      fetchLiveSessions();
      const interval = setInterval(fetchLiveSessions, 5000);
      return () => clearInterval(interval);
    } else {
      fetchHistoricalSessions();
    }
  }, [activeTab]);

  const exportSession = async (sessionId: string, format: 'json' | 'csv') => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/dashboard/export/${sessionId}?format=${format}`
      );
      const blob = new Blob([response.data.data], {
        type: format === 'csv' ? 'text/csv' : 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session_${sessionId}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting session:', error);
    }
  };

  return (
    <div className="infra-dashboard">
      <div className="dashboard-header">
        <h2 className="dashboard-title">
          <Database size={24} />
          Unified Infrastructure Dashboard
        </h2>
        <button onClick={() => activeTab === 'live' ? fetchLiveSessions() : fetchHistoricalSessions()} className="btn btn-secondary">
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      <div className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'live' ? 'active' : ''}`}
          onClick={() => setActiveTab('live')}
        >
          <Activity size={18} />
          Live Sessions
        </button>
        <button
          className={`tab-button ${activeTab === 'historical' ? 'active' : ''}`}
          onClick={() => setActiveTab('historical')}
        >
          <Clock size={18} />
          Historical Sessions
        </button>
      </div>

      {loading ? (
        <div className="loading-state">Loading...</div>
      ) : (
        <div className="sessions-container">
          {activeTab === 'live' ? (
            <div className="live-sessions">
              {liveSessions.length === 0 ? (
                <div className="empty-state">No active sessions</div>
              ) : (
                liveSessions.map((session) => (
                  <div key={session.session_id} className="session-card glass-panel">
                    <div className="session-header">
                      <h3>{session.session_id}</h3>
                      <span className={`status-badge status-${session.status}`}>
                        {session.status}
                      </span>
                    </div>
                    <div className="session-details">
                      <div className="detail-row">
                        <span className="label">Backend:</span>
                        <span className="value">{session.config.backend}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Model:</span>
                        <span className="value">{session.config.model}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Max Rounds:</span>
                        <span className="value">{session.config.max_rounds}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Cost:</span>
                        <span className="value">
                          ${session.current_cost.toFixed(2)} / ${session.max_cost.toFixed(2)}
                        </span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Started:</span>
                        <span className="value">
                          {new Date(session.start_time).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            <div className="historical-sessions">
              {historicalSessions.length === 0 ? (
                <div className="empty-state">No historical sessions</div>
              ) : (
                <table className="sessions-table">
                  <thead>
                    <tr>
                      <th>Session ID</th>
                      <th>Model Version</th>
                      <th>Start Time</th>
                      <th>End Time</th>
                      <th>Rounds</th>
                      <th>Avg Score</th>
                      <th>Blocked</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historicalSessions.map((session) => (
                      <tr key={session.session_id}>
                        <td>{session.session_id}</td>
                        <td>{session.model_version}</td>
                        <td>{new Date(session.start_time).toLocaleString()}</td>
                        <td>{new Date(session.end_time).toLocaleString()}</td>
                        <td>{session.total_rounds}</td>
                        <td>{session.average_score.toFixed(3)}</td>
                        <td>{session.blocked_count}</td>
                        <td>
                          <button
                            onClick={() => exportSession(session.session_id, 'json')}
                            className="btn btn-sm"
                          >
                            JSON
                          </button>
                          <button
                            onClick={() => exportSession(session.session_id, 'csv')}
                            className="btn btn-sm"
                          >
                            CSV
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InfraDashboard;
