import React, { useState } from 'react';
import { BarChart, TrendingUp, TrendingDown } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

interface ModelComparison {
  model_v1: string;
  model_v1_metrics: {
    avg_score: number;
    blocked_count: number;
    total_rounds: number;
    session_count: number;
  };
  model_v2: string;
  model_v2_metrics: {
    avg_score: number;
    blocked_count: number;
    total_rounds: number;
    session_count: number;
  };
}

const ModelVersionComparison: React.FC = () => {
  const [modelV1, setModelV1] = useState('');
  const [modelV2, setModelV2] = useState('');
  const [comparison, setComparison] = useState<ModelComparison | null>(null);
  const [loading, setLoading] = useState(false);

  const compareModels = async () => {
    if (!modelV1 || !modelV2) {
      alert('Please enter both model versions');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.get(
        `${API_BASE_URL}/api/dashboard/compare-models?model_v1=${modelV1}&model_v2=${modelV2}`
      );
      setComparison(response.data);
    } catch (error) {
      console.error('Error comparing models:', error);
      alert('Error comparing models');
    } finally {
      setLoading(false);
    }
  };

  const getScoreTrend = () => {
    if (!comparison) return null;
    const diff = comparison.model_v2_metrics.avg_score - comparison.model_v1_metrics.avg_score;
    if (diff > 0.05) return <TrendingUp className="trend-up" />;
    if (diff < -0.05) return <TrendingDown className="trend-down" />;
    return <span>→</span>;
  };

  return (
    <div className="model-comparison">
      <div className="comparison-header">
        <h2 className="section-title">
          <BarChart size={24} />
          Model Version Comparison
        </h2>
      </div>

      <div className="comparison-inputs glass-panel">
        <div className="input-group">
          <label>Model Version 1</label>
          <input
            type="text"
            value={modelV1}
            onChange={(e) => setModelV1(e.target.value)}
            placeholder="e.g., gpt-4-v1.0"
            className="form-control"
          />
        </div>
        <div className="input-group">
          <label>Model Version 2</label>
          <input
            type="text"
            value={modelV2}
            onChange={(e) => setModelV2(e.target.value)}
            placeholder="e.g., gpt-4-v2.0"
            className="form-control"
          />
        </div>
        <button onClick={compareModels} disabled={loading} className="btn btn-primary">
          {loading ? 'Comparing...' : 'Compare'}
        </button>
      </div>

      {comparison && (
        <div className="comparison-results">
          <div className="results-grid">
            <div className="model-card glass-panel">
              <h3>{comparison.model_v1}</h3>
              <div className="metric-row">
                <span className="metric-label">Average Score:</span>
                <span className="metric-value">{comparison.model_v1_metrics.avg_score.toFixed(3)}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Blocked Count:</span>
                <span className="metric-value">{comparison.model_v1_metrics.blocked_count}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Total Rounds:</span>
                <span className="metric-value">{comparison.model_v1_metrics.total_rounds}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Sessions:</span>
                <span className="metric-value">{comparison.model_v1_metrics.session_count}</span>
              </div>
            </div>

            <div className="comparison-indicator">
              {getScoreTrend()}
            </div>

            <div className="model-card glass-panel">
              <h3>{comparison.model_v2}</h3>
              <div className="metric-row">
                <span className="metric-label">Average Score:</span>
                <span className="metric-value">{comparison.model_v2_metrics.avg_score.toFixed(3)}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Blocked Count:</span>
                <span className="metric-value">{comparison.model_v2_metrics.blocked_count}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Total Rounds:</span>
                <span className="metric-value">{comparison.model_v2_metrics.total_rounds}</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Sessions:</span>
                <span className="metric-value">{comparison.model_v2_metrics.session_count}</span>
              </div>
            </div>
          </div>

          <div className="comparison-summary glass-panel">
            <h4>Summary</h4>
            <p>
              <strong>Score Difference:</strong>{' '}
              {(comparison.model_v2_metrics.avg_score - comparison.model_v1_metrics.avg_score).toFixed(3)}
            </p>
            <p>
              <strong>Interpretation:</strong>{' '}
              {comparison.model_v2_metrics.avg_score > comparison.model_v1_metrics.avg_score
                ? `${comparison.model_v2} shows higher vulnerability scores (worse)`
                : comparison.model_v2_metrics.avg_score < comparison.model_v1_metrics.avg_score
                ? `${comparison.model_v2} shows lower vulnerability scores (better)`
                : 'Models show similar performance'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelVersionComparison;
