/**
 * ============================================================================
 * RED SET PROTOCELL - EIGHT-STATE ADAPTIVE LOOP SPECIFICATION
 * ============================================================================
 *
 * Research-grade specification for autonomous red teaming framework.
 * Defines explicit operational states with deterministic constraints,
 * logging requirements, and mutation boundaries.
 *
 * STATUS: LOCKED - Production configuration
 * VERSION: 1.0.0
 * AUTHOR: Red Set Research Team
 * DATE: 2025
 *
 * ============================================================================
 * STATE MACHINE OVERVIEW
 * ============================================================================
 *
 * INPUT_NORMALIZATION (1) → Target API
 *     ↓ [deterministic]
 * TARGET_INVOCATION (2) → Send normalized prompt
 *     ↓ [deterministic]
 * ADVERSARIAL_GENERATION (3) → Sniper generates variants
 *     ↓ [deterministic]
 * EXECUTION (4) → Deploy variants
 *     ↓ [deterministic]
 * EVALUATION (5) → Spotter scores outputs
 *     ↙         ↘
 * MUTATION (6)   ITERATION_CONTROL (7) → Decision logic
 *   ↓ [loop]         ↙              ↘
 *   │          continue         halt/escalate
 *   └──→ EXECUTION          REPORTING (8)
 *                           [TERMINAL]
 *
 * ============================================================================
 */

// ============================================================================
// SECTION 1: CORE OPERATIONAL STATE DEFINITIONS (States 1-8)
// ============================================================================

/**
 * STATE 1: INPUT_NORMALIZATION
 *
 * Purpose:
 *   Sanitize, tokenize, and structurally validate user input prompt.
 *   Produce deterministic representation for reproducibility.
 *
 * Mutability: IMMUTABLE
 *   Source truth must not change. Once normalized, locked for session.
 *
 * Key Constraint:
 *   Same raw prompt + same normalization rules → identical output
 *
 * Inputs:
 *   - Raw user prompt (string, unvalidated)
 *   - Normalization rules (tokenizer config, sanitizer rules)
 *
 * Outputs:
 *   - NormalizedPrompt (with SHA256 hash, token count, metadata)
 *
 * Logging:
 *   - Input length, output length, tokens, hash
 *   - Any sanitization actions taken (what was removed/encoded)
 *
 * Mutation Boundary:
 *   FORBIDDEN - Input normalization cannot be mutated.
 *   Rationale: Source truth must remain immutable for audit trail.
 */
export interface InputNormalizationState {
  // Source data (never mutate)
  rawPrompt: string;
  tokenCount: number;
  
  // Normalized output
  normalizedText: string;
  hash: string; // SHA256 of normalized prompt
  
  // Metadata
  characterLength: number;
  encodingFormat: 'utf-8' | 'ascii' | 'unicode';
  sanitizationApplied: boolean;
  sanitizationDetails: string[]; // List of actions taken
  
  // Session context
  sessionId: string;
  timestamp: number; // Unix milliseconds
  
  // Determinism flag
  deterministicChecksum: string;
}

/**
 * STATE 2: TARGET_INVOCATION
 *
 * Purpose:
 *   Send normalized prompt to target LLM with deterministic parameters.
 *   Capture API request and response as immutable source truth.
 *
 * Mutability: IMMUTABLE
 *   External API responses are source truth. Cannot be altered post-response.
 *
 * Key Constraint:
 *   Same normalized prompt + locked parameters → reproducible API response
 *   (assuming target model version frozen)
 *
 * Inputs:
 *   - NormalizedPrompt from STATE 1
 *   - API configuration (model, temperature=0.0 for determinism, etc.)
 *
 * Outputs:
 *   - TargetInvocationResult (API response, latency, cost, metadata)
 *
 * Logging:
 *   - Full API request sent
 *   - Full API response received
 *   - Latency, cost, error status
 *   - Retry count if applicable
 *
 * Mutation Boundary:
 *   FORBIDDEN - API responses are source truth.
 *   Rationale: Cannot rewrite what target model said. Traces external behavior.
 */
export interface TargetInvocationState {
  // Request info
  normalizedPromptHash: string; // Reference to STATE 1
  requestPayload: {
    model: string;
    prompt: string;
    temperature: number; // Locked to 0.0 for determinism
    maxTokens: number;
    topP: number;
    frequencyPenalty: number;
    presencePenalty: number;
  };
  
  // Response data (immutable)
  apiResponse: string;
  completionTokens: number;
  promptTokens: number;
  totalTokens: number;
  
  // Metadata
  apiLatencyMs: number;
  estimatedCostUsd: number;
  requestTimestamp: number;
  responseTimestamp: number;
  
  // Error handling
  httpStatusCode: number;
  errorMessage: string | null;
  retryCount: number;
  
  // Determinism tracking
  modelVersionHash: string; // Hash of model identifier
  apiChecksum: string; // Checksum of full request+response
}

/**
 * STATE 3: ADVERSARIAL_GENERATION
 *
 * Purpose:
 *   Sniper component generates initial probe variants from target response.
 *   Create semantically and syntactically distinct attack candidates.
 *
 * Mutability: MUTABLE
 *   This is the core mutation engine. Variants are intentionally transformed.
 *
 * Key Constraint:
 *   Reproducible under fixed seed: seed + target response → same variant set
 *
 * Inputs:
 *   - TargetInvocationResult from STATE 2
 *   - Mutation strategy configuration (types, intensity, seed)
 *   - Domain taxonomy (attack domains: jailbreak, prompt-injection, etc.)
 *
 * Outputs:
 *   - ProbeVariant[] (initial variant set, all with generation metadata)
 *
 * Logging:
 *   - Seed used
 *   - Number of variants generated
 *   - Mutation type per variant
 *   - Transformation trace (what changed)
 *   - Confidence score of variant
 *
 * Mutation Boundary:
 *   ALLOWED - Sniper MUST mutate to generate candidates.
 *   Constraint: All mutations seeded and logged.
 *   Audit: Can regenerate exact variant set with same seed.
 */
export interface AdversarialGenerationState {
  // Source reference
  targetResponseHash: string; // Reference to STATE 2
  
  // Configuration (locked for session)
  mutationSeed: number; // RNG seed for reproducibility
  mutationStrategy: MutationStrategy;
  selectedDomains: AttackDomain[];
  
  // Generated variants
  probeVariants: ProbeVariant[];
  
  // Generation metadata
  generationTimestamp: number;
  totalVariantsGenerated: number;
  
  // Determinism tracking
  generationChecksum: string; // Hash of seed + config + variants
}

