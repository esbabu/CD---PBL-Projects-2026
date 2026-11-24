import React from 'react';
import { ResultsTabs } from './ResultsTabs';
import { OutputTab } from './OutputTab';
import { OptimizedCodeTab } from './OptimizedCodeTab';
import { SecurityTab } from './SecurityTab';
import { MessagesTab } from './MessagesTab';
import {
  ActiveTab,
  OptimizationResult,
  SecurityResult,
  RunMessage,
  RunStatus,
} from '../../features/run/runTypes';

interface ResultsPanelProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  outputLog: string | null;
  optimizationResult: OptimizationResult | null;
  securityResult: SecurityResult | null;
  messages: RunMessage[];
  runStatus: RunStatus;
  language: string;
  onApplyToSource: () => void;
  isDark?: boolean;
  isStale?: boolean;
  height?: number;
  sourceCode?: string;
  onNavigateToLine?: (line: number) => void;
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({
  activeTab,
  onTabChange,
  outputLog,
  optimizationResult,
  securityResult,
  messages,
  runStatus,
  language,
  onApplyToSource,
  isDark = false,
  isStale = false,
  height,
  sourceCode,
  onNavigateToLine,
}) => {
  return (
    <div
      style={height ? { height: `${height}px` } : undefined}
      className={`${!height ? 'h-96 lg:h-[42vh]' : ''} border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col shrink-0 shadow-sm transition-[height] duration-75`}
    >
      {/* Tab Navigation */}
      <ResultsTabs
        activeTab={activeTab}
        onTabChange={onTabChange}
        hasOptimizedCode={!!optimizationResult?.optimized_code}
        isUnverified={Boolean(
          optimizationResult?.metrics?.unverified ||
            optimizationResult?.metrics?.support_level === 'analysis_only'
        )}
        securityFindingsCount={securityResult?.findings.length || 0}
        messagesCount={messages.length}
        isStale={isStale}
      />

      {/* Tab Content Body */}
      <div className="flex-1 min-h-0 relative">
        {activeTab === 'output' && (
          <OutputTab outputLog={outputLog} runStatus={runStatus} />
        )}
        {activeTab === 'optimized_code' && (
          <OptimizedCodeTab
            optimizationResult={optimizationResult}
            language={language}
            onApplyToSource={onApplyToSource}
            isDark={isDark}
            sourceCode={sourceCode}
            onNavigateToLine={onNavigateToLine}
          />
        )}
        {activeTab === 'security' && (
          <SecurityTab
            securityResult={securityResult}
            onNavigateToLine={onNavigateToLine}
            isDark={isDark}
          />
        )}
        {activeTab === 'messages' && <MessagesTab messages={messages} />}
      </div>
    </div>
  );
};
