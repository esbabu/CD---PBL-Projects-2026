import React from 'react';
import type { AnalysisSummary } from '../types';
import './SummaryCard.css';

export interface SummaryCardProps {
  summary: AnalysisSummary;
  analysisVersion?: string;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({
  summary,
  analysisVersion,
}) => {
  return (
    <div className="summary-card">
      <div className="summary-header">
        <h3 className="summary-title">Analysis Overview</h3>
        {analysisVersion && (
          <span className="summary-version-badge" title="Backend analysis engine version">
            {analysisVersion}
          </span>
        )}
      </div>

      <div className="summary-stats-grid">
        <div className="stat-box stat-box-total">
          <span className="stat-value">{summary.diagnosticCount}</span>
          <span className="stat-label">Total Issues</span>
        </div>

        <div className="stat-box">
          <span className="stat-value">{summary.parserDiagnosticCount}</span>
          <span className="stat-label">Parser Findings</span>
        </div>

        <div className="stat-box">
          <span className="stat-value">{summary.sourceHeuristicDiagnosticCount}</span>
          <span className="stat-label">Source Heuristics</span>
        </div>
      </div>
    </div>
  );
};

export default SummaryCard;
