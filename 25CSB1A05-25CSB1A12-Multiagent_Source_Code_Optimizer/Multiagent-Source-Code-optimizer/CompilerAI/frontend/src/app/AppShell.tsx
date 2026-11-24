import React, { useReducer, useEffect, useState } from 'react';
import { AppHeader } from '../components/header/AppHeader';
import { MainWorkspace } from '../components/workspace/MainWorkspace';
import { ResultsPanel } from '../components/results/ResultsPanel';
import { runReducer, initialRunState } from '../features/run/runReducer';
import { useRunController } from '../features/run/useRunController';
import { RunMode, InferenceMode, ActiveTab, HealthStatus } from '../features/run/runTypes';
import { runApi } from '../services/runApi';

export const AppShell: React.FC = () => {
  const [state, dispatch] = useReducer(runReducer, initialRunState);
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isDark, setIsDark] = useState<boolean>(false);
  const [resultsHeight, setResultsHeight] = useState<number>(() => {
    if (typeof window !== 'undefined' && window.innerHeight) {
      return Math.max(340, Math.round(window.innerHeight * 0.42));
    }
    return 380;
  });
  const [isDraggingVertical, setIsDraggingVertical] = useState<boolean>(false);
  const [targetLine, setTargetLine] = useState<{ line: number; timestamp: number } | null>(null);
  const { startRun, stopRun } = useRunController(state, dispatch);

  // Expose automation hook for test case runner
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).__COMPILER_AI__ = {
        dispatch,
        startRun,
        stopRun,
        getState: () => state,
        setLanguage: (lang: string) => dispatch({ type: 'SET_LANGUAGE', payload: lang }),
        setSourceCode: (code: string) => dispatch({ type: 'SET_SOURCE_CODE', payload: code }),
        setMode: (mode: RunMode) => dispatch({ type: 'SET_MODE', payload: mode }),
        setInferenceMode: (inf: InferenceMode) => dispatch({ type: 'SET_INFERENCE_MODE', payload: inf }),
        setActiveTab: (tab: ActiveTab) => dispatch({ type: 'SET_ACTIVE_TAB', payload: tab }),
        setResultsHeight: (h: number) => setResultsHeight(h),
      };
    }
  }, [state, startRun, stopRun]);

  const handleNavigateToLine = (line: number) => {
    setTargetLine({ line, timestamp: Date.now() });
  };

  // Sync Tailwind dark mode class
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  // Handle vertical panel resizing
  useEffect(() => {
    if (!isDraggingVertical) return;

    const handleMouseMove = (e: MouseEvent) => {
      const minHeight = 180;
      const maxHeight = window.innerHeight * 0.75;
      const newHeight = window.innerHeight - e.clientY;
      if (newHeight >= minHeight && newHeight <= maxHeight) {
        setResultsHeight(newHeight);
      }
    };

    const handleMouseUp = () => {
      setIsDraggingVertical(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingVertical]);

  // Health check on mount & poll
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await runApi.checkHealth();
        if (res && res.status === 'healthy') {
          setBackendConnected(true);
          setHealth(res);
        } else {
          setBackendConnected(false);
          setHealth(null);
        }
      } catch {
        setBackendConnected(false);
        setHealth(null);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleModeChange = (mode: RunMode) => {
    dispatch({ type: 'SET_MODE', payload: mode });
  };

  const handleInferenceModeChange = (mode: InferenceMode) => {
    dispatch({ type: 'SET_INFERENCE_MODE', payload: mode });
  };

  const handleLanguageChange = (lang: string) => {
    dispatch({ type: 'SET_LANGUAGE', payload: lang });
  };

  const handleSourceChange = (code: string) => {
    dispatch({ type: 'SET_SOURCE_CODE', payload: code });
  };

  const handleTabChange = (tab: ActiveTab) => {
    dispatch({ type: 'SET_ACTIVE_TAB', payload: tab });
  };

  const handleRunClick = () => {
    startRun();
  };

  const handleStopClick = () => {
    stopRun();
  };

  const handleApplyToSource = () => {
    dispatch({ type: 'APPLY_OPTIMIZED_TO_SOURCE' });
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-100 dark:bg-slate-950 overflow-hidden font-sans transition-colors">
      {/* Top Header */}
      <AppHeader
        mode={state.mode}
        onModeChange={handleModeChange}
        inferenceMode={state.inferenceMode}
        onInferenceModeChange={handleInferenceModeChange}
        status={state.status}
        onRunClick={handleRunClick}
        onStopClick={handleStopClick}
        backendConnected={backendConnected}
        health={health}
        isDark={isDark}
        onToggleTheme={() => setIsDark((prev) => !prev)}
      />

      {/* Main Center Workspace */}
      <MainWorkspace
        sourceCode={state.sourceCode}
        language={state.language}
        onSourceChange={handleSourceChange}
        onLanguageChange={handleLanguageChange}
        stages={state.stages}
        runStatus={state.status}
        currentRunId={state.currentRunId}
        isDark={isDark}
        targetLine={targetLine}
      />

      {/* Resizable Divider between Workspace and Lower Half */}
      <div
        onMouseDown={(e) => {
          e.preventDefault();
          setIsDraggingVertical(true);
        }}
        className="h-2 w-full bg-slate-200/90 hover:bg-blue-500 dark:bg-slate-800 dark:hover:bg-blue-600 cursor-row-resize transition-colors flex items-center justify-center group shrink-0 select-none z-20"
        title="Drag up or down to allocate more or less space to the lower half"
      >
        <div className="w-14 h-1 rounded-full bg-slate-400 dark:bg-slate-600 group-hover:bg-blue-200 transition-colors" />
      </div>

      {/* Fullscreen overlay to capture mouse moves during vertical dragging */}
      {isDraggingVertical && (
        <div className="fixed inset-0 z-50 cursor-row-resize select-none" />
      )}

      {/* Bottom Results Panel */}
      <ResultsPanel
        height={resultsHeight}
        activeTab={state.activeTab}
        onTabChange={handleTabChange}
        outputLog={state.outputLog}
        optimizationResult={state.optimizationResult}
        securityResult={state.securityResult}
        messages={state.messages}
        runStatus={state.status}
        language={state.language}
        onApplyToSource={handleApplyToSource}
        isDark={isDark}
        isStale={state.isStale}
        sourceCode={state.sourceCode}
        onNavigateToLine={handleNavigateToLine}
      />
    </div>
  );
};
