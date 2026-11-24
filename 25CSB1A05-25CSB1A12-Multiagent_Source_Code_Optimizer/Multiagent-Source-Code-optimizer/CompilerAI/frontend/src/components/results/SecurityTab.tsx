import React from 'react';
import { Shield, CheckCircle2, LocateFixed } from 'lucide-react';
import { SecurityResult } from '../../features/run/runTypes';
import { sanitizeVendor } from '../../utils/sanitizeVendor';

interface SecurityTabProps {
  securityResult: SecurityResult | null;
  onNavigateToLine?: (line: number) => void;
  isDark?: boolean;
}

export const SecurityTab: React.FC<SecurityTabProps> = ({
  securityResult,
  onNavigateToLine,
}) => {
  if (!securityResult) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-6 text-slate-400">
        <Shield className="w-8 h-8 mb-2 stroke-1" />
        <p className="text-xs font-medium text-slate-500">
          No security assessment available.
        </p>
        <p className="text-[11px] text-slate-400 mt-1">
          Run Full Pipeline or Security mode to perform security analysis.
        </p>
      </div>
    );
  }

  const { findings, source_kind, is_demo, duration_ms } = securityResult;

  // Enforce 1 card per line maximum: consolidate any findings on the same line into one card
  const dedupedFindings = React.useMemo(() => {
    const lineMap = new Map<number, (typeof findings)[0]>();
    const unlocated: (typeof findings)[0][] = [];
    const sevRank: Record<string, number> = { critical: 5, high: 4, medium: 3, low: 2, info: 1 };

    for (const f of findings) {
      if (f.line_number !== null && f.line_number !== undefined) {
        const existing = lineMap.get(f.line_number);
        if (!existing) {
          lineMap.set(f.line_number, f);
        } else {
          const currRank = sevRank[f.severity.toLowerCase()] || 2;
          const exRank = sevRank[existing.severity.toLowerCase()] || 2;
          const higherSev = currRank > exRank ? f.severity : existing.severity;
          const higherTitle = currRank > exRank ? f.title : existing.title;

          const cwes = (existing.rule_or_cwe || '')
            .split(',')
            .map((s) => s.trim())
            .filter((s) => s && s !== 'CWE-Unknown');
          for (const c of (f.rule_or_cwe || '').split(',').map((s) => s.trim())) {
            if (c && c !== 'CWE-Unknown' && !cwes.includes(c)) {
              cwes.push(c);
            }
          }
          const mergedCwe = cwes.length > 0 ? cwes.join(', ') : (existing.rule_or_cwe || f.rule_or_cwe);
          const mergedDesc = f.description && !existing.description.includes(f.description)
            ? `${existing.description} | ${f.description}`
            : existing.description;

          lineMap.set(f.line_number, {
            ...existing,
            title: higherTitle,
            severity: higherSev,
            rule_or_cwe: mergedCwe,
            description: mergedDesc,
            remediation: existing.remediation || f.remediation,
          });
        }
      } else {
        unlocated.push(f);
      }
    }
    return [
      ...Array.from(lineMap.values()).sort((a, b) => (a.line_number || 0) - (b.line_number || 0)),
      ...unlocated,
    ];
  }, [findings]);

  const severityCounts = {
    critical: dedupedFindings.filter((f) => f.severity === 'critical').length,
    high: dedupedFindings.filter((f) => f.severity === 'high').length,
    medium: dedupedFindings.filter((f) => f.severity === 'medium').length,
    low: dedupedFindings.filter((f) => f.severity === 'low').length,
    info: dedupedFindings.filter((f) => f.severity === 'info').length,
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-slate-900 overflow-hidden">
      {/* Header bar */}
      <div className="h-10 px-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/80 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-slate-700 dark:text-slate-200">SECURITY AUDIT</span>
          
          {/* Assessed code badge */}
          <span className="text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded border border-slate-200 dark:border-slate-700 uppercase">
            Target: {source_kind} Code
          </span>

          {is_demo && (
            <span className="text-[10px] font-bold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 px-2 py-0.5 rounded-full border border-amber-200 dark:border-amber-800">
              DEMO RESULT (MOCK AGENT)
            </span>
          )}

          {duration_ms > 0 && (
            <span className="text-[11px] font-mono text-slate-400">{duration_ms}ms</span>
          )}
        </div>

        {/* Severity summary counts */}
        <div className="flex items-center gap-2">
          {severityCounts.critical > 0 && (
            <span className="text-[10px] font-bold bg-red-100 dark:bg-red-950/60 text-red-800 dark:text-red-300 px-2 py-0.5 rounded border border-red-200 dark:border-red-800">
              {severityCounts.critical} Critical
            </span>
          )}
          {severityCounts.high > 0 && (
            <span className="text-[10px] font-bold bg-orange-100 dark:bg-orange-950/60 text-orange-800 dark:text-orange-300 px-2 py-0.5 rounded border border-orange-200 dark:border-orange-800">
              {severityCounts.high} High
            </span>
          )}
          {severityCounts.medium > 0 && (
            <span className="text-[10px] font-bold bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 px-2 py-0.5 rounded border border-amber-200 dark:border-amber-800">
              {severityCounts.medium} Medium
            </span>
          )}
          {dedupedFindings.length === 0 && (
            <span className="text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 px-2 py-0.5 rounded flex items-center gap-1 border border-emerald-200 dark:border-emerald-800">
              <CheckCircle2 className="w-3 h-3" /> No Issues Detected
            </span>
          )}
        </div>
      </div>

      {/* Findings List */}
      <div className="flex-1 min-h-0 p-4 overflow-y-auto space-y-3">
        {dedupedFindings.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mb-2" />
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              No Vulnerabilities Found
            </h4>
            <p className="text-xs text-slate-400 mt-1 max-w-sm">
              The Security Agent did not report any policy or vulnerability issues in the evaluated {source_kind} source.
            </p>
          </div>
        ) : (
          dedupedFindings.map((f) => {
            let badgeBg = 'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700';
            if (f.severity === 'critical') badgeBg = 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/60 dark:text-red-300 dark:border-red-800';
            if (f.severity === 'high') badgeBg = 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/60 dark:text-orange-300 dark:border-orange-800';
            if (f.severity === 'medium') badgeBg = 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800';
            if (f.severity === 'low') badgeBg = 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-800';

            return (
              <div
                key={f.id}
                onClick={() => f.line_number && onNavigateToLine?.(f.line_number)}
                className={`p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 shadow-2xs hover:border-blue-400 dark:hover:border-blue-500 transition-all ${
                  f.line_number ? 'cursor-pointer group' : ''
                }`}
                title={f.line_number ? `Click to jump to line ${f.line_number} in Source Code` : undefined}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badgeBg}`}
                    >
                      {f.severity}
                    </span>
                    <h4 className="text-xs font-bold text-slate-800 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {f.title}
                    </h4>
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
                    {f.rule_or_cwe && (
                      <span className="bg-slate-100 dark:bg-slate-700 px-1.5 py-0.5 rounded text-slate-600 dark:text-slate-300">
                        {f.rule_or_cwe}
                      </span>
                    )}
                    {f.line_number && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onNavigateToLine?.(f.line_number!);
                        }}
                        className="flex items-center gap-1 text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/70 hover:bg-blue-100 dark:hover:bg-blue-900 border border-blue-200 dark:border-blue-800/80 rounded px-1.5 py-0.5 transition-colors shrink-0 shadow-2xs"
                        title={`Navigate to line ${f.line_number} in original editor`}
                      >
                        <LocateFixed className="w-3 h-3 text-blue-500 group-hover:scale-110 transition-transform" />
                        <span>Line {f.line_number}</span>
                      </button>
                    )}
                  </div>
                </div>

                <p className="text-xs text-slate-600 dark:text-slate-300 mt-2 leading-relaxed">
                  {sanitizeVendor(f.description)}
                </p>

                {f.remediation && (
                  <div className="mt-2.5 p-2 rounded-lg bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300">
                    <span className="font-semibold text-slate-900 dark:text-slate-100">Remediation: </span>
                    {sanitizeVendor(f.remediation)}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
