import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Shield, Zap, Target } from 'lucide-react';
import axios from 'axios';
import { User } from '../types';
import { imageAssets } from '../config/imageAssets';
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
      const response = await axios.post(`${API_BASE_URL}/auth/validate-llm-key`, {
        api_key: apiKey,
        backend: backend
      });
      
      if (response.data.valid) {
        const demoUser: User = {
          username: 'demo_user',
          email: 'demo@rsp.com',
          role: 'admin',
        };
        onAuth(apiKey, backend, demoUser);
        setLoading(false);
        navigate('/admin');
      }
    } catch (err) {
      const axiosError = err as { response?: { data?: { detail?: string } }; message?: string };
      setError(axiosError.response?.data?.detail || axiosError.message || 'Failed to validate API key');
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      {/* Background hero section */}
      <div className="auth-background">
        <div className="hero-image-overlay">
          <img 
            src={imageAssets.heroes.redSetProtocellHero}
            alt="Red Set ProtoCell Architecture"
            className="hero-image"
            loading="lazy"
          />
          <div className="hero-gradient-overlay"></div>
        </div>
        <div className="grid-pattern"></div>
      </div>
      
      {/* Main content area */}
      <div className="auth-content">
        {/* Left side - Hero section with component showcase */}
        <div className="auth-left-panel">
          <div className="hero-header">
            <h1 className="hero-title">
              <span className="text-gradient">RED SET</span>
              <br />
              <span className="text-gradient-secondary">PROTOCELL</span>
            </h1>
            <p className="hero-subtitle">
              Autonomous AI Red Teaming & Ethical Guardrails
            </p>
          </div>

          {/* Component showcase grid */}
          <div className="components-showcase">
            {/* EGG Component */}
            <div className="showcase-card egg-card">
              <div className="showcase-image">
                <img 
                  src={imageAssets.heroes.eggHero}
                  alt="EGG - Ethical Guardrail Governor"
                  loading="lazy"
                />
              </div>
              <div className="showcase-info">
                <Shield size={16} className="showcase-icon" />
                <div>
                  <h4>EGG</h4>
                  <p>Ethical Guardrails</p>
                </div>
              </div>
            </div>

            {/* Sniper/Spotter Component */}
            <div className="showcase-card sniper-card">
              <div className="showcase-image">
                <img 
                  src={imageAssets.heroes.sniperSpotterHero}
                  alt="Sniper/Spotter - Dual Agent Cell"
                  loading="lazy"
                />
              </div>
              <div className="showcase-info">
                <Target size={16} className="showcase-icon" />
                <div>
                  <h4>Red Set</h4>
                  <p>Precision Targeting</p>
                </div>
              </div>
            </div>

            {/* Feedback Loop Component */}
            <div className="showcase-card feedback-card">
              <div className="showcase-image">
                <img 
                  src={imageAssets.heroes.feedbackLoop}
                  alt="Evolving Feedback Loop"
                  loading="lazy"
                />
              </div>
              <div className="showcase-info">
                <Zap size={16} className="showcase-icon" />
                <div>
                  <h4>Feedback Loop</h4>
                  <p>Continuous Evolution</p>
                </div>
              </div>
            </div>
          </div>

          {/* Key features list */}
          <div className="features-list">
            <div className="feature-item">
              <div className="feature-dot"></div>
              <span>Automated Red Teaming</span>
            </div>
            <div className="feature-item">
              <div className="feature-dot"></div>
              <span>Ethical Oversight &amp; Compliance</span>
            </div>
            <div className="feature-item">
              <div className="feature-dot"></div>
              <span>Intelligent Vulnerability Discovery</span>
            </div>
          </div>
        </div>

        {/* Right side - Authentication form */}
        <div className="auth-right-panel">
          <div className="auth-card glass-panel-dark">
            {/* Logo Section */}
            <div className="logo-section">
              <div className="logo-placeholder">
                <Shield size={60} className="logo-icon" />
              </div>
              <h2 className="form-title">Begin Red Teaming</h2>
              <p className="form-subtitle">
                Authenticate with your LLM credentials
              </p>
            </div>

            {/* Auth Form */}
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="backend">
                  <span className="label-text">LLM Backend</span>
                  <span className="label-badge">required</span>
                </label>
                <select
                  id="backend"
                  value={backend}
                  onChange={(e) => setBackend(e.target.value as 'openai' | 'anthropic')}
                  className="form-control"
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic Claude</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="apiKey">
                  <span className="label-text">API Key</span>
                  <span className="label-badge">required</span>
                </label>
                <div className="input-with-icon">
                  <Lock size={18} className="input-icon" />
                  <input
                    id="apiKey"
                    type="password"
                    placeholder={backend === 'openai' ? 'sk-...' : 'sk-ant-...'}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="form-control with-icon"
                    autoComplete="off"
                  />
                </div>
                <p className="input-help-text">
                  Your API key is stored locally and never transmitted to third parties.
                </p>
              </div>

              {error && (
                <div className="error-message" role="alert">
                  <svg className="error-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <span>{error}</span>
                </div>
              )}

              <button 
                type="submit" 
                className="btn btn-primary auth-button"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="loading-spinner"></span>
                    Authenticating...
                  </>
                ) : (
                  'Begin Red Teaming'
                )}
              </button>

              <div className="form-divider">
                <span>Security First</span>
              </div>

              <div className="auth-checklist">
                <div className="checklist-item">
                  <svg className="check-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Local-only key storage</span>
                </div>
                <div className="checklist-item">
                  <svg className="check-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Ethical guardrails enforced</span>
                </div>
                <div className="checklist-item">
                  <svg className="check-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Continuous compliance checks</span>
                </div>
              </div>
            </form>
          </div>

          {/* Security notice */}
          <div className="security-notice glass-panel">
            <Shield size={18} className="notice-icon" />
            <div className="notice-content">
              <strong>Autonomous AI Red Teaming</strong>
              <p>
                This system discovers vulnerabilities with mandatory ethical guardrails 
                and full compliance oversight.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Animated accent elements */}
      <div className="accent-orb accent-orb-1"></div>
      <div className="accent-orb accent-orb-2"></div>
    </div>
  );
};

export default AuthPage;
