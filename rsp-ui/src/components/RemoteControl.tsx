import React, { useState, useEffect } from 'react';
import { Play, Save, Sliders, Settings } from 'lucide-react';
import axios from 'axios';
import { ExperimentConfig } from '../types';

const API_BASE_URL = 'http://localhost:8000';

interface RemoteControlProps {
  apiKey: string;
  userRole: 'admin' | 'researcher' | 'observer';
}

const RemoteControl: React.FC<RemoteControlProps> = ({ apiKey, userRole }) => {
  const [configs, setConfigs] = useState<ExperimentConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<string>('');
  const [showConfigForm, setShowConfigForm] = useState(false);
  const [config, setConfig] = useState<ExperimentConfig>({
    name: '',
    description: '',
    backend: 'openai',
    model: 'gpt-3.5-turbo',
    max_rounds: 100,
    mutation_rate: 0.7,
    selected_domains: ['injection', 'jailbreak', 'refusal_erosion'],
    selected_strategies: ['lexical', 'encoding', 'structural'],
    mutation_weights: {
      lexical: 1.0,
      encoding: 1.0,
      structural: 1.0,
      roleplay: 1.0,
      context: 1.0,
      obfuscation: 1.0,
    },
    thresholds: {
      critical: 0.8,
      high: 0.6,
      medium: 0.4,
      low: 0.2,
    },
  });

  const canStartRun = userRole === 'admin' || userRole === 'researcher';

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/remote/config/list`);
      setConfigs(response.data.configs);
    } catch (error) {
      console.error('Error fetching configs:', error);
    }
  };

  const loadConfig = async (configId: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/remote/config/${configId}`);
      setConfig(response.data.config);
      setSelectedConfig(configId);
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const saveConfig = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/remote/config/save`, config);
      alert('Configuration saved successfully');
      fetchConfigs();
      setShowConfigForm(false);
    } catch (error) {
      console.error('Error saving config:', error);
      alert('Error saving configuration');
    }
  };

  const startRun = async () => {
    if (!canStartRun) {
      alert('You do not have permission to start runs');
      return;
    }

    try {
      const sessionConfig = {
        backend: config.backend,
        api_key: apiKey,
        model: config.model,
        max_rounds: config.max_rounds,
        max_api_cost: 10.0,
        halt_on_critical: true,
        mutation_rate: config.mutation_rate,
        selected_domains: config.selected_domains,
        selected_strategies: config.selected_strategies,
      };

      const response = await axios.post(`${API_BASE_URL}/api/remote/start-run`, sessionConfig);
      alert(`Run started successfully! Session ID: ${response.data.session_id}`);
    } catch (error) {
      console.error('Error starting run:', error);
      alert('Error starting run');
    }
  };

  if (!canStartRun) {
    return (
      <div className="remote-control">
        <div className="access-denied glass-panel">
          <Settings size={48} />
          <h3>Researcher Access Required</h3>
          <p>You need researcher or admin privileges to start runs.</p>
          <p className="current-role">Your role: <strong>{userRole}</strong></p>
        </div>
      </div>
    );
  }

  return (
    <div className="remote-control">
      <div className="control-header">
        <h2 className="section-title">
          <Settings size={24} />
          Remote Run Control
        </h2>
      </div>

      <div className="config-selector glass-panel">
        <h3>Load Saved Configuration</h3>
        <div className="selector-group">
          <select
            value={selectedConfig}
            onChange={(e) => loadConfig(e.target.value)}
            className="form-control"
          >
            <option value="">Select a configuration...</option>
            {configs.map((cfg) => (
              <option key={cfg.config_id} value={cfg.config_id}>
                {cfg.name} - {cfg.backend}/{cfg.model}
              </option>
            ))}
          </select>
          <button onClick={() => setShowConfigForm(!showConfigForm)} className="btn btn-secondary">
            <Save size={18} />
            New Config
          </button>
        </div>
      </div>

      {showConfigForm && (
        <div className="config-form glass-panel">
          <h3>Configuration Details</h3>
          <form onSubmit={(e) => { e.preventDefault(); saveConfig(); }}>
            <div className="form-row">
              <div className="form-group">
                <label>Configuration Name</label>
                <input
                  type="text"
                  value={config.name}
                  onChange={(e) => setConfig({ ...config, name: e.target.value })}
                  required
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input
                  type="text"
                  value={config.description}
                  onChange={(e) => setConfig({ ...config, description: e.target.value })}
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Backend</label>
                <select
                  value={config.backend}
                  onChange={(e) => setConfig({ ...config, backend: e.target.value })}
                  className="form-control"
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                </select>
              </div>
              <div className="form-group">
                <label>Model</label>
                <input
                  type="text"
                  value={config.model}
                  onChange={(e) => setConfig({ ...config, model: e.target.value })}
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Max Rounds</label>
                <input
                  type="number"
                  value={config.max_rounds}
                  onChange={(e) => setConfig({ ...config, max_rounds: parseInt(e.target.value) })}
                  className="form-control"
                />
              </div>
              <div className="form-group">
                <label>Mutation Rate</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={config.mutation_rate}
                  onChange={(e) => setConfig({ ...config, mutation_rate: parseFloat(e.target.value) })}
                  className="form-control"
                />
              </div>
            </div>

            <div className="form-group">
              <label>
                <Sliders size={18} />
                Mutation Weights
              </label>
              <div className="weights-grid">
                {Object.entries(config.mutation_weights || {}).map(([strategy, weight]) => (
                  <div key={strategy} className="weight-control">
                    <label>{strategy}</label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="2"
                      value={weight}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          mutation_weights: {
                            ...config.mutation_weights,
                            [strategy]: parseFloat(e.target.value),
                          },
                        })
                      }
                      className="form-control-sm"
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label>Severity Thresholds</label>
              <div className="thresholds-grid">
                {Object.entries(config.thresholds || {}).map(([level, threshold]) => (
                  <div key={level} className="threshold-control">
                    <label>{level}</label>
                    <input
                      type="number"
                      step="0.1"
                      min="0"
                      max="1"
                      value={threshold}
                      onChange={(e) =>
                        setConfig({
                          ...config,
                          thresholds: {
                            ...config.thresholds,
                            [level]: parseFloat(e.target.value),
                          },
                        })
                      }
                      className="form-control-sm"
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                <Save size={18} />
                Save Configuration
              </button>
              <button type="button" onClick={() => setShowConfigForm(false)} className="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="run-controls glass-panel">
        <h3>Start Remote Run</h3>
        <div className="run-summary">
          <div className="summary-item">
            <span className="label">Backend:</span>
            <span className="value">{config.backend}</span>
          </div>
          <div className="summary-item">
            <span className="label">Model:</span>
            <span className="value">{config.model}</span>
          </div>
          <div className="summary-item">
            <span className="label">Max Rounds:</span>
            <span className="value">{config.max_rounds}</span>
          </div>
          <div className="summary-item">
            <span className="label">Mutation Rate:</span>
            <span className="value">{config.mutation_rate}</span>
          </div>
        </div>
        <button onClick={startRun} className="btn btn-primary btn-lg">
          <Play size={24} />
          Start Run
        </button>
      </div>
    </div>
  );
};

export default RemoteControl;
