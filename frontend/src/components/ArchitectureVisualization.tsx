import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Zap, Target, CheckCircle } from 'lucide-react';

const ArchitectureVisualization: React.FC = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.3,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
      },
    },
  };

  const arrowVariants = {
    hidden: { opacity: 0, scaleX: 0 },
    visible: {
      opacity: 1,
      scaleX: 1,
      transition: {
        duration: 0.5,
      },
    },
  };

  const pulseVariants = {
    pulse: {
      boxShadow: [
        '0 0 20px rgba(239, 68, 68, 0.3)',
        '0 0 40px rgba(239, 68, 68, 0.6)',
        '0 0 20px rgba(239, 68, 68, 0.3)',
      ],
      transition: {
        duration: 2,
        repeat: Infinity,
      },
    },
  };

  return (
    <motion.div
      className="architecture-container"
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true }}
    >
      <div className="architecture-flow">
        {/* User Prompt */}
        <motion.div className="arch-step" variants={itemVariants}>
          <div className="arch-box">
            <Target size={24} className="arch-icon" />
            <h3>User Prompt</h3>
            <p>Define attack domain</p>
          </div>
        </motion.div>

        {/* Arrow */}
        <motion.div className="arch-arrow" variants={arrowVariants}>
          <ArrowRight size={20} />
        </motion.div>

        {/* Sniper Agent */}
        <motion.div className="arch-step" variants={itemVariants}>
          <motion.div className="arch-box sniper-box" variants={pulseVariants} animate="pulse">
            <Zap size={24} className="arch-icon" />
            <h3>Sniper Agent</h3>
            <p>Generate adversarial prompts</p>
            <div className="arch-detail">Evolutionary algorithms & mutations</div>
          </motion.div>
        </motion.div>

        {/* Arrow */}
        <motion.div className="arch-arrow" variants={arrowVariants}>
          <ArrowRight size={20} />
        </motion.div>

        {/* Target LLM */}
        <motion.div className="arch-step" variants={itemVariants}>
          <div className="arch-box target-box">
            <div className="arch-icon-text">LLM</div>
            <h3>Target Model</h3>
            <p>Execute attack</p>
          </div>
        </motion.div>

        {/* Arrow */}
        <motion.div className="arch-arrow" variants={arrowVariants}>
          <ArrowRight size={20} />
        </motion.div>

        {/* Spotter Agent */}
        <motion.div className="arch-step" variants={itemVariants}>
          <motion.div className="arch-box spotter-box" variants={pulseVariants} animate="pulse">
            <CheckCircle size={24} className="arch-icon" />
            <h3>Spotter Agent</h3>
            <p>Evaluate & score failures</p>
            <div className="arch-detail">3-layer taxonomy analysis</div>
          </motion.div>
        </motion.div>

        {/* Arrow */}
        <motion.div className="arch-arrow" variants={arrowVariants}>
          <ArrowRight size={20} />
        </motion.div>

        {/* Risk Report */}
        <motion.div className="arch-step" variants={itemVariants}>
          <div className="arch-box report-box">
            <div className="arch-icon-text">📊</div>
            <h3>Risk Report</h3>
            <p>Actionable findings</p>
          </div>
        </motion.div>
      </div>

      {/* Feedback Loop */}
      <motion.div className="feedback-loop" variants={itemVariants}>
        <div className="loop-label">Evolutionary Feedback</div>
        <svg viewBox="0 0 200 80" className="loop-svg">
          <motion.path
            d="M 10 40 Q 100 -10 190 40"
            stroke="rgba(239, 68, 68, 0.3)"
            strokeWidth="2"
            fill="none"
            strokeDasharray="200"
            initial={{ strokeDashoffset: 200 }}
            animate={{ strokeDashoffset: 0 }}
            transition={{ duration: 3, repeat: Infinity }}
          />
          <motion.path
            d="M 10 40 Q 100 -10 190 40"
            stroke="rgba(239, 68, 68, 0.6)"
            strokeWidth="1"
            fill="none"
            opacity="0.5"
            strokeDasharray="200"
            initial={{ strokeDashoffset: 200 }}
            animate={{ strokeDashoffset: 0 }}
            transition={{ duration: 3, repeat: Infinity, delay: 0.2 }}
          />
        </svg>
      </motion.div>
    </motion.div>
  );
};

export default ArchitectureVisualization;
