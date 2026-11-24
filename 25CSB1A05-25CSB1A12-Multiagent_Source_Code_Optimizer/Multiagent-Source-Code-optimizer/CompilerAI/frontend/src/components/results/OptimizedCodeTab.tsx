import React, { useState, useEffect, useRef } from 'react';
import EditorImport from '@monaco-editor/react';
import { Copy, Check, ArrowRightLeft, Sparkles, AlertTriangle, LocateFixed } from 'lucide-react';
import { OptimizationResult } from '../../features/run/runTypes';
import { getTransformationLine } from '../../utils/transformationLineResolver';
import { sanitizeVendor } from '../../utils/sanitizeVendor';

const Editor = ((EditorImport as unknown as { default?: typeof EditorImport }).default ||
  EditorImport) as typeof EditorImport;

interface OptimizedCodeTabProps {
  optimizationResult: OptimizationResult | null;
  language: string;
  onApplyToSource: () => void;
  isDark?: boolean;
  sourceCode?: string;
  onNavigateToLine?: (line: number) => void;
}

export const OptimizedCodeTab: React.FC<OptimizedCodeTabProps> = ({
  optimizationResult,
  language,
  onApplyToSource,
  isDark = false,
  sourceCode = '',
  onNavigateToLine,
}) => {
  const [copied, setCopied] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState<number>(380);
  const [isDraggingCol, setIsDraggingCol] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isDraggingCol) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const newWidth = e.clientX - rect.left;
      const minWidth = 260;
      const maxWidth = Math.max(minWidth, rect.width - 260);
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setSidebarWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsDraggingCol(false);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDraggingCol]);

  if (!optimizationResult) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-slate-400">
        <Sparkles className="w-8 h-8 mb-2 stroke-1" />
        <p className="text-xs font-medium text-slate-500">
          No optimization result available.
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Run Full Pipeline or Optimize mode to generate optimized code.
        </p>
      </div>
    );
  }

  const handleCopy = () => {
    if (optimizationResult.optimized_code) {
      navigator.clipboard.writeText(optimizationResult.optimized_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isUnverified = Boolean(
    optimizationResult.metrics?.unverified ||
    optimizationResult.metrics?.support_level === 'analysis_only'
  );
  const supportLevel = String(optimizationResult.metrics?.support_level || (isUnverified ? 'analysis_only' : 'full'));
  const evidenceTier = optimizationResult.metrics?.evidence_tier ? String(optimizationResult.metrics.evidence_tier) : null;
  const internalStages: Array<{ name: string; status: string; seconds?: number }> =
    Array.isArray(optimizationResult.raw_result?.outcome?.stages)
      ? optimizationResult.raw_result.outcome.stages
      : [];

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Top Banner & Actions */}
      <div className="h-10 px-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50 shrink-0">
        <div className="flex items-center gap-2.5 flex-wrap">
          <span className="text-xs font-bold text-slate-700">
            {isUnverified ? 'STATIC ANALYSIS (UNVERIFIED)' : 'OPTIMIZED OUTPUT'}
          </span>
          {isUnverified && (
            <span className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full border border-amber-200">
              ANALYSIS ONLY{evidenceTier ? ` · ${evidenceTier}` : ''} · UNVERIFIED
            </span>
          )}
          {!isUnverified && evidenceTier && (
            <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full border border-emerald-200">
              {supportLevel.toUpperCase()} · {evidenceTier}
            </span>
          )}
          {optimizationResult.is_demo && (
            <span className="text-[10px] font-bold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full border border-amber-200">
              DEMO RESULT (MOCK AGENT)
            </span>
          )}
          {optimizationResult.duration_ms > 0 && (
            <span className="text-[11px] font-mono text-slate-400">
              {optimizationResult.duration_ms}ms
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Apply to Source Button (only for verified optimization outputs) */}
          {optimizationResult.optimized_code && !isUnverified && (
            <button
              onClick={() => {
                if (confirm('Replace source code editor contents with this optimized version?')) {
                  onApplyToSource();
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 rounded-lg text-xs font-semibold transition-colors"
            >
              <ArrowRightLeft className="w-3.5 h-3.5" />
              Apply to Source
            </button>
          )}

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            disabled={!optimizationResult.optimized_code}
            className="flex items-center gap-1.5 px-2.5 py-1 text-slate-600 hover:text-slate-900 border border-slate-200 rounded-lg text-xs font-semibold transition-colors disabled:opacity-40"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            Copy
          </button>
        </div>
      </div>

      {/* Unverified / Degraded Banner */}
      {isUnverified && (
        <div className="px-4 py-1.5 bg-amber-50 border-b border-amber-200 flex items-center gap-2 text-xs text-amber-900 shrink-0">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
          <span>
            Executable verification was not performed ({supportLevel}). Source code is shown unchanged; review diagnostics below for remediation.
          </span>
        </div>
      )}

      {/* Transformations & Editor Split View */}
      <div ref={containerRef} className="flex-1 min-h-0 flex flex-col lg:flex-row relative">
        {/* Transformations, Stages, Metrics & Diagnostics Sidebar (LEFT) */}
        <div
          style={sidebarWidth ? { width: `${sidebarWidth}px` } : undefined}
          className={`${!sidebarWidth ? 'w-full lg:w-96' : ''} p-3.5 bg-slate-50/70 dark:bg-slate-900/60 overflow-y-auto space-y-3.5 border-b lg:border-b-0 border-slate-200 dark:border-slate-800 shrink-0`}
        >
          <div>
            <div className="flex items-center justify-between mb-1">
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                Applied Transformations
              </h4>
              {optimizationResult.transformations.length > 0 && (
                <span className="text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 px-2 py-0.5 rounded-full">
                  {optimizationResult.transformations.length}
                </span>
              )}
            </div>
            <p className="text-[10px] text-slate-400 dark:text-slate-500 mb-2">
              Click any transformation to jump to its line in Source Code
            </p>

            {optimizationResult.transformations.length > 0 ? (
              <ul className="space-y-1.5">
                {optimizationResult.transformations.map((trans, idx) => {
                  const targetLine = getTransformationLine(
                    trans,
                    sourceCode,
                    optimizationResult.optimized_code,
                    idx
                  );

                  return (
                    <li
                      key={idx}
                      onClick={() => onNavigateToLine?.(targetLine)}
                      className="text-xs bg-white dark:bg-slate-800 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 shadow-2xs leading-relaxed hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-xs transition-all cursor-pointer group"
                      title={`Click to jump to line ${targetLine} in original source code`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-start gap-2 flex-1 min-w-0">
                          <span className="text-[10px] font-bold px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded shrink-0 mt-0.5 group-hover:bg-blue-50 dark:group-hover:bg-blue-950 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                            #{idx + 1}
                          </span>
                          <span className="flex-1 break-words">{sanitizeVendor(trans)}</span>
                        </div>

                        {/* Interactive Line Navigation Badge */}
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            onNavigateToLine?.(targetLine);
                          }}
                          className="flex items-center gap-1 text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/70 hover:bg-blue-100 dark:hover:bg-blue-900 border border-blue-200 dark:border-blue-800/80 rounded px-1.5 py-0.5 transition-colors shrink-0 shadow-2xs"
                          title={`Navigate to line ${targetLine} in source editor`}
                        >
                          <LocateFixed className="w-3 h-3 text-blue-500 group-hover:scale-110 transition-transform" />
                          <span>Line {targetLine}</span>
                        </button>
                      </div>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="text-xs text-slate-400 italic">None reported</p>
            )}
          </div>

          {internalStages.length > 0 && (
            <div>
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Pipeline Stages
              </h4>
              <div className="bg-white dark:bg-slate-800 p-2 rounded-lg border border-slate-200 dark:border-slate-700 space-y-1">
                {internalStages.map((st, idx) => (
                  <div key={`${st.name}-${idx}`} className="flex items-center justify-between text-xs">
                    <span className="font-mono text-slate-600 dark:text-slate-400">{sanitizeVendor(st.name)}</span>
                    <span
                      className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${st.status === 'ok'
                          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                          : st.status === 'skipped'
                            ? 'bg-amber-50 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
                            : 'bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300'
                        }`}
                    >
                      {st.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {Object.keys(optimizationResult.metrics).length > 0 && (
            <div>
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Optimization Metrics
              </h4>
              <div className="bg-white dark:bg-slate-800 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700 space-y-1">
                {Object.entries(optimizationResult.metrics).map(([key, val]) => (
                  <div key={key} className="flex justify-between text-xs gap-2">
                    <span className="text-slate-500 dark:text-slate-400">{key}:</span>
                    <span className="font-mono font-medium text-slate-800 dark:text-slate-200 truncate">{sanitizeVendor(String(val))}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {optimizationResult.diagnostics && optimizationResult.diagnostics.length > 0 && (
            <div>
              <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                Diagnostics &amp; Remediation
              </h4>
              <ul className="space-y-1">
                {optimizationResult.diagnostics.map((diag, idx) => (
                  <li
                    key={idx}
                    className={`text-xs p-2 rounded-lg border ${isUnverified
                        ? 'bg-amber-50/70 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200'
                        : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300'
                      }`}
                  >
                    {sanitizeVendor(diag)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Resizable Divider between Transformations and Monaco */}
        <div
          onMouseDown={(e) => {
            e.preventDefault();
            setIsDraggingCol(true);
          }}
          className="hidden lg:flex w-2 bg-slate-200/90 hover:bg-blue-500 dark:bg-slate-800 dark:hover:bg-blue-600 cursor-col-resize transition-colors items-center justify-center group shrink-0 select-none z-10"
          title="Drag left/right to resize Applied Transformations"
        >
          <div className="h-10 w-1 rounded-full bg-slate-400 dark:bg-slate-600 group-hover:bg-blue-200 transition-colors" />
        </div>

        {/* Fullscreen overlay during horizontal dragging */}
        {isDraggingCol && (
          <div className="fixed inset-0 z-50 cursor-col-resize select-none" />
        )}

        {/* Monaco Viewer (RIGHT) */}
        <div className="flex-1 min-h-[160px] relative">
          <Editor
            height="100%"
            language={language === 'c' || language === 'cpp' ? 'cpp' : language}
            value={optimizationResult.optimized_code || '// No code returned'}
            theme={isDark ? 'vs-dark' : 'vs'}
            options={{
              minimap: { enabled: false },
              fontSize: 12,
              fontFamily: "'JetBrains Mono', Consolas, monospace",
              lineNumbers: 'on',
              readOnly: true,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              padding: { top: 8, bottom: 8 },
            }}
          />
        </div>
      </div>
    </div>
  );
};
