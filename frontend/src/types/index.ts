export interface Attack {
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
  severity: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  blocked: boolean;
}

export interface SessionStats {
  sessionId: string;
  totalRounds: number;
  completedRounds: number;
  averageScore: number;
  blockedCount: number;
  apiCost: number;
  startTime: string;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'halted';
}

export interface AgentStats {
  sniper: {
    totalGenerated: number;
    mutationCount: number;
  };
  target: {
    totalExecutions: number;
    errorCount: number;
  };
  spotter: {
    totalEvaluations: number;
  };
  egg: {
    totalBlocked: number;
  };
}

export interface MutationStrategy {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
}

export interface AttackDomain {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
}

export interface SessionConfig {
  maxRounds: number;
  maxApiCost: number;
  haltOnCritical: boolean;
  backend: 'openai' | 'anthropic' | 'openrouter';
  model: string;
  mutationRate: number;
  semanticIntensity: 'low' | 'medium' | 'high'; // NEW: Control encoding transform drift
  selectedDomains: string[];
  selectedStrategies: string[];
  mutationWeights?: Record<string, number>;
  thresholds?: Record<string, number>;
}

export interface WebSocketMessage {
  type: 'attack' | 'stats' | 'status' | 'error' | 'ping' | 'pong';
  data: unknown;
}

export type OutgoingWebSocketMessage = 
  | { type: 'subscribe'; sessionId: string }
  | { type: 'pong' }
  | { type: 'start' }
  | { type: 'stop' }
  | { type: 'pause' }
  | { type: 'resume' };


export interface User {
  username: string;
  email: string;
  role: 'admin' | 'researcher' | 'observer';
  token?: string;
}

export interface ExperimentConfig {
  config_id?: string;
  name: string;
  description?: string;
  backend: string;
  model?: string;
  max_rounds: number;
  mutation_rate: number;
  semantic_intensity?: 'low' | 'medium' | 'high'; // NEW: Control encoding transform drift
  selected_domains: string[];
  selected_strategies: string[];
  mutation_weights?: Record<string, number>;
  thresholds?: Record<string, number>;
}

export interface LiveSession {
  session_id: string;
  status: string;
  start_time: string;
  current_cost: number;
  max_cost: number;
  config: {
    backend: string;
    model: string;
    max_rounds: number;
  };
}

export interface HistoricalSession {
  session_id: string;
  start_time: string;
  end_time: string;
  total_rounds: number;
  average_score: number;
  blocked_count: number;
  model_version: string;
}
