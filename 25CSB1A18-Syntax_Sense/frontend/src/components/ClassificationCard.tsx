import React from 'react';
import type { ClassificationResult } from '../types';
import './ClassificationCard.css';

export interface ClassificationCardProps {
  classification: ClassificationResult;
  language?: string;
}

export const ClassificationCard: React.FC<ClassificationCardProps> = ({
  classification,
  language,
}) => {
  const confidencePercent = Math.min(
    100,
    Math.max(0, Number(classification.confidence.toFixed(1))),
  );

  const isClean = classification.label === 'CLEAN';

  // Determine engine badge and description dynamically from source and language
  const src = (classification.source || '').toLowerCase();
  const lang = (language || '').toLowerCase();

  let engineBadge = 'ML Model';
  let engineBadgeClass = 'engine-badge-model';
  let confidenceLabel = 'Model Confidence';
  let confidenceSublabel = '(Raw Ensemble Vote Proportion)';
  let engineNote =
    'Classification predicted by the Random Forest classifier using 30 AST structural features. The confidence score represents the raw decision-tree vote proportion returned by the model, not a calibrated statistical probability.';

  if (src === 'ast_parser' || lang === 'python') {
    engineBadge = 'Deterministic AST';
    engineBadgeClass = 'engine-badge-ast';
    confidenceLabel = 'Parser Confidence';
    confidenceSublabel = '(Deterministic AST & Token Validation)';
    engineNote =
      'Classification determined deterministically via Python Abstract Syntax Tree (ast.parse) and lexical tokenizer validation without code execution.';
  } else if (src === 'java_parser' || lang === 'java') {
    engineBadge = 'Deterministic Parser';
    engineBadgeClass = 'engine-badge-java';
    confidenceLabel = 'Parser Confidence';
    confidenceSublabel = '(Deterministic Lexical & Grammar Checks)';
    engineNote =
      'Classification determined deterministically via Java lexical token scanning, delimiter stack balancing, and statement grammar checks without code execution.';
  } else if (src === 'model' || lang === 'cpp') {
    engineBadge = 'ML Model';
    engineBadgeClass = 'engine-badge-model';
    confidenceLabel = 'Model Confidence';
    confidenceSublabel = isClean
      ? '(Syntax Validated — Clean Code)'
      : '(Raw Ensemble Vote Proportion)';
    engineNote = isClean
      ? 'Deterministic AST parsing and source heuristics verified that the C++ code is syntactically clean with 0 diagnostic issues.'
      : 'Classification predicted by the Random Forest classifier using 30 AST structural features. The confidence score represents the raw decision-tree vote proportion returned by the model, not a calibrated statistical probability.';
  }

  return (
    <div className="classification-card">
      <div className="classification-header">
        <div className="classification-title-wrap">
          <span className={`ml-source-badge ${engineBadgeClass}`}>
            {engineBadge}
          </span>
          <h3 className="classification-title">Syntax Error Classification</h3>
        </div>
        <span className="source-label" title="Origin engine">
          Source: {classification.source}
        </span>
      </div>

      <div className="classification-body">
        <div className="prediction-row">
          <span className="prediction-label">Predicted Category:</span>
          <span className={`prediction-badge ${isClean ? 'clean' : ''}`}>
            {classification.label}
          </span>
        </div>

        <div className="confidence-section">
          <div className="confidence-header">
            <span className="confidence-label">
              {confidenceLabel}{' '}
              <span className="confidence-sublabel">{confidenceSublabel}</span>
            </span>
            <span className="confidence-value">{confidencePercent}%</span>
          </div>
          <div className="confidence-meter-track">
            <div
              className={`confidence-meter-fill ${isClean ? 'clean' : ''}`}
              style={{ width: `${confidencePercent}%` }}
            />
          </div>
        </div>

        <p className="classification-note">{engineNote}</p>
      </div>
    </div>
  );
};

export default ClassificationCard;
