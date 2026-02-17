import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Zap, Lock, Eye, AlertCircle, ArrowRight } from 'lucide-react';
import NeuralBackground from '../components/NeuralBackground';
import ArchitectureVisualization from '../components/ArchitectureVisualization';
import '../styles/LandingPage.css';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8 },
    },
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  };

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <NeuralBackground />
        
        <motion.div
          className="hero-content"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
        >
          <motion.img
            src="/logo.png"
            alt="Red Set ProtoCell Logo"
            className="hero-logo"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.1 }}
          />

          <motion.h1
            className="hero-title"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.2 }}
          >
            An Immune System for AI
          </motion.h1>

          <motion.p
            className="hero-subtitle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.4 }}
          >
            Red Set ProtoCell is an open-source AI red-teaming platform designed to detect vulnerabilities in large language models before they cause harm.
          </motion.p>

          <motion.button
            className="hero-cta"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.6 }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/early-access')}
          >
            Request Early Access
            <ArrowRight size={18} />
          </motion.button>
        </motion.div>
      </section>

      {/* Problem Section */}
      <section className="content-section problem-section">
        <motion.div
          className="section-content"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <motion.div variants={fadeInUp}>
            <h2>The Problem</h2>
            <p className="section-lead">
              AI systems are deployed faster than they are stress-tested.
            </p>
          </motion.div>

          <motion.img
            src="https://cdn.builder.io/api/v1/image/assets%2Fa5bd7a5a13174e4caedb216ad01c7f84%2F6d81d08ff4eb41b38b1b417cb5b6a021?format=webp&width=800&height=1200"
            alt="AI threat and vulnerability visualization"
            className="section-image problem-image"
            variants={fadeInUp}
          />

          <motion.div
            className="problem-grid"
            variants={staggerContainer}
          >
            <motion.div className="problem-card" variants={fadeInUp}>
              <AlertCircle size={28} className="problem-icon" />
              <h3>Unknown Vulnerabilities</h3>
              <p>Most AI risk comes from failure modes we haven't discovered yet.</p>
            </motion.div>

            <motion.div className="problem-card" variants={fadeInUp}>
              <Eye size={28} className="problem-icon" />
              <h3>Static Testing</h3>
              <p>Traditional test suites only find known issues. They don't adapt.</p>
            </motion.div>

            <motion.div className="problem-card" variants={fadeInUp}>
              <Lock size={28} className="problem-icon" />
              <h3>Real Adversaries</h3>
              <p>Attackers evolve their techniques. Your defenses shouldn't be static.</p>
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Solution Section */}
      <section className="content-section solution-section">
        <motion.div
          className="section-content"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <motion.div variants={fadeInUp}>
            <h2>The Solution</h2>
            <p className="section-lead">
              Autonomous agents that think like attackers, reason like researchers.
            </p>
          </motion.div>

          <motion.img
            src="https://cdn.builder.io/api/v1/image/assets%2Fa5bd7a5a13174e4caedb216ad01c7f84%2F644f7a3fbdfb4c10bce5a85866e36e75?format=webp&width=800&height=1200"
            alt="Sniper Spotter dual agent red teaming architecture"
            className="section-image solution-image"
            variants={fadeInUp}
          />

          <ArchitectureVisualization />

          <motion.div className="solution-details" variants={staggerContainer}>
            <motion.div className="detail-item" variants={fadeInUp}>
              <Zap className="detail-icon" />
              <h3>Dual-Agent Architecture</h3>
              <p>
                <strong>Sniper:</strong> Generates adversarial prompts using evolutionary algorithms
                <br />
                <strong>Spotter:</strong> Evaluates responses and scores failures
              </p>
            </motion.div>

            <motion.div className="detail-item" variants={fadeInUp}>
              <Shield className="detail-icon" />
              <h3>Deterministic & Reproducible</h3>
              <p>
                Every attack is logged. Every finding is verifiable. No black boxes.
              </p>
            </motion.div>

            <motion.div className="detail-item" variants={fadeInUp}>
              <Lock className="detail-icon" />
              <h3>Ethical by Design</h3>
              <p>
                Built-in guardrails. Respects rate limits, API policies, and responsible disclosure.
              </p>
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* Why It Matters Section */}
      <section className="content-section why-section">
        <motion.div
          className="section-content"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <motion.div variants={fadeInUp}>
            <h2>Why It Matters</h2>
          </motion.div>

          <motion.div className="why-grid" variants={staggerContainer}>
            <motion.div className="why-card" variants={fadeInUp}>
              <h3>Regulation is Coming</h3>
              <p>
                Enterprise AI deployments will soon require provable red-teaming infrastructure. 
                Red Set is the tool that makes compliance feasible and efficient.
              </p>
            </motion.div>

            <motion.div className="why-card" variants={fadeInUp}>
              <h3>Discover Before They Do</h3>
              <p>
                Find vulnerabilities through systematic, automated testing before real adversaries 
                or end users discover them in production.
              </p>
            </motion.div>

            <motion.div className="why-card" variants={fadeInUp}>
              <h3>Inevitable Infrastructure</h3>
              <p>
                Just as pen-testing is standard for security, autonomous red-teaming will become 
                standard for AI safety. Red Set is that infrastructure.
              </p>
            </motion.div>
          </motion.div>
        </motion.div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <motion.div
          className="cta-content"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <motion.h2 variants={fadeInUp}>Join the Red Set Network</motion.h2>
          <motion.p variants={fadeInUp}>
            Help build the immune system for AI. Request early access to shape the future of responsible red-teaming.
          </motion.p>
          <motion.button
            className="cta-button"
            variants={fadeInUp}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/early-access')}
          >
            Get Early Access
          </motion.button>
        </motion.div>
      </section>
    </div>
  );
};

export default LandingPage;
