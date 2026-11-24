import React from 'react';
import { Network, CheckCircle2, Clock, AlertCircle, AlertTriangle, PlayCircle, Ban } from 'lucide-react';
import { PipelineStageState, RunStatus } from '../../features/run/runTypes';
import { sanitizeVendor } from '../../utils/sanitizeVendor';

interface LivePipelinePanelProps {
  stages: PipelineStageState[];
  runStatus: RunStatus;
  currentRunId: string | null;
}

export const LivePipelinePanel: React.FC<LivePipelinePanelProps> = ({
  stages,
  runStatus,
  currentRunId,
}) => {
  const isIdle = runStatus === 'idle';

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
      {/* Panel Header */}
      <div className="h-10 border-b border-slate-200 dark:border-slate-800 px-3 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/80">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          <span className="text-xs font-bold text-slate-700 dark:text-slate-200 tracking-wider">LIVE PIPELINE</span>
        </div>
        {currentRunId && (
          <div className="text-[11px] font-mono text-slate-400">
            Run: {currentRunId}
          </div>
        )}
      </div>

      {/* Main Body */}
      <div className="flex-1 min-h-0 flex flex-col items-center justify-center p-6 overflow-y-auto">
        {isIdle ? (
          /* Idle visual matching screenshot */
          <div className="flex flex-col items-center text-center max-w-sm">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-4 h-4 rounded-full border-2 border-slate-300 bg-white" />
              <div className="w-8 h-0.5 bg-slate-200" />
              <div className="w-5 h-5 rounded-full border-2 border-blue-500 bg-blue-50 flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-blue-500" />
              </div>
              <div className="w-8 h-0.5 bg-slate-200" />
              <div className="w-4 h-4 rounded-full border-2 border-slate-300 bg-white" />
            </div>
            <p className="text-sm text-slate-500 font-medium leading-relaxed">
              Pipeline will run here when you execute the Full Pipeline or Run.
            </p>
          </div>
        ) : (
          /* Active Pipeline Stages */
          <div className="w-full max-w-md space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <span className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                Execution Sequence
              </span>
              <span
                className={`text-[11px] font-semibold px-2 py-0.5 rounded-full capitalize ${
                  runStatus === 'completed'
                    ? 'bg-emerald-100 text-emerald-700'
                    : runStatus === 'running'
                    ? 'bg-blue-100 text-blue-700 animate-pulse'
                    : runStatus === 'partially_completed' || runStatus === 'cancelled'
                    ? 'bg-amber-100 text-amber-800'
                    : 'bg-rose-100 text-rose-700'
                }`}
              >
                {runStatus.replace('_', ' ')}
              </span>
            </div>

            <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-200">
              {stages.map((stage) => {
                let icon = <Clock className="w-3.5 h-3.5 text-slate-400" />;
                let dotClass = 'border-slate-300 bg-white';
                let cardClass = 'border-slate-200 bg-white opacity-60';

                if (stage.status === 'running') {
                  icon = <PlayCircle className="w-3.5 h-3.5 text-blue-600 animate-spin" />;
                  dotClass = 'border-blue-600 bg-blue-100 ring-4 ring-blue-50';
                  cardClass = 'border-blue-200 bg-blue-50/50 shadow-sm opacity-100';
                } else if (stage.status === 'completed') {
                  icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />;
                  dotClass = 'border-emerald-600 bg-emerald-100';
                  cardClass = 'border-slate-200 bg-white opacity-100';
                } else if (stage.status === 'degraded') {
                  icon = <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />;
                  dotClass = 'border-amber-500 bg-amber-100';
                  cardClass = 'border-amber-200 bg-amber-50/50 opacity-100';
                } else if (stage.status === 'failed') {
                  icon = <AlertCircle className="w-3.5 h-3.5 text-rose-600" />;
                  dotClass = 'border-rose-600 bg-rose-100';
                  cardClass = 'border-rose-200 bg-rose-50/40 opacity-100';
                } else if (stage.status === 'cancelled') {
                  icon = <Ban className="w-3.5 h-3.5 text-amber-600" />;
                  dotClass = 'border-amber-500 bg-amber-100';
                  cardClass = 'border-amber-200 bg-amber-50/40 opacity-90';
                }

                return (
                  <div key={stage.id} className="relative">
                    {/* Timeline Node */}
                    <div
                      className={`absolute -left-6 top-2 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all ${dotClass}`}
                    >
                      {icon}
                    </div>

                    {/* Stage Card */}
                    <div className={`p-3 rounded-xl border transition-all ${cardClass}`}>
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-800">
                          {stage.label}
                        </span>
                        <span
                          className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded ${
                            stage.status === 'completed'
                              ? 'bg-emerald-50 text-emerald-700'
                              : stage.status === 'degraded'
                              ? 'bg-amber-50 text-amber-800'
                              : stage.status === 'running'
                              ? 'bg-blue-50 text-blue-700 font-bold'
                              : stage.status === 'failed'
                              ? 'bg-rose-50 text-rose-700'
                              : 'bg-slate-100 text-slate-500'
                          }`}
                        >
                          {stage.status}
                        </span>
                      </div>

                      {stage.message && (
                        <p className="text-xs text-slate-500 mt-1">
                          {sanitizeVendor(stage.message)}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