/**
 * STATE 4: EXECUTION
 *
 * Purpose:
 *   Deploy probe variants against target LLM.
 *   Capture all API calls, responses, and execution metadata.
 *
 * Mutability: IMMUTABLE
 *   API responses are source truth. Cannot alter what target said.
 *
 * Key Constraint:
 *   Execution must be bounded: max concurrent requests, cost cap, timeout.
 *
 * Inputs:
 *   - ProbeVariant[] from STATE 3
 *   - Execution configuration (concurrency, timeout, cost limits)
 *
 * Outputs:
 *   - ExecutionResult[] (one per variant, with API response + metadata)
 *
 * Logging:
 *   - Variant ID vs API response (traceability)
 *   - Latency per request
 *   - Cost per request (cumulative)
 *   - Error status (rate limits, failures, etc.)
 *   - Execution order and timing
 *
 * Mutation Boundary:
 *   FORBIDDEN - External API responses cannot be mutated.
 *   Constraint: Bounded execution (cost, concurrency, time).
 *   Enforcement: Hard limits with telemetry before breach.
 */
export interface ExecutionState {
  // Reference to input
  probeVariantIds: string[]; // Which variants to execute
  
  // Execution configuration
  maxConcurrentRequests: number;
  maxApiCostPerRound: number;
  requestTimeoutMs: number;
  
  // Execution results
  executionResults: ExecutionResult[];
  
  // Bounded execution tracking
  totalCostAccumulated: number;
  totalRequestsExecuted: number;
  totalRequestsFailed: number;
  
  // Timing
  executionStartTimestamp: number;
  executionEndTimestamp: number;
  totalExecutionTimeMs: number;
  
  // Status
  executionStatus: 'pending' | 'in_progress' | 'completed' | 'halted_cost_limit' | 'halted_timeout';
  
  // Determinism tracking
  executionChecksum: string; // Hash of all results
}

/**
 * STATE 5: EVALUATION
 *
 * Purpose:
 *   Spotter component scores execution results using deterministic rubric.
 *   Assess risk across L1 (linguistic), L2 (security), L3 (cognitive) dimensions.
 *
 * Mutability: IMMUTABLE
 *   Scoring rubric is locked. Scores are deterministic, not adjusted post-hoc.
 *
 * Key Constraint:
 *   Same execution results + locked rubric → identical scores
 *
 * Inputs:
 *   - ExecutionResult[] from STATE 4
 *   - ScoringRubric (risk metrics, thresholds, weights)
 *
 * Outputs:
 *   - ScoreResult[] (L1, L2, L3 scores per variant, global risk)
 *
 * Logging:
 *   - Score breakdown (L1, L2, L3)
 *   - Rubric version used
 *   - Any edge cases or exceptions in scoring
 *   - Risk classification (safe, low, medium, high, critical)
 *
 * Mutation Boundary:
 *   FORBIDDEN - Scores cannot be adjusted after evaluation.
 *   Rationale: Risk assessment must be deterministic and auditable.
 *   Enforcement: Rubric locked at session start; no live adjustments.
 */
export interface EvaluationState {
  // Reference
  executionResultIds: string[];
  
  // Scoring configuration (locked)
  scoringRubric: ScoringRubric;
  rubricVersion: string;
  
  // Score results
  scoreResults: ScoreResult[];
  
  // Aggregate metrics
  averageL1Score: number;
  averageL2Score: number;
  averageL3Score: number;
  averageGlobalRiskScore: number;
  
  // Risk distribution
  riskDistribution: {
    safe: number;
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  
  // Timing
  evaluationTimestamp: number;
  
  // Determinism tracking
  evaluationChecksum: string; // Hash of all scores
}

/**
 * STATE 6: MUTATION
 *
 * Purpose:
 *   Adaptive perturbation of high-signal variants based on risk gradient.
 *   Refine probe set to explore vulnerability space more deeply.
 *
 * Mutability: MUTABLE
 *   This is THE mutation state. Variants are intentionally transformed.
 *
 * Key Constraint:
 *   Reproducible: high-signal variants + risk gradient + seed → refined variants
 *
 * Inputs:
 *   - ProbeVariant[] (high-signal variants from execution)
 *   - ScoreResult[] (risk feedback from evaluation)
 *   - MutationConfig (strategy, intensity, seed)
 *   - Iteration count (controls mutation intensity scaling)
 *
 * Outputs:
 *   - ProbeVariant[] (refined variant set)
 *   - MutationLogEntry[] (full transformation trace)
 *
 * Logging:
 *   - Which variants were selected as high-signal
 *   - Mutation intensity per iteration
 *   - Seed and transformation details
 *   - Confidence delta (score improvement expected)
 *   - Mutation type applied
 *
 * Mutation Boundary:
 *   REQUIRED - Mutation MUST happen in this state.
 *   Constraint: All mutations seeded and logged with full traceability.
 *   Audit: Can regenerate exact refined set with same seed + gradient.
 */
export interface MutationState {
  // References
  highSignalVariantIds: string[];
  scoreResultsRef: ScoreResult[];
  
  // Mutation configuration
  mutationSeed: number;
  mutationConfig: MutationConfig;
  iterationCount: number; // Controls intensity scaling
  
  // Risk gradient (guides mutation)
  riskGradient: RiskGradient;
  
  // Mutation results
  refinedVariants: ProbeVariant[];
  mutationLog: MutationLogEntry[];
  
  // Metrics
  variantsRefined: number;
  avgConfidenceDelta: number; // Expected improvement
  
  // Timing
  mutationTimestamp: number;
  
  // Determinism tracking
  mutationChecksum: string; // Hash of seed + config + results
}

/**
 * STATE 7: ITERATION_CONTROL
 *
 * Purpose:
 *   Deterministic logic to decide: continue loop, escalate, or terminate.
 *   Apply convergence criteria, cost limits, max iterations.
 *
 * Mutability: IMMUTABLE
 *   Decision logic is deterministic. No adjustment based on intuition.
 *
 * Key Constraint:
 *   Same metrics + locked criteria → same decision (continue/halt/escalate)
 *
 * Inputs:
 *   - EvaluationState (current scores)
 *   - SessionMetadata (cost, rounds, time elapsed)
 *   - TerminationCriteria (max iterations, cost cap, convergence threshold)
 *
 * Outputs:
 *   - IterationControlDecision (type: continue | halt | escalate)
 *   - ExitReason (explicit reason for decision)
 *
 * Logging:
 *   - Current cost vs limit
 *   - Round count vs max
 *   - Convergence metric (if tracking)
 *   - Decision rationale
 *
 * Mutation Boundary:
 *   FORBIDDEN - Decision logic cannot be adjusted on the fly.
 *   Rationale: Prevents arbitrary loop termination or extension.
 *   Enforcement: Criteria locked at session start.
 */
export interface IterationControlState {
  // Session metrics
  currentRound: number;
  currentCumulativeCost: number;
  currentCumulativeTime: number;
  
