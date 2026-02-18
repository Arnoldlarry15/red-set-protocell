import React from 'react';
import { Settings, Check } from 'lucide-react';
import { SessionConfig } from '../types';
import '../styles/Components.css';

interface AttackConfigProps {
  config: SessionConfig;
  onConfigChange: (config: SessionConfig) => void;
}

const AttackConfig: React.FC<AttackConfigProps> = ({ config, onConfigChange }) => {
  const attackDomains = [
    { id: 'injection', name: 'Prompt Injection', description: 'Command injection attacks' },
    { id: 'jailbreak', name: 'Jailbreak', description: 'Constraint breaking attempts' },
    { id: 'refusal_erosion', name: 'Refusal Erosion', description: 'Boundary testing' },
    { id: 'pii_extraction', name: 'PII Extraction', description: 'Data leakage attempts' },
    { id: 'policy_circumvention', name: 'Policy Bypass', description: 'Policy violations' },
    { id: 'cognitive_manipulation', name: 'Cognitive Attacks', description: 'Logic manipulation' },
    { id: 'context_confusion', name: 'Context Confusion', description: 'Context attacks' },
  ];

  const mutationStrategies = [
    { id: 'lexical', name: 'Lexical', description: 'Synonym replacement' },
    { id: 'encoding', name: 'Encoding', description: 'Character encoding' },
    { id: 'structural', name: 'Structural', description: 'Sentence restructuring' },
    { id: 'roleplay', name: 'Role-play', description: 'Persona injection' },
    { id: 'context', name: 'Context', description: 'Context injection' },
    { id: 'obfuscation', name: 'Obfuscation', description: 'Content obfuscation' },
  ];

  const toggleDomain = (domainId: string) => {
    const newDomains = config.selectedDomains.includes(domainId)
      ? config.selectedDomains.filter(id => id !== domainId)
      : [...config.selectedDomains, domainId];
    
    onConfigChange({ ...config, selectedDomains: newDomains });
  };

  const toggleStrategy = (strategyId: string) => {
    const newStrategies = config.selectedStrategies.includes(strategyId)
      ? config.selectedStrategies.filter(id => id !== strategyId)
      : [...config.selectedStrategies, strategyId];
    
    onConfigChange({ ...config, selectedStrategies: newStrategies });
  };

  return (
    <div className="attack-config glass-panel">
      <div className="panel-header">
        <div className="panel-header-title">
          <Settings size={20} />
          <h2>Attack Configuration</h2>
        </div>
      </div>

      <div className="config-content">
        {/* Settings */}
        <div className="config-section">
          <h3 className="config-title">Session Settings</h3>
          
          <div className="config-field">
            <label htmlFor="maxRounds">Max Rounds</label>
            <input
              id="maxRounds"
              type="number"
              value={config.maxRounds}
              onChange={(e) => onConfigChange({ ...config, maxRounds: parseInt(e.target.value) })}
              min="1"
              max="1000"
            />
          </div>

          <div className="config-field">
            <label htmlFor="maxCost">Max API Cost ($)</label>
            <input
              id="maxCost"
              type="number"
              value={config.maxApiCost}
              onChange={(e) => onConfigChange({ ...config, maxApiCost: parseFloat(e.target.value) })}
              min="0"
              step="0.1"
            />
          </div>

          <div className="config-field">
            <label htmlFor="mutationRate">Mutation Rate</label>
            <input
              id="mutationRate"
              type="range"
              value={config.mutationRate}
              onChange={(e) => onConfigChange({ ...config, mutationRate: parseFloat(e.target.value) })}
              min="0"
              max="1"
              step="0.1"
            />
            <span className="range-value">{(config.mutationRate * 100).toFixed(0)}%</span>
          </div>

          <div className="config-checkbox">
            <input
              id="haltOnCritical"
              type="checkbox"
              checked={config.haltOnCritical}
              onChange={(e) => onConfigChange({ ...config, haltOnCritical: e.target.checked })}
            />
            <label htmlFor="haltOnCritical">Halt on Critical Vulnerability</label>
          </div>

          <div className="config-field">
            <label htmlFor="semanticIntensity">
              Semantic Intensity
              <span className="field-help" title="Controls encoding transform drift: Low (minimal), Medium (balanced), High (philosophical)">ⓘ</span>
            </label>
            <select
              id="semanticIntensity"
              value={config.semanticIntensity}
              onChange={(e) => onConfigChange({ ...config, semanticIntensity: e.target.value as 'low' | 'medium' | 'high' })}
              className="config-select"
            >
              <option value="low">Low (Conservative)</option>
              <option value="medium">Medium (Balanced)</option>
              <option value="high">High (Exploratory)</option>
            </select>
            <div className="field-description">
              {config.semanticIntensity === 'low' && 'Simple, predictable transforms with minimal drift'}
              {config.semanticIntensity === 'medium' && 'Balanced semantic challenges and reasonable drift'}
              {config.semanticIntensity === 'high' && 'Deep philosophical transforms for maximum exploration'}
            </div>
          </div>
        </div>

        {/* Attack Domains */}
        <div className="config-section">
          <h3 className="config-title">Attack Domains</h3>
          <div className="selection-grid">
            {attackDomains.map((domain) => (
              <button
                key={domain.id}
                className={`selection-card ${config.selectedDomains.includes(domain.id) ? 'selected' : ''}`}
                onClick={() => toggleDomain(domain.id)}
              >
                {config.selectedDomains.includes(domain.id) && (
                  <div className="selection-check">
                    <Check size={14} />
                  </div>
                )}
                <div className="selection-name">{domain.name}</div>
                <div className="selection-description">{domain.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Mutation Strategies */}
        <div className="config-section">
          <h3 className="config-title">Mutation Strategies</h3>
          <div className="selection-grid">
            {mutationStrategies.map((strategy) => (
              <button
                key={strategy.id}
                className={`selection-card ${config.selectedStrategies.includes(strategy.id) ? 'selected' : ''}`}
                onClick={() => toggleStrategy(strategy.id)}
              >
                {config.selectedStrategies.includes(strategy.id) && (
                  <div className="selection-check">
                    <Check size={14} />
                  </div>
                )}
                <div className="selection-name">{strategy.name}</div>
                <div className="selection-description">{strategy.description}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttackConfig;
