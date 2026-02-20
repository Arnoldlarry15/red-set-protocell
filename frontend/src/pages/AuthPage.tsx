import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock } from 'lucide-react';
import axios from 'axios';
import { User } from '../types';
import { getUserFriendlyApiError } from '../utils/apiErrors';
import '../styles/Auth.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface AuthPageProps {
  onAuth: (apiKey: string, backend: string, userData?: User) => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ onAuth }) => {
  const [apiKey, setApiKey] = useState('');
  const [backend, setBackend] = useState<'openai' | 'anthropic'>('openai');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      setError('Please enter an API key');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Validate the API key with the backend
      const response = await axios.post(`${API_BASE_URL}/auth/validate-llm-key`, {
        api_key: apiKey,
        backend: backend
      });
      
      if (response.data.valid) {
        // Create a demo user based on validated API key
        const demoUser: User = {
          username: 'demo_user',
          email: 'demo@rsp.com',
          role: 'admin', // Default to admin for demo
        };
        onAuth(apiKey, backend, demoUser);
        setLoading(false);
        navigate('/admin'); // Navigate to admin dashboard
      }
    } catch (err) {
      setError(getUserFriendlyApiError(err, API_BASE_URL));
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="grid-pattern"></div>
      </div>
      
      <div className="auth-content">
        <div className="auth-card glass-panel-dark">
          {/* Logo Section */}
          <div className="logo-section">
            <div className="logo-placeholder">
              <img 
                src="/logo.png" 
                alt="Red Set ProtoCell" 
                style={{ width: '80px', height: '80px', objectFit: 'contain' }}
              />
            </div>
            <h1 className="logo-text">RED SET PROTOCELL</h1>
            <p className="logo-subtitle">Autonomous AI Red Teaming System</p>
          </div>

          {/* Auth Form */}
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="backend">LLM Backend</label>
              <select
                id="backend"
                value={backend}
                onChange={(e) => setBackend(e.target.value as 'openai' | 'anthropic')}
                className="form-control"
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="apiKey">API Key</label>
              <div className="input-with-icon">
                <Lock size={18} className="input-icon" />
                <input
                  id="apiKey"
                  type="password"
                  placeholder={backend === 'openai' ? 'sk-...' : 'sk-ant-...'}
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="form-control with-icon"
                />
              </div>
            </div>

            {error && (
              <div className="error-message" style={{
                padding: '10px',
                marginBottom: '15px',
                backgroundColor: '#ff4444',
                color: 'white',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                {error}
              </div>
            )}

            <button 
              type="submit" 
              className="btn btn-primary auth-button"
              disabled={loading}
            >
              {loading ? 'Authenticating...' : 'Begin Red Teaming'}
            </button>
          </form>

          {/* Info Section */}
          <div className="auth-info">
            <p>
              <strong>Offensive Security Tool</strong> | Red Teaming Engine | Ethical Guardrails
            </p>
            <p className="text-small">
              This system is an automated AI red-teaming platform for discovering LLM vulnerabilities.
            </p>
          </div>
        </div>

        {/* Security Notice */}
        <div className="security-notice glass-panel">
          <img 
            src="/logo.png" 
            alt="Red Set ProtoCell logo" 
            style={{ width: '20px', height: '20px', objectFit: 'contain' }}
          />
          <div>
            <strong>Security Notice:</strong> Your API key is stored locally and never transmitted 
            to third parties. All red teaming operations include mandatory ethical guardrails.
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