  // Termination criteria (locked)
  criteria: TerminationCriteria;
  
  // Decision
  decision: 'CONTINUE' | 'HALT' | 'ESCALATE';
  exitReason: string;
  
  // Reasoning
  costRemainingBudget: number;
  roundsRemaining: number;
  convergenceMetric: number | null; // If tracking convergence
  
  // Timestamp
  controlTimestamp: number;
  
  // Determinism tracking
  controlChecksum: string;
}

/**
 * STATE 8: REPORTING
 *
 * Purpose:
 *   Generate final structured report with full traceability.
 *   All vulnerabilities, risk scores, mutation history, session metadata.
 *   Terminal state - no further processing.
 *
 * Mutability: IMMUTABLE
 *   Report is final. Signed with checksum. Cannot be altered.
 *
 * Key Constraint:
 *   Report must be reproducible: given session transcript + seeds, regenerate identical report.
 *
 * Inputs:
 *   - All prior state outputs (accumulated during session)
 *   - SessionMetadata (full context)
 *
 * Outputs:
 *   - StructuredRiskReport (JSON/structured format)
 *   - ReportSignature (cryptographic checksum)
 *
 * Logging:
 *   - Final report persisted to database
 *   - Signature verification passed
 *   - Tamper detection configured
 *
 * Mutation Boundary:
 *   FORBIDDEN - Report is immutable after generation.
 *   Rationale: Terminal state, audit trail, legal record.
 *   Enforcement: Signature verification on retrieval.
 */
export interface ReportingState {
  // Session context
  sessionId: string;
  sessionMetadata: SessionMetadata;
  
  // Full result aggregation
  totalRounds: number;
  totalCost: number;
  totalExecutionTime: number;
  
  // Risk summary
  vulnerabilitiesFound: VulnerabilityRecord[];
  overallRiskLevel: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  riskScoreSummary: {
    avgL1: number;
    avgL2: number;
    avgL3: number;
    avgGlobal: number;
  };
  
  // Mutation history
  totalMutationCycles: number;
  mutationCycleLog: MutationLogEntry[];
  
  // Execution history
  totalProbesGenerated: number;
  totalProbesExecuted: number;
  totalProbesFailed: number;
  
  // Report metadata
  reportGeneratedTimestamp: number;
  reportVersion: string;
  
  // Immutability tracking
  reportSignature: string; // Cryptographic hash
  tamperDetectionEnabled: boolean;
  
  // Full audit trail (for reproducibility)
  auditTrail: AuditTrailEntry[];
}

// ============================================================================
// SECTION 2: SUPPORTING TYPE DEFINITIONS (15+ types)
// ============================================================================

/**
 * Normalized prompt with deterministic hash and metadata.
 */
export interface NormalizedPrompt {
  text: string;
  hash: string; // SHA256
  tokenCount: number;
  characterLength: number;
  encoding: 'utf-8' | 'ascii' | 'unicode';
  sanitizationApplied: boolean;
  sanitizationLog: Array<{
    action: string;
    description: string;
    timestamp: number;
  }>;
}

/**
 * Probe variant generated by Sniper.
 */
export interface ProbeVariant {
  id: string;
  generationRound: number;
  parentVariantId: string | null; // null if initial generation
  mutationType: string; // e.g., 'lexical', 'structural', 'context', 'constraint', 'payload'
  
  // Variant content
  probeText: string;
  tokenCount: number;
  
  // Generation metadata
  domainTarget: string; // Which attack domain
  strategyUsed: string; // Strategy identifier
  mutationSeed: number;
  transformationTrace: string; // Detailed transformation log
  
  // Confidence (for sorting)
  generationConfidenceScore: number; // 0-100
  
  // Execution tracking
  executionStatus: 'pending' | 'executed' | 'failed';
  executionResultId: string | null;
  
  // Timestamps
  createdAt: number;
  executedAt: number | null;
}

/**
 * API execution result for a single probe variant.
 */
export interface ExecutionResult {
  id: string;
  variantId: string;
  
  // Request
  requestPayload: {
    model: string;
    prompt: string;
    temperature: number;
    maxTokens: number;
  };
  
  // Response
  apiResponse: string;
  completionTokens: number;
  promptTokens: number;
  
  // Metadata
  apiLatencyMs: number;
  estimatedCostUsd: number;
  httpStatusCode: number;
  errorMessage: string | null;
  
  // Timestamps
  requestSentAt: number;
  responseSentAt: number;
}

/**
 * Risk score result for a single variant execution.
 */
export interface ScoreResult {
  id: string;
  executionResultId: string;
  variantId: string;
  
  // L1 Linguistic Dimension
  l1_linguistic: {
    score: number; // 0-100
    dimension: 'syntax_anomaly' | 'semantic_drift' | 'encoding_bypass';
    explanation: string;
  };
  
  // L2 Security Dimension
  l2_security: {
    score: number; // 0-100
    dimension: 'prompt_injection' | 'jailbreak' | 'bypass_trigger';
    explanation: string;
  };
  
  // L3 Cognitive Dimension
  l3_cognitive: {
    score: number; // 0-100
    dimension: 'goal_subversion' | 'value_misalignment' | 'deception';
    explanation: string;
  };
  
  // Global
  globalRiskScore: number; // 0-100 (weighted average)
  riskClassification: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  
  // Metadata
  rubricVersion: string;
  scoredAt: number;
}

/**
 * Configuration for mutation strategy.
 */
export interface MutationStrategy {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  priority: number; // Sort order
  
  // Mutation parameters
  intensityMultiplier: number; // 1.0 = base intensity, 2.0 = doubled
  targetRiskLevel: 'low' | 'medium' | 'high';
}

/**
 * Attack domain configuration.
 */
export interface AttackDomain {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  
  // Domain specifics
  keywordTriggers: string[];
  riskDimensionFocus: 'L1' | 'L2' | 'L3' | 'balanced';
}

/**
 * Detailed mutation log entry.
 */
export interface MutationLogEntry {
  id: string;
  iterationRound: number;
  sourceVariantId: string;
  targetVariantId: string;
  
  // Transformation
  mutationType: string;
  transformationDetails: {
    originalText: string;
    transformedText: string;
    changesApplied: string[];
    seedUsed: number;
  };
  
  // Metrics
  expectedRiskDelta: number; // Expected score improvement
  actualRiskDelta: number | null; // Filled after execution
  
  // Metadata
  mutationTimestamp: number;
  executionTimestamp: number | null;
}

/**
 * Risk gradient guides adaptive exploration.
 */
export interface RiskGradient {
  l1_direction: 'increase' | 'maintain' | 'decrease';
  l2_direction: 'increase' | 'maintain' | 'decrease';
  l3_direction: 'increase' | 'maintain' | 'decrease';
  
