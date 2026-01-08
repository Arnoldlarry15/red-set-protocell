import React from 'react';
import { DollarSign, AlertCircle } from 'lucide-react';
import '../styles/Components.css';

interface CostTrackerProps {
  currentCost: number;
  maxCost: number;
  status: string;
}

const CostTracker: React.FC<CostTrackerProps> = ({ currentCost, maxCost, status }) => {
  const percentage = (currentCost / maxCost) * 100;
  const isNearLimit = percentage >= 80;
  const isAtLimit = percentage >= 100;

  return (
    <div className={`cost-tracker glass-panel ${isAtLimit ? 'cost-limit-reached' : ''}`}>
      <div className="panel-header">
        <div className="panel-header-title">
          <DollarSign size={20} />
          <h2>API Cost Tracker</h2>
        </div>
        {isNearLimit && (
          <AlertCircle size={18} className="warning-icon" />
        )}
      </div>

      <div className="cost-content">
        <div className="cost-display">
          <div className="cost-current">
            ${currentCost.toFixed(2)}
          </div>
          <div className="cost-max">
            / ${maxCost.toFixed(2)}
          </div>
        </div>

        <div className="cost-bar-container">
          <div 
            className={`cost-bar-fill ${isNearLimit ? 'cost-warning' : ''} ${isAtLimit ? 'cost-critical' : ''}`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          >
            <div className="cost-bar-shine"></div>
          </div>
        </div>

        <div className="cost-details">
          <div className="cost-stat">
            <span className="cost-label">Used</span>
            <span className="cost-value">{percentage.toFixed(1)}%</span>
          </div>
          <div className="cost-stat">
            <span className="cost-label">Remaining</span>
            <span className="cost-value">${(maxCost - currentCost).toFixed(2)}</span>
          </div>
        </div>

        {isAtLimit && (
          <div className="cost-alert">
            <AlertCircle size={16} />
            <span>Cost limit reached - session halted</span>
          </div>
        )}
        {isNearLimit && !isAtLimit && (
          <div className="cost-warning-message">
            <AlertCircle size={16} />
            <span>Approaching cost limit</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default CostTracker;
