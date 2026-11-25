import React, { useMemo } from 'react';
import type { DiagnosticItem } from '../types';
import './DiagnosticsList.css';

export interface DiagnosticsListProps {
  diagnostics: DiagnosticItem[];
  onSelectDiagnostic?: (diagnostic: DiagnosticItem) => void;
  selectedLine?: number | null;
}

export const DiagnosticsList: React.FC<DiagnosticsListProps> = ({
  diagnostics,
  onSelectDiagnostic,
  selectedLine,
}) => {
  // Deduplicate only demonstrably exact identical items while preserving distinct origins and parser details
  const deduplicatedDiagnostics = useMemo(() => {
    const seen = new Set<string>();
    return diagnostics.filter((diag) => {
      const signature = `${diag.category}|${diag.origin}|${diag.severity}|${diag.line}|${diag.column}|${diag.parserMessage ?? ''}|${diag.explanation}`;
      if (seen.has(signature)) return false;
      seen.add(signature);
      return true;
    });
  }, [diagnostics]);

  if (deduplicatedDiagnostics.length === 0) {
    return (
      <div className="diagnostics-panel">
        <h3 className="diagnostics-title">Detailed Diagnostics</h3>
        <div className="diagnostics-empty">
          <span className="empty-icon">✓</span>
          <p className="empty-text">No syntactic diagnostics reported</p>
          <p className="empty-subtext">
            The parser and source-level heuristics detected no syntax violations under checked
            grammar rules. Note: This does not guarantee semantic correctness or compiler-level completeness.
          </p>
        </div>
      </div>
    );
  }

  const duplicatesFilteredCount = diagnostics.length - deduplicatedDiagnostics.length;

  return (
    <div className="diagnostics-panel">
      <div className="diagnostics-header">
        <h3 className="diagnostics-title">Detailed Diagnostics</h3>
        <div className="diagnostics-count-wrap">
          <span className="diagnostics-count">
            {deduplicatedDiagnostics.length}{' '}
            {deduplicatedDiagnostics.length === 1 ? 'finding' : 'findings'}
          </span>
          {duplicatesFilteredCount > 0 && (
            <span
              className="duplicates-tag"
              title={`${duplicatesFilteredCount} identical diagnostic report(s) folded`}
            >
              ({duplicatesFilteredCount} duplicate folded)
            </span>
          )}
        </div>
      </div>

      <div className="diagnostics-list">
        {deduplicatedDiagnostics.map((diag, index) => {
          const isSelected = selectedLine !== null && diag.line === selectedLine;
          const originLabel =
            diag.origin === 'parser'
              ? 'AST Parser'
              : diag.origin === 'source_heuristic'
                ? 'Source Heuristic'
                : diag.origin;

          const locationText =
            typeof diag.line === 'number'
              ? `Line ${diag.line}${typeof diag.column === 'number' ? `:${diag.column}` : ' (Col N/A)'}`
              : 'File-level / EOF';

          return (
            <div
              key={`${diag.category}-${diag.line ?? 'none'}-${diag.column ?? 'none'}-${diag.origin}-${index}`}
              className={`diagnostic-card ${isSelected ? 'selected' : ''} ${
                typeof diag.line === 'number' ? 'clickable' : ''
              }`}
              onClick={() => typeof diag.line === 'number' && onSelectDiagnostic?.(diag)}
              title={
                typeof diag.line === 'number'
                  ? `Click to navigate to line ${diag.line} in editor`
                  : 'Location unavailable — reported at EOF or file level'
              }
            >
              <div className="diagnostic-card-header">
                <div className="header-left">
                  <span className={`severity-badge severity-${diag.severity || 'error'}`}>
                    {diag.severity || 'error'}
                  </span>
                  <span className="category-name">{diag.category}</span>
                </div>

                <div className="header-right">
                  <span className="origin-badge">{originLabel}</span>
                  <span className="location-badge">{locationText}</span>
                </div>
              </div>

              <div className="diagnostic-card-body">
                <div className="detail-row">
                  <span className="detail-label">Issue:</span>
                  <span className="detail-value">{diag.explanation}</span>
                </div>

                <div className="detail-row fix-row">
                  <span className="detail-label">Suggested Fix:</span>
                  <span className="detail-value fix-value">{diag.suggestion}</span>
                </div>

                {diag.parserMessage && (
                  <div className="parser-raw-message">
                    <code>{diag.parserMessage}</code>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DiagnosticsList;
