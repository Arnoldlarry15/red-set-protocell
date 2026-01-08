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
  backend: 'openai' | 'anthropic';
  model: string;
  mutationRate: number;
  selectedDomains: string[];
  selectedStrategies: string[];
}

export interface WebSocketMessage {
  type: 'attack' | 'stats' | 'status' | 'error';
  data: any;
}