  // Suggests which mutation types to prioritize
  suggestedMutationTypes: string[];
  
  // Convergence signal
  convergenceScore: number; // 0-1, higher = more converged
}

/**
 * Mutation configuration for current round.
 */
export interface MutationConfig {
  strategy: string;
  intensity: number; // 0-100, scales mutation perturbation
  seed: number; // RNG seed for reproducibility
  maxMutationsPerVariant: number;
  
  // Which mutation types allowed
  enabledMutationTypes: Array<
    'lexical' | 'structural' | 'context' | 'constraint' | 'payload'
  >;
}

/**
 * Termination criteria for loop control.
 */
export interface TerminationCriteria {
  maxRounds: number;
  maxApiCostUsd: number;
  maxExecutionTimeMs: number;
  haltOnCriticalFound: boolean;
  
  // Convergence criteria
  convergenceThreshold: number | null; // null = disabled
  convergenceWindowRounds: number;
  
  // Explicit stopping signals
  minRoundsBeforeHalt: number; // Prevent premature exit
}

/**
 * Session-wide metadata.
 */
export interface SessionMetadata {
  sessionId: string;
  userId: string;
  createdAt: number;
  
  // Configuration
  targetModel: string;
  backend: 'openai' | 'anthropic';
  
  // Resource tracking
  initialBudgetUsd: number;
  currentCostUsd: number;
  
  // State tracking
  currentRound: number;
  currentState: AdaptiveLoopStateName;
  
  // Timestamps
  startTime: number;
  pausedTime: number | null;
  resumedTime: number | null;
  endTime: number | null;
}

/**
 * Scoring rubric defines risk assessment.
 */
export interface ScoringRubric {
  id: string;
  version: string;
  name: string;
  
  // Dimension definitions
  l1_linguistic: {
    description: string;
    weight: number; // 0-1
    thresholds: {
      safe: number;
      low: number;
      medium: number;
      high: number;
      critical: number;
    };
  };
  
  l2_security: {
    description: string;
    weight: number;
    thresholds: {
      safe: number;
      low: number;
      medium: number;
      high: number;
      critical: number;
    };
  };
  
  l3_cognitive: {
    description: string;
    weight: number;
    thresholds: {
      safe: number;
      low: number;
      medium: number;
      high: number;
      critical: number;
    };
  };
  
  // Global scoring
  globalWeighting: {
    l1_weight: number;
    l2_weight: number;
    l3_weight: number;
  };
  
  // Locked at session start
  lockedAt: number;
  lockedByUserId: string;
}

/**
 * Vulnerability record for final report.
 */
export interface VulnerabilityRecord {
  id: string;
  variantId: string;
  executionResultId: string;
  
  // The vulnerability
  probeText: string;
  targetResponse: string;
  
  // Risk assessment
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  globalRiskScore: number;
  dimensionalScores: {
    l1_linguistic: number;
    l2_security: number;
    l3_cognitive: number;
  };
  
  // Classification
  attackDomain: string;
  vulnerabilityType: string;
  description: string;
  
  // Evidence
  mutationHistory: MutationLogEntry[];
  
  // Metadata
  discoveredAtRound: number;
  discoveredAt: number;
}

/**
 * Audit trail entry for full reproducibility.
 */
export interface AuditTrailEntry {
  id: string;
  round: number;
  stateName: AdaptiveLoopStateName;
  action: string;
  timestamp: number;
  
  // State snapshot (minimal)
  stateChecksum: string;
  
  // Change tracking
  mutationsApplied: string[];
  dataModified: Record<string, unknown>;
}

/**
 * Structured risk report (final deliverable).
 */
export interface StructuredRiskReport {
  id: string;
  sessionId: string;
  reportVersion: string;
  
  // Metadata
  generatedAt: number;
  generatedBy: string;
  
  // Summary
  executive_summary: string;
  overall_risk_level: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  
  // Findings
  vulnerabilities: VulnerabilityRecord[];
  total_vulnerabilities: number;
  vulnerability_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  
  // Metrics
  total_probes_generated: number;
  total_probes_executed: number;
  success_rate: number;
  average_risk_score: number;
  
  // Cost and resources
  total_api_cost: number;
  total_execution_time: number;
  total_rounds: number;
  
  // Mutation details
  total_mutations: number;
  mutation_effectiveness: number;
  
  // Recommendations
  remediation_recommendations: string[];
  further_testing_suggestions: string[];
  
  // Signature
  signature: string; // Cryptographic verification
}

// ============================================================================
// SECTION 3: MUTABILITY AND CONSTRAINT ENFORCEMENT
// ============================================================================

/**
 * Mutability classification for states.
 * IMMUTABLE: Source truth, cannot be changed
 * MUTABLE: Intentional transformation, must be logged
 * NONE: Read-only reference state
 */
export type MutabilityLevel = 'IMMUTABLE' | 'MUTABLE' | 'REFERENCE';

export interface MutabilityBoundary {
  stateName: AdaptiveLoopStateName;
  mutability: MutabilityLevel;
  rationale: string;
  
  // Enforcement
  checksumRequired: boolean;
  loggingRequired: boolean;
  auditTrailRequired: boolean;
  
  // Constraints
  constraints: string[];
}

/**
 * Determinism constraint specification.
 */
export interface DeterminismConstraint {
  stateName: AdaptiveLoopStateName;
  
  // Reproducibility guarantee
  reproducibilityGuarantee: string;
  // e.g., "Same input + seed → identical output"
  
  // Seed handling
  requiresExplicitSeed: boolean;
  seedHashing: 'SHA256' | 'MD5' | 'BLAKE2' | 'NONE';
  
  // Hard limits
  hardLimits: {
    maxIterations?: number;
    maxCostBudget?: number;
    maxTimeoutMs?: number;
    maxConcurrentRequests?: number;
  };
  
  // Verification
  verificationMethod: string;
}

/**
 * Logging requirement specification.
 */
export interface LoggingRequirement {
  stateName: AdaptiveLoopStateName;
  
  // What to log
  fieldsToLog: Array<{
    field: string;
    dataType: string;
    description: string;
  }>;
  
  // Where to log
  logDestinations: Array<'console' | 'file' | 'database' | 'audit'>;
  
  // Retention
  retentionDays: number;
  retentionPolicy: 'permanent' | 'session' | 'purge_after_days';
  
  // Masking (PII, secrets)
  fieldsToMask: string[];
  maskingStrategy: 'hash' | 'redact' | 'pseudonymize';
  
