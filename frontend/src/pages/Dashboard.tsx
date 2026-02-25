import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Play, Pause, Square } from 'lucide-react';
import axios from 'axios';
import LiveFeed from '../components/LiveFeed';
import MetricsPanel from '../components/MetricsPanel';
import AttackConfig from '../components/AttackConfig';
import UserInput from '../components/UserInput';
import CostTracker from '../components/CostTracker';
import { useSessionStream } from '../hooks/useSessionStream';
import { safeAsync } from '../utils/async';
import '../styles/Dashboard.css';
import { Attack, SessionStats, SessionConfig, WebSocketMessage, OutgoingWebSocketMessage } from '../types';

interface DashboardProps {
  apiKey: string;
  backend: string;
}

// Get API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const WS_URL = API_BASE_URL.replace(/^http/, 'ws') + '/ws';

const Dashboard: React.FC<DashboardProps> = ({ apiKey, backend }) => {
  const [attacks, setAttacks] = useState<Attack[]>([]);
  const [sessionStats, setSessionStats] = useState<SessionStats>({
    sessionId: '',
    totalRounds: 100,
    completedRounds: 0,
    averageScore: 0,
    blockedCount: 0,
    apiCost: 0,
    startTime: new Date().toISOString(),
    status: 'idle',
  });

  const [config, setConfig] = useState<SessionConfig>({
    maxRounds: 100,
    maxApiCost: 10.0,
    haltOnCritical: true,
    backend: backend as 'openai' | 'anthropic' | 'openrouter',
    model:
      backend === 'openai'
        ? 'gpt-4o-mini'
        : backend === 'anthropic'
          ? 'claude-3-opus-20240229'
          : 'openai/gpt-4o-mini',
    mutationRate: 0.7,
    semanticIntensity: 'medium',  // NEW: Default to balanced semantic intensity
    selectedDomains: ['injection', 'jailbreak', 'refusal_erosion'],
    selectedStrategies: ['lexical', 'encoding', 'structural'],
  });

  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [pendingExecutionSessionId, setPendingExecutionSessionId] = useState<string | null>(null);
  
  // Refs to track session state
  const wsConnectionRef = useRef<{
    isConnected: boolean;
    disconnect: () => void;
    sendMessage: (message: OutgoingWebSocketMessage) => boolean;
  } | null>(null);

  // Helper to calculate severity from score
  const getSeverity = (score: number): Attack['severity'] => {
    if (score < 0.2) return 'safe';
    if (score < 0.4) return 'low';
    if (score < 0.6) return 'medium';
    if (score < 0.8) return 'high';
    return 'critical';
  };

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    console.log('[Dashboard] WebSocket message received:', message.type);
    
    if (message.type === 'attack') {
      const attackData = message.data as {
        id: string;
        timestamp: string;
        round: number;
        prompt: string;
        response: string;
        domain: string;
        strategy: string;
        mutation: string;
        score: {
          global: number;
          l1_linguistic: number;
          l2_security: number;
          l3_cognitive: number;
        };
        severity: Attack['severity'];
        blocked: boolean;
      };
      const newAttack: Attack = {
        id: attackData.id,
        timestamp: attackData.timestamp,
        round: attackData.round,
        prompt: attackData.prompt,
        response: attackData.response,
        domain: attackData.domain,
        strategy: attackData.strategy,
        mutation: attackData.mutation,
        score: {
          global: attackData.score.global,
          l1_linguistic: attackData.score.l1_linguistic,
          l2_security: attackData.score.l2_security,
          l3_cognitive: attackData.score.l3_cognitive,
        },
        severity: attackData.severity,
        blocked: attackData.blocked,
      };
      setAttacks(prevAttacks => [newAttack, ...prevAttacks].slice(0, 100));
    } else if (message.type === 'stats') {
      const statsData = message.data as {
        session_id?: string;
        completed_rounds: number;
        total_rounds: number;
        average_score: number;
        blocked_count: number;
        api_cost: number;
        status: SessionStats['status'];
      };
      setSessionStats(prev => ({
        ...prev,
        sessionId: statsData.session_id || prev.sessionId,
        completedRounds: statsData.completed_rounds,
        totalRounds: statsData.total_rounds,
        averageScore: statsData.average_score,
        blockedCount: statsData.blocked_count,
        apiCost: statsData.api_cost,
        status: statsData.status,
      }));
    } else if (message.type === 'status') {
      const statusData = message.data as {
        status: SessionStats['status'];
      };
      setSessionStats(prev => ({
        ...prev,
        status: statusData.status,
      }));
    } else if (message.type === 'error') {
      const errorData = message.data as {
        message?: string;
      };
      setError(errorData.message || 'An error occurred');
    }
  }, []);

  // WebSocket connection (only when session is active)
  const wsConnection = useSessionStream({
    url: WS_URL,
    sessionId: sessionId,
    onMessage: handleWebSocketMessage,
    onError: (error) => {
      console.error('[Dashboard] WebSocket error:', error);
      setError(error.message);
    },
  });

  // Store connection reference
  useEffect(() => {
    wsConnectionRef.current = wsConnection;
  }, [wsConnection]);

  useEffect(() => {
    if (!pendingExecutionSessionId || !wsConnection.isConnected) {
      return;
    }

    let cancelled = false;

    const executeSession = async () => {
      try {
        await axios.post(`${API_BASE_URL}/session/${pendingExecutionSessionId}/execute`);
        if (!cancelled) {
          console.log('[Dashboard] Session execution started');
          setPendingExecutionSessionId(null);
          setIsConnecting(false);
        }
      } catch (error) {
        if (cancelled) {
          return;
        }
        console.error('[Dashboard] Error starting session execution:', error);
        const axiosError = error as { response?: { data?: { detail?: string } }; message?: string };
        setError(axiosError.response?.data?.detail || axiosError.message || 'Failed to start session');
        setSessionStats(prev => ({ ...prev, status: 'idle' }));
        setPendingExecutionSessionId(null);
        setIsConnecting(false);
      }
    };

    void executeSession();

    return () => {
      cancelled = true;
    };
  }, [pendingExecutionSessionId, wsConnection.isConnected]);

  // Start a new session
  const handleStart = useCallback(async () => {
    if (isConnecting) return;
    
    setIsConnecting(true);
    setError(null);
    
    try {
      console.log('[Dashboard] Starting session with config:', config);
      
      // Step 1: Create session
      const sessionResponse = await axios.post(`${API_BASE_URL}/session/start`, {
        backend: config.backend,
        api_key: apiKey,
        model: config.model,
        max_rounds: config.maxRounds,
        max_api_cost: config.maxApiCost,
        halt_on_critical: config.haltOnCritical,
        mutation_rate: config.mutationRate,
        selected_domains: config.selectedDomains,
        selected_strategies: config.selectedStrategies,
      });

      const newSessionId = sessionResponse.data.session_id;
      console.log('[Dashboard] Session created:', newSessionId);
      
      // Update session ID - this will trigger WebSocket connection
      setSessionId(newSessionId);
      setSessionStats(prev => ({
        ...prev,
        sessionId: newSessionId,
        status: 'running',
        startTime: new Date().toISOString(),
      }));

      // Step 2: defer execution until WebSocket is connected
      setPendingExecutionSessionId(newSessionId);
      
    } catch (error) {
      console.error('[Dashboard] Error starting session:', error);
      const axiosError = error as { response?: { data?: { detail?: string } }; message?: string };
      setError(axiosError.response?.data?.detail || axiosError.message || 'Failed to start session');
      setSessionStats(prev => ({ ...prev, status: 'idle' }));
      setIsConnecting(false);
    }
  }, [apiKey, config, isConnecting]);

  // Pause session
  const handlePause = useCallback(() => {
    if (sessionStats.status === 'running') {
      setSessionStats(prev => ({ ...prev, status: 'paused' }));
      wsConnectionRef.current?.sendMessage({ type: 'pause' });
    } else if (sessionStats.status === 'paused') {
      setSessionStats(prev => ({ ...prev, status: 'running' }));
      wsConnectionRef.current?.sendMessage({ type: 'resume' });
    }
  }, [sessionStats.status]);

  // Stop session
  const handleStop = useCallback(async () => {
    if (!sessionId) return;
    
    try {
      await axios.post(`${API_BASE_URL}/session/${sessionId}/stop`);
      console.log('[Dashboard] Session stopped');
      setSessionStats(prev => ({ ...prev, status: 'completed' }));
      wsConnectionRef.current?.disconnect();
      setSessionId('');
    } catch (error) {
      console.error('[Dashboard] Error stopping session:', error);
      const axiosError = error as { response?: { data?: { detail?: string } }; message?: string };
      setError(axiosError.response?.data?.detail || axiosError.message || 'Failed to stop session');
    }
  }, [sessionId]);

  // Execute custom user prompt
  const handleUserInput = useCallback(async (prompt: string) => {
    if (!prompt.trim()) return;
    
    // Need an active session to execute custom prompts
    if (!sessionId) {
      setError('Please start a session before submitting custom prompts');
      return;
    }
    
    try {
      console.log('[Dashboard] Executing custom prompt:', prompt);
      
      const response = await axios.post(`${API_BASE_URL}/prompt/execute`, {
        session_id: sessionId,
        prompt: prompt,
      });

      console.log('[Dashboard] Custom prompt response:', response.data);
      
      // Add result as an attack entry
      const customAttack: Attack = {
        id: `custom_${Date.now()}`,
        timestamp: response.data.timestamp || new Date().toISOString(),
        round: 0, // Custom prompts are not part of regular rounds
        prompt: response.data.prompt,
        response: response.data.response,
        domain: response.data.domain || 'custom',
        strategy: 'user_input',
        mutation: 'none',
        score: {
          global: response.data.global_score || 0,
          l1_linguistic: response.data.l1_score || 0,
          l2_security: response.data.l2_score || 0,
          l3_cognitive: response.data.l3_score || 0,
        },
        severity: getSeverity(response.data.global_score || 0),
        blocked: response.data.blocked || false,
      };
      
      setAttacks(prevAttacks => [customAttack, ...prevAttacks].slice(0, 100));
      
    } catch (error) {
      console.error('[Dashboard] Error executing custom prompt:', error);
      const axiosError = error as { response?: { data?: { detail?: string } }; message?: string };
      setError(axiosError.response?.data?.detail || axiosError.message || 'Failed to execute prompt');
    }
  }, [sessionId]);

  // Cleanup on unmount
  useEffect(() => {
    const cleanup = async () => {
      if (sessionId && sessionStats.status === 'running') {
        try {
          await axios.post(`${API_BASE_URL}/session/${sessionId}/stop`);
          console.log('[Dashboard] Session cleaned up on unmount');
        } catch (error) {
          console.error('[Dashboard] Error cleaning up session:', error);
        }
      }
    };
    
    return () => {
      safeAsync(cleanup);
    };
    // Only run on unmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="dashboard">
      {/* Error Display */}
      {error && (
        <div className="error-banner" style={{
          backgroundColor: '#fee',
          border: '1px solid #fcc',
          color: '#c33',
          padding: '12px 20px',
          marginBottom: '16px',
          borderRadius: '8px',
        }}>
          <strong>Error:</strong> {error}
          <button 
            onClick={() => setError(null)}
            style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px' }}
          >
            ×
          </button>
        </div>
      )}

      {/* Session Controls Header */}
      <header className="dashboard-header glass-panel">
        <div className="header-left">
          <div className="header-info">
            <h2>Active Red Teaming Session</h2>
            <p className="session-id">
              {sessionStats.sessionId ? `Session ID: ${sessionStats.sessionId}` : 'No active session'}
            </p>
          </div>
        </div>
        
        <div className="header-center">
          <div className="status-indicator">
            <div className={`status-dot status-${sessionStats.status}`}></div>
            <span className="status-text">{sessionStats.status.toUpperCase()}</span>
          </div>
          {wsConnectionRef.current?.isConnected && <span style={{ marginLeft: '8px', color: '#4ade80' }}>● WS Connected</span>}
        </div>

        <div className="header-right">
          <button 
            className="btn btn-secondary control-btn"
            onClick={handleStart}
            disabled={sessionStats.status === 'running' || isConnecting}
            aria-label="Start session"
          >
            <Play size={16} /> {isConnecting ? 'Starting...' : 'Start'}
          </button>
          <button 
            className="btn btn-secondary control-btn"
            onClick={handlePause}
            disabled={sessionStats.status !== 'running' && sessionStats.status !== 'paused'}
            aria-label="Pause session"
          >
            <Pause size={16} /> {sessionStats.status === 'paused' ? 'Resume' : 'Pause'}
          </button>
          <button 
            className="btn btn-primary control-btn"
            onClick={handleStop}
            disabled={sessionStats.status === 'idle' || sessionStats.status === 'completed'}
            aria-label="Stop session"
          >
            <Square size={16} /> Stop
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Left Column */}
        <div className="dashboard-column column-left">
          <LiveFeed attacks={attacks} />
        </div>

        {/* Center Column */}
        <div className="dashboard-column column-center">
          <MetricsPanel sessionStats={sessionStats} attacks={attacks} />
          <UserInput onSubmit={handleUserInput} disabled={!apiKey} />
        </div>

        {/* Right Column */}
        <div className="dashboard-column column-right">
          <CostTracker 
            currentCost={sessionStats.apiCost} 
            maxCost={config.maxApiCost}
            status={sessionStats.status}
          />
          <AttackConfig config={config} onConfigChange={setConfig} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
