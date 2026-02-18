import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Activity, Zap, Lock, Github, ArrowRight } from 'lucide-react';
import '../styles/Landing.css';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <header className="hero">
        <div className="hero-content">
          <div className="logo-section">
            <Shield className="logo-icon" size={48} />
            <h1 className="logo-text">Red Set ProtoCell</h1>
          </div>
          <p className="tagline">
            Advanced AI Safety Platform for LLM Red-Teaming
          </p>
          <p className="description">
            An open-source dual-agent system using Sniper/Spotter red-teaming to audit and secure large language models. Scalable, transparent, and built for advanced AI risk monitoring.
          </p>
          <div className="cta-buttons">
            <button 
              className="cta-primary" 
              onClick={() => navigate('/auth')}
            >
              Get Started <ArrowRight size={20} />
            </button>
            <a 
              href="https://github.com/Arnoldlarry15/red-set-protocell" 
              target="_blank" 
              rel="noopener noreferrer"
              className="cta-secondary"
            >
              <Github size={20} /> View on GitHub
            </a>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <section className="features">
        <h2>Why Red Set ProtoCell?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <Activity className="feature-icon" size={32} />
            <h3>Dual-Agent Architecture</h3>
            <p>Sniper generates adversarial attacks while Spotter evaluates their effectiveness, creating a robust feedback loop for continuous improvement.</p>
          </div>
          <div className="feature-card">
            <Zap className="feature-icon" size={32} />
            <h3>Evolutionary Mutations</h3>
            <p>Sophisticated mutation engine with 15+ strategies including behavioral bias, archetype guidance, and intelligent domain selection.</p>
          </div>
          <div className="feature-card">
            <Lock className="feature-icon" size={32} />
            <h3>Deterministic & Auditable</h3>
            <p>Complete reproducibility with cryptographic audit trails, ensuring transparent and verifiable security testing.</p>
          </div>
          <div className="feature-card">
            <Shield className="feature-icon" size={32} />
            <h3>Multi-Backend Support</h3>
            <p>Test against OpenAI, Anthropic, OpenRouter, and custom backends with unified configuration.</p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats">
        <div className="stats-grid">
          <div className="stat">
            <h3>15+</h3>
            <p>Mutation Strategies</p>
          </div>
          <div className="stat">
            <h3>78%+</h3>
            <p>Test Coverage</p>
          </div>
          <div className="stat">
            <h3>100%</h3>
            <p>Open Source</p>
          </div>
          <div className="stat">
            <h3>3</h3>
            <p>Platform Support</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <p>© 2026 Red Set ProtoCell. Released under MIT License.</p>
        <div className="footer-links">
          <a href="https://github.com/Arnoldlarry15/red-set-protocell" target="_blank" rel="noopener noreferrer">
            Documentation
          </a>
          <a href="https://github.com/Arnoldlarry15/red-set-protocell/issues" target="_blank" rel="noopener noreferrer">
            Report Issue
          </a>
          <button onClick={() => navigate('/auth')} className="footer-cta">
            Launch App
          </button>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
