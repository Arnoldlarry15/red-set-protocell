import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, Lock, Code, Users, Target } from 'lucide-react';
import '../styles/About.css';

const AboutPage: React.FC = () => {
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
        delayChildren: 0.1,
      },
    },
  };

  return (
    <div className="about-page">
      {/* Red Set Section */}
      <section className="about-section red-set-section">
        <motion.div
          className="section-content"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.div className="section-header" variants={fadeInUp}>
            <h1>Red Set ProtoCell</h1>
            <p className="section-tagline">
              An immune system for artificial intelligence
            </p>
          </motion.div>

          <motion.div className="philosophy-grid" variants={staggerContainer}>
            <motion.div className="philosophy-card" variants={fadeInUp}>
              <Zap className="philosophy-icon" />
              <h3>Ethical Red Teaming</h3>
              <p>
                Red teaming isn't about attacking AI for its own sake. It's about discovering vulnerabilities 
                responsibly so they can be fixed. Every attack is logged, every finding is reproducible.
              </p>
            </motion.div>

            <motion.div className="philosophy-card" variants={fadeInUp}>
              <Shield className="philosophy-icon" />
              <h3>Determinism Over Magic</h3>
              <p>
                No heuristics. No approximations. Every red-teaming run is deterministic and fully reproducible. 
                You know exactly what you're testing and why.
              </p>
            </motion.div>

            <motion.div className="philosophy-card" variants={fadeInUp}>
              <Code className="philosophy-icon" />
              <h3>Open Source Foundation</h3>
              <p>
                Transparency is security. Red Set is built on open-source principles because the safety of AI 
                benefits from public scrutiny, not proprietary control.
              </p>
            </motion.div>

            <motion.div className="philosophy-card" variants={fadeInUp}>
              <Users className="philosophy-icon" />
              <h3>Community Driven</h3>
              <p>
                From independent researchers to enterprise security teams, Red Set is built by the people who care 
                about AI safety.
              </p>
            </motion.div>
          </motion.div>

          <motion.div className="rsp-details" variants={fadeInUp}>
            <h2>How Red Set Works</h2>
            <div className="details-content">
              <div className="detail-block">
                <h4>The Sniper Agent</h4>
                <p>
                  Generates adversarial prompts using evolutionary algorithms. It learns from what works 
                  (successful attacks) and mutates those patterns to find novel vulnerabilities. Think of it as 
                  an intelligent fuzzer for language models.
                </p>
              </div>

              <div className="detail-block">
                <h4>The Spotter Agent</h4>
                <p>
                  Evaluates each response using a scientifically-grounded 3-layer taxonomy: Linguistic Safety 
                  (does the response violate content policies?), Security Exploitability (can this be weaponized?), 
                  and Cognitive Stability (does it show reasoning breaks?).
                </p>
              </div>

              <div className="detail-block">
                <h4>Evolutionary Learning</h4>
                <p>
                  Successful attack patterns feed back into the Sniper's mutation algorithms. Over time, Red Set 
                  discovers increasingly sophisticated failure modes that static test suites would miss entirely.
                </p>
              </div>

              <div className="detail-block">
                <h4>Provable Results</h4>
                <p>
                  Every attack payload is stored. Every score is justified. Every finding can be independently 
                  verified. This is not a black box—it's a scientific instrument.
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* LA Builds Section */}
      <section className="about-section la-builds-section">
        <motion.div
          className="section-content"
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.div className="section-header" variants={fadeInUp}>
            <h1>LA Builds</h1>
            <p className="section-tagline">
              Research and engineering for responsible AI
            </p>
          </motion.div>

          <motion.div className="la-builds-intro" variants={fadeInUp}>
            <p>
              LA Builds is an independent AI research and systems engineering initiative focused on building 
              the infrastructure for responsible artificial intelligence. We believe that AI safety requires 
              both technical rigor and architectural resilience.
            </p>
          </motion.div>

          <motion.div className="la-builds-grid" variants={staggerContainer}>
            <motion.div className="la-builds-card" variants={fadeInUp}>
              <Target className="la-icon" />
              <h3>AI Safety Systems</h3>
              <p>
                Designing systems that discover and mitigate AI vulnerabilities before they reach production.
              </p>
            </motion.div>

            <motion.div className="la-builds-card" variants={fadeInUp}>
              <Zap className="la-icon" />
              <h3>Architecture Resilience</h3>
              <p>
                Building infrastructure that can withstand adversarial conditions and degrade gracefully.
              </p>
            </motion.div>

            <motion.div className="la-builds-card" variants={fadeInUp}>
              <Lock className="la-icon" />
              <h3>Applied Red Teaming</h3>
              <p>
                Developing the tools and methodologies for systematic, ethical vulnerability discovery.
              </p>
            </motion.div>
          </motion.div>

          <motion.div className="founder-section" variants={fadeInUp}>
            <h2>Founder</h2>
            <div className="founder-card">
              <div className="founder-name">Larry Arnold</div>
              <div className="founder-title">AI Researcher & Systems Engineer</div>
              <div className="founder-focus">
                <p>
                  Independent researcher focused on AI safety systems, architecture design, and the practical 
                  challenges of building responsible AI infrastructure at scale.
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div className="vision-statement" variants={fadeInUp}>
            <h2>Our Vision</h2>
            <p>
              As AI systems become more powerful and more integrated into critical systems, the need for 
              rigorous, systematic red-teaming becomes non-negotiable. LA Builds exists to develop the 
              tools, methodologies, and infrastructure that make responsible AI deployment feasible.
            </p>
            <p>
              Red Set ProtoCell is our flagship project—an open-source platform that democratizes access 
              to enterprise-grade red-teaming capabilities.
            </p>
          </motion.div>
        </motion.div>
      </section>
    </div>
  );
};

export default AboutPage;
