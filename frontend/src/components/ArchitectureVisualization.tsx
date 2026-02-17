import React from 'react';
import { motion } from 'framer-motion';
import { ArrowDown, Zap, Target, CheckCircle, Repeat2, TrendingUp, FileText, Cog } from 'lucide-react';

const ArchitectureVisualization: React.FC = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
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
    hidden: { opacity: 0, scaleY: 0 },
    visible: {
      opacity: 1,
      scaleY: 1,
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

  const loopVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.6,
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
      {/* Main Vertical Flow */}
      <div className="vertical-flow">
        {/* Step 1: Beginning Prompt */}
        <motion.div className="flow-step" variants={itemVariants}>
          <div className="flow-box prompt-box">
            <Target size={28} className="flow-icon" />
            <h3>Beginning Prompt</h3>
            <p>Define attack domain</p>
          </div>
        </motion.div>

        <motion.div className="flow-arrow" variants={arrowVariants}>
          <ArrowDown size={24} />
        </motion.div>

        {/* Step 2: Target Model */}
        <motion.div className="flow-step" variants={itemVariants}>
          <div className="flow-box target-box">
            <div className="flow-icon-text">🎯</div>
            <h3>Target Model</h3>
            <p>Initial attack surface</p>
          </div>
        </motion.div>

        <motion.div className="flow-arrow" variants={arrowVariants}>
          <ArrowDown size={24} />
        </motion.div>

        {/* Step 3: Sniper Generates Probes */}
        <motion.div className="flow-step" variants={itemVariants}>
          <motion.div className="flow-box sniper-box" variants={pulseVariants} animate="pulse">
            <Zap size={28} className="flow-icon" />
            <h3>Sniper Generates</h3>
            <p>Adversarial probes</p>
            <div className="flow-detail">Evolutionary algorithms</div>
          </motion.div>
        </motion.div>

        <motion.div className="flow-arrow" variants={arrowVariants}>
          <ArrowDown size={24} />
        </motion.div>

        {/* Step 4: Spotter Evaluates */}
        <motion.div className="flow-step" variants={itemVariants}>
          <motion.div className="flow-box spotter-box" variants={pulseVariants} animate="pulse">
            <CheckCircle size={28} className="flow-icon" />
            <h3>Spotter Evaluates</h3>
            <p>Assigns risk score</p>
            <div className="flow-detail">3-layer taxonomy analysis</div>
          </motion.div>
        </motion.div>

        <motion.div className="flow-arrow" variants={arrowVariants}>
          <ArrowDown size={24} />
        </motion.div>

        {/* Step 5: Mutation Engine */}
        <motion.div className="flow-step" variants={itemVariants}>
          <motion.div className="flow-box mutation-box" variants={pulseVariants} animate="pulse">
            <Cog size={28} className="flow-icon" />
            <h3>Mutation Engine</h3>
            <p>Modify probe strategy</p>
            <div className="flow-detail">Adaptive refinement</div>
          </motion.div>
        </motion.div>

        <motion.div className="flow-arrow" variants={arrowVariants}>
          <ArrowDown size={24} />
        </motion.div>

        {/* Step 6: Sniper Redeploys */}
        <motion.div className="flow-step" variants={itemVariants}>
          <motion.div className="flow-box sniper-redeploy-box" variants={pulseVariants} animate="pulse">
            <Zap size={28} className="flow-icon" />
            <h3>Sniper Redeploys</h3>
            <p>Refined probes v2+</p>
            <div className="flow-detail">Loop with mutations</div>
          </motion.div>
        </motion.div>

        {/* Loop Indicator */}
        <motion.div className="loop-indicator" variants={loopVariants}>
          <Repeat2 size={20} />
          <span>Repeat Cycle</span>
        </motion.div>

        <motion.div className="flow-arrow" variants={arrowVariants}>
          <ArrowDown size={24} />
        </motion.div>

        {/* Step 7: Convergence */}
        <motion.div className="flow-step" variants={itemVariants}>
          <div className="flow-box convergence-box">
            <TrendingUp size={28} className="flow-icon" />
            <h3>Convergence</h3>
            <p>Exploit or safety boundary</p>
            <div className="flow-detail">Evolutionary pressure drives discovery</div>
          </div>
        </motion.div>

        <motion.div className="flow-arrow" variants={arrowVariants}>
          <ArrowDown size={24} />
        </motion.div>

        {/* Step 8: Final Report */}
        <motion.div className="flow-step" variants={itemVariants}>
          <div className="flow-box report-box">
            <FileText size={28} className="flow-icon" />
            <h3>Final Report</h3>
            <p>Risk distribution & findings</p>
            <div className="flow-detail">Actionable vulnerabilities</div>
          </div>
        </motion.div>
      </div>

      {/* Evolutionary Nature Callout */}
      <motion.div className="evolution-callout" variants={itemVariants}>
        <h4>The Evolution Loop</h4>
        <p>
          Red Set doesn't just attack once—it evolves. Each iteration learns from failures,
          mutates its strategies, and tries again. Like natural selection for adversarial prompts,
          the system converges toward real exploits over time.
        </p>
      </motion.div>
    </motion.div>
  );
};

export default ArchitectureVisualization;
