import React from 'react';
import { SourceCodePanel } from './SourceCodePanel';
import { LivePipelinePanel } from './LivePipelinePanel';
import { PipelineStageState, RunStatus } from '../../features/run/runTypes';

interface MainWorkspaceProps {
  sourceCode: string;
  language: string;
  onSourceChange: (code: string) => void;
  onLanguageChange: (lang: string) => void;
  stages: PipelineStageState[];
  runStatus: RunStatus;
  currentRunId: string | null;
  isDark: boolean;
  targetLine?: { line: number; timestamp: number } | null;
}

export const MainWorkspace: React.FC<MainWorkspaceProps> = ({
  sourceCode,
  language,
  onSourceChange,
  onLanguageChange,
  stages,
  runStatus,
  currentRunId,
  isDark,
  targetLine,
}) => {
  return (
    <div className="flex-1 min-h-0 p-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Left Column: Source Code Editor */}
      <SourceCodePanel
        sourceCode={sourceCode}
        language={language}
        onSourceChange={onSourceChange}
        onLanguageChange={onLanguageChange}
        readOnly={runStatus === 'running'}
        isDark={isDark}
        targetLine={targetLine}
      />

      {/* Right Column: Live Pipeline */}
      <LivePipelinePanel
        stages={stages}
        runStatus={runStatus}
        currentRunId={currentRunId}
      />
    </div>
  );
};
