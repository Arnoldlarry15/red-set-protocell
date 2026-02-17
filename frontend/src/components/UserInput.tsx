import React, { useState } from 'react';
import { Send, Zap } from 'lucide-react';
import { imageAssets } from '../config/imageAssets';
import '../styles/Components.css';

interface UserInputProps {
  onSubmit: (prompt: string) => void;
  disabled?: boolean;
}

const UserInput: React.FC<UserInputProps> = ({ onSubmit, disabled }) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !disabled) {
      onSubmit(prompt);
      setPrompt('');
    }
  };

  return (
    <div className="user-input glass-panel">
      <div className="panel-header">
        <div className="panel-header-title">
          <Zap size={20} />
          <h2>Custom Prompt</h2>
        </div>
        <span className="panel-subtitle">Test your own adversarial prompts</span>
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter a custom adversarial prompt to test against the target LLM..."
          className="prompt-textarea"
          rows={4}
          disabled={disabled}
        />
        <div className="input-actions">
          <div className="char-count">
            {prompt.length} characters
          </div>
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={disabled || !prompt.trim()}
          >
            <Send size={16} />
            Execute Prompt
          </button>
        </div>
      </form>
    </div>
  );
};

export default UserInput;
