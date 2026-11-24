import React from 'react';
import { Cpu, Play, Square, Network, Zap, Shield, Sparkles, Code2, Sun, Moon } from 'lucide-react';
import { RunMode, InferenceMode, RunStatus, HealthStatus } from '../../features/run/runTypes';
import { sanitizeVendor } from '../../utils/sanitizeVendor';

interface AppHeaderProps {
  mode: RunMode;
  onModeChange: (mode: RunMode) => void;
  inferenceMode: InferenceMode;
  onInferenceModeChange: (mode: InferenceMode) => void;
  status: RunStatus;
  onRunClick: () => void;
  onStopClick: () => void;
  backendConnected: boolean;
  health: HealthStatus | null;
  isDark: boolean;
  onToggleTheme: () => void;
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  mode,
  onModeChange,
  inferenceMode,
  onInferenceModeChange,
  status,
  onRunClick,
  onStopClick,
  backendConnected,
  health,
  isDark,
  onToggleTheme,
}) => {
  const isRunning = status === 'running' || status === 'queued';

  const optMode = health?.adapters?.optimization ?? 'unknown';
  const secMode = health?.adapters?.security ?? 'unknown';
  const llmStatus = health?.llm_connection ?? 'not_configured';

  let statusLabel = 'Backend Offline';
  let statusTooltip = 'Backend disconnected or starting...';
  if (backendConnected && health) {
    if (optMode === 'real' && secMode === 'real') {
      statusLabel = 'Real Agents Ready';
    } else if (optMode === 'real' || secMode === 'real') {
      statusLabel = 'Hybrid Agents Ready';
    } else {
      statusLabel = 'Mock Engine Ready';
    }
    statusTooltip = sanitizeVendor(`Backend healthy (v${health.version}) | Optimization: ${optMode} | Security: ${secMode} | LLM: ${llmStatus}`);
  }

  const llmConnected = llmStatus === 'connected';
  const rawModel = health?.ollama?.active_model;
  const activeModel = rawModel ? sanitizeVendor(rawModel) : null;
  const llmBadgeLabel = llmConnected
    ? `LLM Online${activeModel ? ` (${activeModel})` : ''}`
    : 'LLM Offline';
  const llmTooltip = sanitizeVendor(
    llmConnected
      ? `Ollama connected at ${health?.ollama?.base_url || 'localhost:11434'} | Installed: ${(health?.ollama?.models || []).join(', ')}`
      : health?.ollama?.remediation || 'Ollama is unreachable; deterministic heuristics remain active.'
  );

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-4 flex items-center justify-between gap-2 shrink-0 select-none overflow-x-auto">
      {/* Left: Branding */}
      <div className="flex items-center gap-3 shrink-0">
        <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-200 dark:shadow-none">
          <Cpu className="w-6 h-6" />
        </div>
        <div>
          <div className="font-bold text-slate-900 dark:text-slate-100 text-lg tracking-tight leading-none">
            CompilerAI
          </div>
          <div className="text-[10px] font-semibold tracking-wider text-slate-400 mt-0.5">
            OPTIMIZATION STUDIO
          </div>
        </div>
      </div>

      {/* Center: Mode & Inference Selectors */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Run Mode Selector */}
        <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 gap-1">
          <button
            onClick={() => onModeChange('pipeline')}
            disabled={isRunning}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-60 ${
              mode === 'pipeline'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700'
            }`}
          >
            <Network className="w-3.5 h-3.5" />
            Full Pipeline
          </button>

          <button
            onClick={() => onModeChange('optimize')}
            disabled={isRunning}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-60 ${
              mode === 'optimize'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            Optimize
          </button>

          <button
            onClick={() => onModeChange('security')}
            disabled={isRunning}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-60 ${
              mode === 'security'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700'
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            Security
          </button>
        </div>

        {/* Inference Selector */}
        <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-xl border border-slate-200 dark:border-slate-700 gap-1">
          <button
            onClick={() => onInferenceModeChange('llm')}
            disabled={isRunning}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-60 ${
              inferenceMode === 'llm'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            LLM
          </button>

          <button
            onClick={() => onInferenceModeChange('heuristics')}
            disabled={isRunning}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all disabled:opacity-60 ${
              inferenceMode === 'heuristics'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            Heuristics
          </button>
        </div>
      </div>

      {/* Right: Service Status, LLM Status, Theme Toggle & Run Action */}
      <div className="flex items-center gap-2.5 shrink-0">
        {/* LLM Status Badge */}
        {backendConnected && (
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border text-xs font-medium ${
              llmConnected
                ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700'
            }`}
            title={llmTooltip}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                llmConnected ? 'bg-emerald-500' : 'bg-slate-400'
              }`}
            />
            <span>{llmBadgeLabel}</span>
          </div>
        )}

        {/* Service Status Badge */}
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-medium ${
            backendConnected
              ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
              : 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800'
          }`}
          title={statusTooltip}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              backendConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
            }`}
          />
          <span>{statusLabel}</span>
        </div>

        {/* Light / Dark Theme Toggle */}
        <button
          onClick={onToggleTheme}
          title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          aria-label="Toggle theme"
          className="p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors cursor-pointer"
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
        </button>

        {/* Primary Run / Stop Button */}
        {isRunning ? (
          <button
            onClick={onStopClick}
            className="flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 shadow-sm shadow-rose-200 dark:shadow-none transition-all cursor-pointer"
          >
            <Square className="w-3.5 h-3.5 fill-current" />
            Stop
          </button>
        ) : (
          <button
            onClick={onRunClick}
            disabled={!backendConnected}
            title={!backendConnected ? 'Waiting for backend service...' : 'Execute selected pipeline'}
            className="flex items-center gap-2 px-6 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-sm shadow-blue-200 dark:shadow-none transition-all cursor-pointer hover:shadow disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            Run
          </button>
        )}
      </div>
    </header>
  );
};
