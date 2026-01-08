import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock } from 'lucide-react';
import '../styles/Auth.css';

interface AuthPageProps {
  onAuth: (apiKey: string, backend: string) => void;
}

const AuthPage: React.FC<AuthPageProps> = ({ onAuth }) => {
  const [apiKey, setApiKey] = useState('');
  const [backend, setBackend] = useState<'openai' | 'anthropic'>('openai');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey.trim()) {
      alert('Please enter an API key');
      return;
    }
    
    setLoading(true);
    // Simulate API key validation
    setTimeout(() => {
      onAuth(apiKey, backend);
      navigate('/dashboard');
    }, 1000);
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
              <strong>Defense-Only System</strong> | Zero-Retention Policy | Ethical Guardrails
            </p>
            <p className="text-small">
              This system is designed for security research and LLM safety testing only.
            </p>
          </div>
        </div>

        {/* Security Notice */}
        <div className="security-notice glass-panel">
          <img 
            src="/logo.png" 
            alt="" 
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
