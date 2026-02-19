import React, { useRef, useEffect, useState } from 'react';
import { Activity, AlertTriangle, Shield, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { safeAsync } from '../utils/async';
import { Attack } from '../types';
import '../styles/Components.css';

interface LiveFeedProps {
  attacks: Attack[];
}

const LiveFeed: React.FC<LiveFeedProps> = ({ attacks }) => {
  const feedRef = useRef<HTMLDivElement>(null);
  const [expandedAttacks, setExpandedAttacks] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    if (feedRef.current && attacks.length > 0) {
      feedRef.current.scrollTop = 0;
    }
  }, [attacks]);

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const toggleExpanded = (attackId: string) => {
    setExpandedAttacks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(attackId)) {
        newSet.delete(attackId);
      } else {
        newSet.add(attackId);
      }
      return newSet;
    });
  };

  const redactSensitiveData = (text: string): string => {
    // Redact known API key patterns
    let redacted = text.replace(/sk-[A-Za-z0-9]{48}/g, '[REDACTED_OPENAI_KEY]');
    redacted = redacted.replace(/sk-ant-[A-Za-z0-9-]{95}/g, '[REDACTED_ANTHROPIC_KEY]');
    // Redact generic long alphanumeric strings that look like keys (40+ chars)
    redacted = redacted.replace(/\b[A-Za-z0-9]{40,}\b/g, '[REDACTED_KEY]');
    // Redact email addresses
    redacted = redacted.replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, '[REDACTED_EMAIL]');
    // Redact phone numbers
    redacted = redacted.replace(/\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/g, '[REDACTED_PHONE]');
    // Redact credit card patterns
    redacted = redacted.replace(/\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g, '[REDACTED_CARD]');
    // Redact SSN patterns
    redacted = redacted.replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[REDACTED_SSN]');
    return redacted;
  };

  const copyRedacted = (attack: Attack) => {
    const redactedContent = `Round ${attack.round} - ${formatTime(attack.timestamp)}
Domain: ${attack.domain}
Strategy: ${attack.strategy}
Mutation: ${attack.mutation}
Severity: ${attack.severity}
Blocked: ${attack.blocked ? 'Yes' : 'No'}

Prompt (Redacted):
${redactSensitiveData(attack.prompt)}

Response (Redacted):
${attack.blocked ? '[BLOCKED BY SYSTEM]' : redactSensitiveData(attack.response)}

Scores:
- Global: ${(attack.score.global * 100).toFixed(1)}%
- L1 (Linguistic): ${(attack.score.l1_linguistic * 100).toFixed(1)}%
- L2 (Security): ${(attack.score.l2_security * 100).toFixed(1)}%
- L3 (Cognitive): ${(attack.score.l3_cognitive * 100).toFixed(1)}%`;

    safeAsync(async () => {
      await navigator.clipboard.writeText(redactedContent);
      setCopiedId(attack.id);
      setTimeout(() => setCopiedId(null), 2000);
    });
  };

  // Create a render function for attack cards that can be used in both regular and virtualized lists
  const renderAttackCard = (attack: Attack) => {
    const isExpanded = expandedAttacks.has(attack.id);
    const isCopied = copiedId === attack.id;
    
    return (
      <div 
        key={attack.id} 
        className={`attack-card animate-slide-in ${attack.blocked ? 'attack-blocked' : ''}`}
      >
        <div className="attack-header">
          <div className="attack-meta">
            <span className="attack-round">Round {attack.round}</span>
            <span className="attack-time">{formatTime(attack.timestamp)}</span>
          </div>
          <div className="attack-badges">
            <span className={`severity-badge severity-${attack.severity}`}>
              {attack.severity}
            </span>
            {attack.blocked && (
              <span className="blocked-badge">
                <AlertTriangle size={14} /> BLOCKED
              </span>
            )}
          </div>
        </div>

        <div className="attack-details">
          <div className="attack-tags">
            <span className="tag tag-domain">{attack.domain}</span>
            <span className="tag tag-strategy">{attack.strategy}</span>
            <span className="tag tag-mutation">{attack.mutation}</span>
          </div>

          <div className="attack-scores">
            <div className="score-item">
              <span className="score-label">Global</span>
              <div className="score-bar">
                <div 
                  className="score-fill"
                  style={{ width: `${attack.score.global * 100}%` }}
                ></div>
              </div>
              <span className="score-value">{(attack.score.global * 100).toFixed(1)}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">L1</span>
              <div className="score-bar score-bar-small">
                <div 
                  className="score-fill"
                  style={{ width: `${attack.score.l1_linguistic * 100}%` }}
                ></div>
              </div>
              <span className="score-value">{(attack.score.l1_linguistic * 100).toFixed(0)}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">L2</span>
              <div className="score-bar score-bar-small">
                <div 
                  className="score-fill"
                  style={{ width: `${attack.score.l2_security * 100}%` }}
                ></div>
              </div>
              <span className="score-value">{(attack.score.l2_security * 100).toFixed(0)}%</span>
            </div>
            <div className="score-item">
              <span className="score-label">L3</span>
              <div className="score-bar score-bar-small">
                <div 
                  className="score-fill"
                  style={{ width: `${attack.score.l3_cognitive * 100}%` }}
                ></div>
              </div>
              <span className="score-value">{(attack.score.l3_cognitive * 100).toFixed(0)}%</span>
            </div>
          </div>

          {isExpanded && (
            <div className="attack-content">
              <div className="content-section">
                <strong>Prompt:</strong>
                <p className="attack-prompt">{attack.prompt}</p>
              </div>
              {!attack.blocked && (
                <div className="content-section">
                  <strong>Response:</strong>
                  <p className="attack-response">{attack.response}</p>
                </div>
              )}
            </div>
          )}

          <div className="attack-actions">
            <button 
              className="btn btn-sm btn-secondary"
              onClick={() => toggleExpanded(attack.id)}
              aria-label={isExpanded ? "Collapse details" : "Expand details"}
            >
              {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              {isExpanded ? 'Hide Details' : 'Show Details'}
            </button>
            <button 
              className="btn btn-sm btn-secondary"
              onClick={() => copyRedacted(attack)}
              aria-label="Copy redacted content"
            >
              {isCopied ? <Check size={16} /> : <Copy size={16} />}
              {isCopied ? 'Copied!' : 'Copy (Redacted)'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="live-feed glass-panel">
      <div className="panel-header">
        <div className="panel-header-title">
          <Activity size={20} />
          <h2>Live Attack Feed</h2>
        </div>
        <div className="badge">{attacks.length} attacks</div>
      </div>

      <div className="feed-container" ref={feedRef}>
        {attacks.length === 0 ? (
          <div className="empty-state">
            <Shield size={48} className="empty-icon" />
            <p>No attacks yet</p>
            <p className="empty-subtitle">Start the red teaming session to see live attacks</p>
          </div>
        ) : (
          <div className="feed-list">
            {attacks.map((attack) => renderAttackCard(attack))}
          </div>
        )}
      </div>
    </div>
  );
};

export default React.memo(LiveFeed);
