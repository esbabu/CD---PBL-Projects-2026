export type RunMode = 'pipeline' | 'optimize' | 'security';
export type InferenceMode = 'llm' | 'heuristics';
export type StageStatus = 'pending' | 'running' | 'completed' | 'degraded' | 'failed' | 'skipped' | 'cancelled';
export type RunStatus = 'idle' | 'queued' | 'running' | 'completed' | 'partially_completed' | 'failed' | 'cancelled';
export type ActiveTab = 'output' | 'optimized_code' | 'security' | 'messages';

export interface OllamaStatusInfo {
  reachable: boolean;
  base_url: string;
  version?: string | null;
  models: string[];
  active_model?: string | null;
  roles?: Record<string, string | null>;
  reason_kind?: string;
  remediation?: string;
}

export interface ToolchainStatusInfo {
  status: string;
  backend?: string;
  remediation?: string | null;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  demo_mode: boolean;
  adapters: {
    optimization: 'real' | 'mock' | string;
    security: 'real' | 'mock' | string;
  };
  llm_connection: 'connected' | 'unreachable' | 'no_models' | 'not_configured' | string;
  ollama?: OllamaStatusInfo;
  toolchains?: Record<string, ToolchainStatusInfo>;
  supported_modes: string[];
  supported_languages: string[];
}

export interface SecurityFinding {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  description: string;
  line_number?: number;
  rule_or_cwe?: string;
  remediation?: string;
}

export interface OptimizationResult {
  run_id: string;
  status: string;
  optimized_code?: string;
  transformations: string[];
  metrics: Record<string, any>;
  raw_result: Record<string, any>;
  diagnostics: string[];
  duration_ms: number;
  is_demo: boolean;
}

export interface SecurityResult {
  run_id: string;
  status: string;
  source_kind: 'original' | 'optimized';
  findings: SecurityFinding[];
  raw_result: Record<string, any>;
  diagnostics: string[];
  duration_ms: number;
  is_demo: boolean;
}

export interface RunMessage {
  id: string;
  timestamp: string;
  category: 'info' | 'warning' | 'error' | 'lifecycle' | 'demo';
  message: string;
  details?: string;
}

export interface PipelineStageState {
  id: 'source' | 'optimization' | 'security' | 'completed';
  label: string;
  agent?: string;
  status: StageStatus;
  message?: string;
  duration_ms?: number;
}

export interface RunState {
  currentRunId: string | null;
  mode: RunMode;
  inferenceMode: InferenceMode;
  language: string;
  sourceCode: string;
  status: RunStatus;
  activeTab: ActiveTab;
  stages: PipelineStageState[];
  optimizationResult: OptimizationResult | null;
  securityResult: SecurityResult | null;
  outputLog: string | null;
  messages: RunMessage[];
  isStale: boolean;
}
