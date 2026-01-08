import React, { useRef, useEffect } from 'react';
import { Activity, AlertTriangle, Shield } from 'lucide-react';
import { Attack } from '../types';
import '../styles/Components.css';

interface LiveFeedProps {
  attacks: Attack[];
}

const LiveFeed: React.FC<LiveFeedProps> = ({ attacks }) => {
  const feedRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (feedRef.current && attacks.length > 0) {
      feedRef.current.scrollTop = 0;
    }
  }, [attacks]);

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
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
            {attacks.map((attack) => (
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
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveFeed;