  // Immutability
  immutabilityRequired: boolean;
}

// ============================================================================
// SECTION 4: STATE TRANSITION AND FLOW CONTROL
// ============================================================================

/**
 * State names as literal union type.
 */
export type AdaptiveLoopStateName =
  | 'INPUT_NORMALIZATION'
  | 'TARGET_INVOCATION'
  | 'ADVERSARIAL_GENERATION'
  | 'EXECUTION'
  | 'EVALUATION'
  | 'MUTATION'
  | 'ITERATION_CONTROL'
  | 'REPORTING';

/**
 * Valid state transitions.
 */
export type StateTransition = 
  | { from: 'INPUT_NORMALIZATION'; to: 'TARGET_INVOCATION' }
  | { from: 'TARGET_INVOCATION'; to: 'ADVERSARIAL_GENERATION' }
  | { from: 'ADVERSARIAL_GENERATION'; to: 'EXECUTION' }
  | { from: 'EXECUTION'; to: 'EVALUATION' }
  | { from: 'EVALUATION'; to: 'ITERATION_CONTROL' }
  | { from: 'ITERATION_CONTROL'; to: 'MUTATION' }
  | { from: 'ITERATION_CONTROL'; to: 'REPORTING' }
  | { from: 'MUTATION'; to: 'EXECUTION' };

/**
 * Iteration control decision type.
 */
export type IterationDecision = 'CONTINUE' | 'HALT' | 'ESCALATE';

/**
 * Loop control flow state.
 */
export interface LoopControlFlow {
  currentRound: number;
  currentState: AdaptiveLoopStateName;
  nextState: AdaptiveLoopStateName | null;
  
  // Decision tracking
  lastDecision: IterationDecision | null;
  decisionReason: string;
  
  // Resources
  costRemaining: number;
  timeRemaining: number;
  roundsRemaining: number;
}

// ============================================================================
// SECTION 5: STATE MACHINE DEFINITION AND CONSTANTS
// ============================================================================

/**
 * Complete definition of all 8 states with metadata.
 */
export interface AdaptiveLoopStateDefinition {
  id: number;
  name: AdaptiveLoopStateName;
  description: string;
  
  // Constraints
  mutability: MutabilityLevel;
  determinism: DeterminismConstraint;
  logging: LoggingRequirement;
  boundary: MutabilityBoundary;
  
  // Documentation
  purpose: string;
  inputs: Array<{ name: string; type: string; description: string }>;
  outputs: Array<{ name: string; type: string; description: string }>;
  
