import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';
import NeuralBackground from '../components/NeuralBackground';
import { API_BASE_URL } from '../utils/config';
import '../styles/EarlyAccess.css';

type Role = 'developer' | 'researcher' | 'security' | 'investor' | 'other' | '';

const EarlyAccessPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<Role>('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email.trim()) {
      setError('Please enter a valid email');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`${API_BASE_URL}/early-access`, {
        email: email.trim(),
        role: role || null,
      });
      setSubmitted(true);
      setEmail('');
      setRole('');

      // Reset submitted state after 5 seconds
      setTimeout(() => {
        setSubmitted(false);
      }, 5000);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === 'string' ? detail : 'Something went wrong. Please try again.');
      } else {
        setError('Something went wrong. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6 },
    },
  };

  return (
    <div className="early-access-page">
      <NeuralBackground />

      <motion.div
        className="early-access-container"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="early-access-card" variants={itemVariants}>
          {/* Terminal Header */}
          <div className="terminal-header">
            <div className="terminal-dots">
              <span className="dot red"></span>
              <span className="dot yellow"></span>
              <span className="dot green"></span>
            </div>
            <div className="terminal-title">red_set_network.sh</div>
          </div>

          {/* Content */}
          <div className="early-access-content">
            <motion.div variants={itemVariants}>
              <h1 className="early-access-title">
                Help Build the Immune System for AI
              </h1>
              <p className="early-access-subtitle">
                We're onboarding early researchers, developers, and AI safety advocates.
              </p>
            </motion.div>

            {submitted ? (
              <motion.div
                className="success-state"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <CheckCircle size={48} className="success-icon" />
                <h2>You're on the list!</h2>
                <p>
                  Welcome to the Red Set network. We'll be in touch soon with onboarding details and 
                  early access to the platform.
                </p>
              </motion.div>
            ) : (
              <motion.form onSubmit={handleSubmit} className="early-access-form" variants={itemVariants}>
                <div className="form-group">
                  <label htmlFor="email" className="terminal-prompt">
                    {"$ red_set_network --email "}
                  </label>
                  <div className="input-wrapper">
                    <input
                      id="email"
                      type="email"
                      placeholder="your@email.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="terminal-input"
                      disabled={loading}
                    />
                    <span className="cursor">_</span>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="role" className="terminal-prompt">
                    {"$ --role "}
                  </label>
                  <select
                    id="role"
                    value={role}
                    onChange={(e) => setRole(e.target.value as Role)}
                    className="terminal-select"
                    disabled={loading}
                  >
                    <option value="">Select your role (optional)</option>
                    <option value="developer">Developer</option>
                    <option value="researcher">Researcher</option>
                    <option value="security">Security Professional</option>
                    <option value="investor">Investor / Business</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {error && (
                  <motion.div
                    className="error-message"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <AlertCircle size={16} />
                    {error}
                  </motion.div>
                )}

                <button
                  type="submit"
                  className="terminal-button"
                  disabled={loading || !email}
                >
                  {loading ? (
                    <>
                      <span className="loading-spinner">⟳</span>
                      Submitting...
                    </>
                  ) : (
                    <>
                      Enter the network
                      <ArrowRight size={18} />
                    </>
                  )}
                </button>
              </motion.form>
            )}

            <motion.div className="form-notice" variants={itemVariants}>
              <p>Your email is safe with us. No spam. Pure signal.</p>
            </motion.div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default EarlyAccessPage;
