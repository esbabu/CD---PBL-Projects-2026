import React from 'react';
import { Terminal } from 'lucide-react';
import { RunStatus } from '../../features/run/runTypes';
import { sanitizeVendor } from '../../utils/sanitizeVendor';

interface OutputTabProps {
  outputLog: string | null;
  runStatus: RunStatus;
}

export const OutputTab: React.FC<OutputTabProps> = ({ outputLog }) => {
  if (!outputLog) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-slate-400">
        <Terminal className="w-8 h-8 mb-2 stroke-1" />
        <p className="text-xs font-medium text-slate-500">
          No execution output recorded.
        </p>
        <p className="text-[11px] text-slate-400 mt-1 max-w-sm text-center">
          Run Full Pipeline, Optimize, or Security to view stage execution status, complexity diff, verification evidence, and diagnostics.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full p-4 font-mono text-xs text-slate-800 bg-slate-50 overflow-auto whitespace-pre-wrap">
      {sanitizeVendor(outputLog)}
    </div>
  );
};