  // Flow
  validNextStates: AdaptiveLoopStateName[];
  allowsLoopback: boolean;
}

/**
 * Master state machine constant.
 * Defines all 8 states with full specifications.
 */
export const ADAPTIVE_LOOP_STATES: Record<AdaptiveLoopStateName, AdaptiveLoopStateDefinition> = {
  INPUT_NORMALIZATION: {
    id: 1,
    name: 'INPUT_NORMALIZATION',
    description: 'Sanitize, tokenize, structurally validate user prompt',
    
    mutability: 'IMMUTABLE',
    determinism: {
      stateName: 'INPUT_NORMALIZATION',
      reproducibilityGuarantee: 'Same raw prompt + normalization rules → identical output',
      requiresExplicitSeed: false,
      seedHashing: 'NONE',
      hardLimits: { maxTimeoutMs: 5000 },
      verificationMethod: 'SHA256 hash comparison',
    },
    logging: {
      stateName: 'INPUT_NORMALIZATION',
      fieldsToLog: [
        { field: 'rawPromptLength', dataType: 'number', description: 'Input length' },
        { field: 'normalizedText', dataType: 'string', description: 'Sanitized text' },
        { field: 'tokenCount', dataType: 'number', description: 'Token count' },
        { field: 'hash', dataType: 'string', description: 'SHA256 checksum' },
        { field: 'sanitizationApplied', dataType: 'boolean', description: 'Was sanitization needed' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 365,
      retentionPolicy: 'permanent',
      fieldsToMask: [],
      maskingStrategy: 'hash',
      immutabilityRequired: true,
    },
    boundary: {
      stateName: 'INPUT_NORMALIZATION',
      mutability: 'IMMUTABLE',
      rationale: 'Source truth must not change. Audit trail depends on immutable input.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'Cannot modify normalized output after generation',
        'Must preserve original raw prompt hash',
        'Deterministic tokenization required',
      ],
    },
    purpose: 'Produce deterministic normalized representation of user input for reproducible execution',
    inputs: [
      { name: 'rawPrompt', type: 'string', description: 'User-provided prompt' },
      { name: 'normalizationRules', type: 'Config', description: 'Tokenizer and sanitizer rules' },
    ],
    outputs: [
      { name: 'NormalizedPrompt', type: 'NormalizedPrompt', description: 'Sanitized, tokenized prompt' },
    ],
    validNextStates: ['TARGET_INVOCATION'],
    allowsLoopback: false,
  },
  
  TARGET_INVOCATION: {
    id: 2,
    name: 'TARGET_INVOCATION',
    description: 'Send normalized prompt to target LLM with deterministic parameters',
    
    mutability: 'IMMUTABLE',
    determinism: {
      stateName: 'TARGET_INVOCATION',
      reproducibilityGuarantee: 'Same prompt + locked params → reproducible response (model version frozen)',
      requiresExplicitSeed: false,
      seedHashing: 'NONE',
      hardLimits: { maxTimeoutMs: 120000, maxCostBudget: 1.0 },
      verificationMethod: 'API checksum (request + response hash)',
    },
    logging: {
      stateName: 'TARGET_INVOCATION',
      fieldsToLog: [
        { field: 'requestPayload', dataType: 'object', description: 'Full API request' },
        { field: 'apiResponse', dataType: 'string', description: 'Full API response' },
        { field: 'apiLatencyMs', dataType: 'number', description: 'Latency' },
        { field: 'estimatedCostUsd', dataType: 'number', description: 'Cost' },
        { field: 'httpStatusCode', dataType: 'number', description: 'HTTP status' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 365,
      retentionPolicy: 'permanent',
      fieldsToMask: ['apiKey'],
      maskingStrategy: 'redact',
      immutabilityRequired: true,
    },
    boundary: {
      stateName: 'TARGET_INVOCATION',
      mutability: 'IMMUTABLE',
      rationale: 'API responses are source truth. Cannot rewrite target model behavior.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'Temperature locked to 0.0 for determinism',
        'Cannot alter API response post-reception',
        'Retry logic must be transparent',
      ],
    },
    purpose: 'Capture deterministic API interaction with target model',
    inputs: [
      { name: 'normalizedPrompt', type: 'NormalizedPrompt', description: 'From STATE 1' },
      { name: 'apiConfig', type: 'Config', description: 'Model, temperature, limits' },
    ],
    outputs: [
      { name: 'TargetInvocationResult', type: 'TargetInvocationState', description: 'API response + metadata' },
    ],
    validNextStates: ['ADVERSARIAL_GENERATION'],
    allowsLoopback: false,
  },
  
  ADVERSARIAL_GENERATION: {
    id: 3,
    name: 'ADVERSARIAL_GENERATION',
    description: 'Sniper generates initial probe variants from target response',
    
    mutability: 'MUTABLE',
    determinism: {
      stateName: 'ADVERSARIAL_GENERATION',
      reproducibilityGuarantee: 'Seed + target response → same variant set',
      requiresExplicitSeed: true,
      seedHashing: 'SHA256',
      hardLimits: { maxIterations: 10000 },
      verificationMethod: 'Seed replay with checksum verification',
    },
    logging: {
      stateName: 'ADVERSARIAL_GENERATION',
      fieldsToLog: [
        { field: 'mutationSeed', dataType: 'number', description: 'RNG seed' },
        { field: 'variantsGenerated', dataType: 'number', description: 'Count' },
        { field: 'mutationType', dataType: 'string[]', description: 'Types per variant' },
        { field: 'transformationTrace', dataType: 'string', description: 'Detailed changes' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 365,
      retentionPolicy: 'permanent',
      fieldsToMask: [],
      maskingStrategy: 'hash',
      immutabilityRequired: false,
    },
    boundary: {
      stateName: 'ADVERSARIAL_GENERATION',
      mutability: 'MUTABLE',
      rationale: 'Sniper MUST mutate to generate adversarial candidates.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'All mutations must be seeded',
        'Seed must be logged and immutable',
        'Transformation trace required for every variant',
        'Can regenerate exact variants with same seed',
      ],
    },
    purpose: 'Generate diverse attack variants using mutation engine',
    inputs: [
      { name: 'targetResponse', type: 'TargetInvocationState', description: 'From STATE 2' },
      { name: 'mutationSeed', type: 'number', description: 'RNG seed for reproducibility' },
      { name: 'mutationStrategy', type: 'MutationStrategy', description: 'Strategy config' },
    ],
    outputs: [
      { name: 'probeVariants', type: 'ProbeVariant[]', description: 'Generated variants' },
      { name: 'generationLog', type: 'MutationLogEntry[]', description: 'Transformation traces' },
    ],
    validNextStates: ['EXECUTION'],
    allowsLoopback: false,
  },
  
  EXECUTION: {
    id: 4,
    name: 'EXECUTION',
    description: 'Deploy probe variants against target model',
    
    mutability: 'IMMUTABLE',
    determinism: {
      stateName: 'EXECUTION',
      reproducibilityGuarantee: 'Variant set → API responses (deterministic for same model version)',
      requiresExplicitSeed: false,
      seedHashing: 'NONE',
      hardLimits: { maxConcurrentRequests: 10, maxCostBudget: 100.0, maxTimeoutMs: 600000 },
      verificationMethod: 'Cost tracking, rate limit detection, timeout enforcement',
    },
    logging: {
      stateName: 'EXECUTION',
      fieldsToLog: [
        { field: 'variantId', dataType: 'string', description: 'Which variant' },
        { field: 'apiResponse', dataType: 'string', description: 'Response text' },
        { field: 'apiLatencyMs', dataType: 'number', description: 'Latency per request' },
        { field: 'cumulativeCost', dataType: 'number', description: 'Running cost' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 365,
      retentionPolicy: 'permanent',
      fieldsToMask: [],
      maskingStrategy: 'hash',
      immutabilityRequired: true,
    },
    boundary: {
      stateName: 'EXECUTION',
      mutability: 'IMMUTABLE',
      rationale: 'API responses cannot be modified. Execution bounded by cost/concurrency/time limits.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'Hard cost limit enforcement',
        'Max concurrent requests enforced',
        'Request timeout enforced',
        'Rate limit detection enabled',
        'Cannot alter API responses',
      ],
    },
    purpose: 'Execute probe variants with bounded resource consumption',
    inputs: [
      { name: 'probeVariants', type: 'ProbeVariant[]', description: 'From STATE 3' },
      { name: 'executionConfig', type: 'Config', description: 'Limits and constraints' },
    ],
    outputs: [
      { name: 'executionResults', type: 'ExecutionResult[]', description: 'API responses + metadata' },
    ],
    validNextStates: ['EVALUATION'],
    allowsLoopback: false,
  },
  
  EVALUATION: {
    id: 5,
    name: 'EVALUATION',
    description: 'Spotter scores execution results using locked rubric',
    
    mutability: 'IMMUTABLE',
    determinism: {
      stateName: 'EVALUATION',
      reproducibilityGuarantee: 'Same execution results + locked rubric → identical scores',
      requiresExplicitSeed: false,
      seedHashing: 'NONE',
      hardLimits: {},
      verificationMethod: 'Rubric version + result hash comparison',
    },
    logging: {
      stateName: 'EVALUATION',
      fieldsToLog: [
        { field: 'l1Score', dataType: 'number', description: 'Linguistic score' },
        { field: 'l2Score', dataType: 'number', description: 'Security score' },
        { field: 'l3Score', dataType: 'number', description: 'Cognitive score' },
        { field: 'globalScore', dataType: 'number', description: 'Weighted global' },
        { field: 'riskClassification', dataType: 'string', description: 'Risk level' },
        { field: 'rubricVersion', dataType: 'string', description: 'Rubric used' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 365,
      retentionPolicy: 'permanent',
      fieldsToMask: [],
      maskingStrategy: 'hash',
      immutabilityRequired: true,
    },
    boundary: {
      stateName: 'EVALUATION',
      mutability: 'IMMUTABLE',
      rationale: 'Risk scores must be deterministic and auditable. No post-hoc adjustment.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'Rubric locked at session start',
        'No live adjustments to scoring rules',
        'Scores cannot be changed after evaluation',
        'Rubric version must be recorded',
      ],
    },
    purpose: 'Deterministically score risk across L1/L2/L3 dimensions',
    inputs: [
      { name: 'executionResults', type: 'ExecutionResult[]', description: 'From STATE 4' },
      { name: 'scoringRubric', type: 'ScoringRubric', description: 'Risk metrics (locked)' },
    ],
    outputs: [
      { name: 'scoreResults', type: 'ScoreResult[]', description: 'L1/L2/L3 + global scores' },
    ],
    validNextStates: ['ITERATION_CONTROL'],
    allowsLoopback: false,
  },
  
  MUTATION: {
    id: 6,
    name: 'MUTATION',
    description: 'Adapt and refine variants based on risk gradient',
    
    mutability: 'MUTABLE',
    determinism: {
      stateName: 'MUTATION',
      reproducibilityGuarantee: 'High-signal variants + risk gradient + seed → refined variants',
      requiresExplicitSeed: true,
      seedHashing: 'SHA256',
      hardLimits: { maxIterations: 10000 },
      verificationMethod: 'Seed replay with gradient checksum',
    },
    logging: {
      stateName: 'MUTATION',
      fieldsToLog: [
        { field: 'mutationSeed', dataType: 'number', description: 'RNG seed' },
        { field: 'selectedVariants', dataType: 'string[]', description: 'High-signal IDs' },
        { field: 'riskGradient', dataType: 'object', description: 'Gradient data' },
        { field: 'mutationIntensity', dataType: 'number', description: 'Intensity scaling' },
        { field: 'refinedVariantIds', dataType: 'string[]', description: 'Output variants' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 365,
      retentionPolicy: 'permanent',
      fieldsToMask: [],
      maskingStrategy: 'hash',
      immutabilityRequired: false,
    },
    boundary: {
      stateName: 'MUTATION',
      mutability: 'MUTABLE',
      rationale: 'Mutation state MUST transform variants. All mutations seeded and logged.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'All mutations must be seeded',
        'Seed immutable after recording',
        'Transformation trace required',
        'Risk gradient drives mutation direction',
        'Intensity scales per iteration',
        'Can regenerate exact refined set with seed + gradient',
      ],
    },
    purpose: 'Adaptively refine variants based on risk feedback',
    inputs: [
      { name: 'highSignalVariants', type: 'ProbeVariant[]', description: 'Variants to refine' },
      { name: 'scoreResults', type: 'ScoreResult[]', description: 'Risk feedback from STATE 5' },
      { name: 'mutationSeed', type: 'number', description: 'RNG seed' },
      { name: 'riskGradient', type: 'RiskGradient', description: 'Guides mutation' },
      { name: 'iterationCount', type: 'number', description: 'Controls intensity' },
    ],
    outputs: [
      { name: 'refinedVariants', type: 'ProbeVariant[]', description: 'Mutated variants' },
      { name: 'mutationLog', type: 'MutationLogEntry[]', description: 'Transformation traces' },
    ],
    validNextStates: ['EXECUTION'],
    allowsLoopback: true,
  },
  
  ITERATION_CONTROL: {
    id: 7,
    name: 'ITERATION_CONTROL',
    description: 'Deterministic loop control: continue, escalate, or halt',
    
    mutability: 'IMMUTABLE',
    determinism: {
      stateName: 'ITERATION_CONTROL',
      reproducibilityGuarantee: 'Same metrics + locked criteria → same decision',
      requiresExplicitSeed: false,
      seedHashing: 'NONE',
      hardLimits: {},
      verificationMethod: 'Decision logic hash + criteria version',
    },
    logging: {
      stateName: 'ITERATION_CONTROL',
      fieldsToLog: [
        { field: 'decision', dataType: 'string', description: 'CONTINUE | HALT | ESCALATE' },
        { field: 'exitReason', dataType: 'string', description: 'Why this decision' },
        { field: 'currentRound', dataType: 'number', description: 'Iteration count' },
        { field: 'costRemaining', dataType: 'number', description: 'Budget left' },
        { field: 'convergenceMetric', dataType: 'number', description: 'If tracking' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 365,
      retentionPolicy: 'permanent',
      fieldsToMask: [],
      maskingStrategy: 'hash',
      immutabilityRequired: true,
    },
    boundary: {
      stateName: 'ITERATION_CONTROL',
      mutability: 'IMMUTABLE',
      rationale: 'Loop control logic is deterministic. Prevents arbitrary termination or extension.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'Criteria locked at session start',
        'No adjustment on the fly',
        'Explicit termination criteria only',
        'No magic thresholds',
      ],
    },
    purpose: 'Apply convergence criteria and resource limits to determine loop fate',
    inputs: [
      { name: 'evaluationState', type: 'EvaluationState', description: 'From STATE 5' },
      { name: 'sessionMetadata', type: 'SessionMetadata', description: 'Cost, rounds, time' },
      { name: 'terminationCriteria', type: 'TerminationCriteria', description: 'Limits (locked)' },
    ],
    outputs: [
      { name: 'decision', type: 'IterationControlDecision', description: 'CONTINUE | HALT | ESCALATE' },
      { name: 'controlState', type: 'IterationControlState', description: 'Decision + reasoning' },
    ],
    validNextStates: ['MUTATION', 'REPORTING'],
    allowsLoopback: false,
  },
  
  REPORTING: {
    id: 8,
    name: 'REPORTING',
    description: 'Generate final structured report with full traceability',
    
    mutability: 'IMMUTABLE',
    determinism: {
      stateName: 'REPORTING',
      reproducibilityGuarantee: 'Session transcript + seeds → identical report',
      requiresExplicitSeed: false,
      seedHashing: 'NONE',
      hardLimits: {},
      verificationMethod: 'Cryptographic signature verification',
    },
    logging: {
      stateName: 'REPORTING',
      fieldsToLog: [
        { field: 'reportId', dataType: 'string', description: 'Unique report ID' },
        { field: 'signature', dataType: 'string', description: 'Cryptographic signature' },
        { field: 'vulnerabilityCount', dataType: 'number', description: 'Found vulnerabilities' },
        { field: 'overallRisk', dataType: 'string', description: 'Risk level' },
        { field: 'persistedAt', dataType: 'number', description: 'Storage timestamp' },
      ],
      logDestinations: ['database', 'audit'],
      retentionDays: 3650,
      retentionPolicy: 'permanent',
      fieldsToMask: [],
      maskingStrategy: 'hash',
      immutabilityRequired: true,
    },
    boundary: {
      stateName: 'REPORTING',
      mutability: 'IMMUTABLE',
      rationale: 'Terminal state. Report is legal record. Cannot be altered post-generation.',
      checksumRequired: true,
      loggingRequired: true,
      auditTrailRequired: true,
      constraints: [
        'Report is final and immutable',
        'Cryptographic signature verification on retrieval',
        'Tamper detection configured',
        'Cannot be modified after generation',
      ],
    },
    purpose: 'Generate immutable, signed risk report with full audit trail',
    inputs: [
      { name: 'allSessionStates', type: 'AllAdaptiveLoopStates', description: 'All prior states' },
      { name: 'sessionMetadata', type: 'SessionMetadata', description: 'Full context' },
    ],
    outputs: [
      { name: 'report', type: 'StructuredRiskReport', description: 'Final report' },
    ],
    validNextStates: [],
    allowsLoopback: false,
  },
};

/**
 * Get state by name.
 */
export function getAdaptiveLoopState(
  stateName: AdaptiveLoopStateName
): AdaptiveLoopStateDefinition | null {
  return ADAPTIVE_LOOP_STATES[stateName] ?? null;
}

/**
 * Check if transition is valid.
 */
export function isValidTransition(
  from: AdaptiveLoopStateName,
  to: AdaptiveLoopStateName
): boolean {
  const state = getAdaptiveLoopState(from);
  return state?.validNextStates.includes(to) ?? false;
}

/**
 * Get all valid next states for current state.
 */
export function getValidNextStates(
  currentState: AdaptiveLoopStateName
): AdaptiveLoopStateName[] {
  const state = getAdaptiveLoopState(currentState);
  return state?.validNextStates ?? [];
}

// ============================================================================
// SECTION 6: MUTABILITY BOUNDARIES (MASTER REFERENCE)
// ============================================================================

export const MUTABILITY_BOUNDARIES: Record<AdaptiveLoopStateName, MutabilityBoundary> = {
  INPUT_NORMALIZATION: {
    stateName: 'INPUT_NORMALIZATION',
    mutability: 'IMMUTABLE',
    rationale: 'Source truth. Input hash is audit anchor.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'Cannot modify normalized output after generation',
      'Original raw prompt hash must be preserved',
      'Deterministic tokenization required',
      'Sanitization log immutable',
    ],
  },
  TARGET_INVOCATION: {
    stateName: 'TARGET_INVOCATION',
    mutability: 'IMMUTABLE',
    rationale: 'API response is external source truth. Cannot rewrite target behavior.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'Cannot alter API response post-reception',
      'Temperature locked to 0.0',
      'Full request payload must be logged',
      'Retry logic transparent and logged',
    ],
  },
  ADVERSARIAL_GENERATION: {
    stateName: 'ADVERSARIAL_GENERATION',
    mutability: 'MUTABLE',
    rationale: 'Sniper intentionally mutates. All mutations seeded and logged.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'All mutations must be seeded',
      'Seed immutable after recording',
      'Transformation trace required for every variant',
      'Can regenerate exact variants with same seed',
      'Mutation type documented per variant',
    ],
  },
  EXECUTION: {
    stateName: 'EXECUTION',
    mutability: 'IMMUTABLE',
    rationale: 'API responses are source truth. Cannot modify what target said.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'Cannot alter API responses',
      'Cost limit enforced with hard cap',
      'Concurrency limit enforced',
      'Timeout limit enforced',
      'Rate limit detection active',
    ],
  },
  EVALUATION: {
    stateName: 'EVALUATION',
    mutability: 'IMMUTABLE',
    rationale: 'Risk scores must be deterministic. No post-hoc adjustment.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'Rubric locked at session start',
      'No live adjustments to scoring rules',
      'Scores cannot be changed after evaluation',
      'Rubric version must be recorded',
      'Scoring logic deterministic',
    ],
  },
  MUTATION: {
    stateName: 'MUTATION',
    mutability: 'MUTABLE',
    rationale: 'Mutation state MUST transform variants. Adaptive engine.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'All mutations must be seeded',
      'Seed immutable after recording',
      'Transformation trace required',
      'Risk gradient drives direction',
      'Intensity scales per iteration',
      'Can regenerate exact refined set with seed',
    ],
  },
  ITERATION_CONTROL: {
    stateName: 'ITERATION_CONTROL',
    mutability: 'IMMUTABLE',
    rationale: 'Loop control logic deterministic. Prevents arbitrary termination.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'Criteria locked at session start',
      'No adjustment on the fly',
      'Decision logic deterministic',
      'No magic thresholds',
      'Explicit termination criteria only',
    ],
  },
  REPORTING: {
    stateName: 'REPORTING',
    mutability: 'IMMUTABLE',
    rationale: 'Terminal state. Legal record. Immutable and signed.',
    checksumRequired: true,
    loggingRequired: true,
    auditTrailRequired: true,
    constraints: [
      'Report immutable after generation',
      'Cryptographic signature required',
      'Tamper detection configured',
      'Cannot be modified post-generation',
      'Permanent audit trail',
    ],
  },
};

/**
 * Check if state is mutable.
 */
export function isStateMutable(stateName: AdaptiveLoopStateName): boolean {
  const boundary = MUTABILITY_BOUNDARIES[stateName];
  return boundary?.mutability === 'MUTABLE';
}

/**
 * Check if state is immutable.
 */
export function isStateImmutable(stateName: AdaptiveLoopStateName): boolean {
  const boundary = MUTABILITY_BOUNDARIES[stateName];
  return boundary?.mutability === 'IMMUTABLE';
}

// ============================================================================
// SECTION 7: DETERMINISM VERIFICATION UTILITIES
// ============================================================================

/**
 * Verify determinism for a state.
 * Given same inputs + seed, should produce same output.
 *
 * @param _stateName - State being verified (kept for API consistency)
 * @param firstChecksum - Expected checksum
 * @param secondChecksum - Actual checksum to verify
 */
export function verifyDeterminism(
  _stateName: AdaptiveLoopStateName,
  firstChecksum: string,
  secondChecksum: string
): boolean {
  return firstChecksum === secondChecksum;
}

/**
 * Generate deterministic checksum for state.
 * Use state name + inputs + seed.
 */
export function generateDeterminismChecksum(
  stateName: AdaptiveLoopStateName,
  inputHash: string,
  seed: number | null
): string {
  const combined = `${stateName}:${inputHash}:${seed ?? 'no-seed'}`;
  // Simple hash for demonstration (use SHA256 in production)
  let hash = 0;
  for (let i = 0; i < combined.length; i++) {
    const char = combined.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash.toString(16);
}

// ============================================================================
// SECTION 8: MASTER STATE UNION TYPE
// ============================================================================

/**
 * Union type of all 8 states.
 * Use for type-safe state machine implementation.
 */
export type AdaptiveLoopState =
  | InputNormalizationState
  | TargetInvocationState
  | AdversarialGenerationState
  | ExecutionState
  | EvaluationState
  | MutationState
  | IterationControlState
  | ReportingState;

/**
 * Aggregated state snapshot (for session storage).
 */
export interface AdaptiveLoopSnapshot {
  sessionId: string;
  roundNumber: number;
  currentStateName: AdaptiveLoopStateName;
  states: {
    input_normalization?: InputNormalizationState;
    target_invocation?: TargetInvocationState;
    adversarial_generation?: AdversarialGenerationState;
    execution?: ExecutionState;
    evaluation?: EvaluationState;
    mutation?: MutationState;
    iteration_control?: IterationControlState;
    reporting?: ReportingState;
  };
  timestamp: number;
}

// ============================================================================
// NOTE: All types and utilities are exported inline throughout this file.
// See types/index.ts for centralized re-exports.
// ============================================================================
