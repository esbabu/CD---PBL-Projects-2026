import React, { useState } from 'react';
import './AboutAnalysis.css';

export const AboutAnalysis: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <section className="about-analysis-card">
      <div
        className="about-analysis-header"
        onClick={() => setIsOpen(!isOpen)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsOpen(!isOpen);
          }
        }}
        aria-expanded={isOpen}
      >
        <div className="about-title-group">
          <span className="info-icon">ℹ</span>
          <h4 className="about-title">About This Analysis & Current Limitations</h4>
        </div>
        <span className="toggle-indicator">
          {isOpen ? '▲ Hide Details' : '▼ View Scope & Limitations'}
        </span>
      </div>

      {isOpen && (
        <div className="about-analysis-body">
          <div className="limitation-grid">
            <div className="limitation-item">
              <span className="limitation-badge language-badge-item">Languages</span>
              <p>
                SyntaxSense supports <strong>C++</strong>, <strong>Python</strong>, and{' '}
                <strong>Java</strong>. Each language uses a dedicated, non-executing parser
                and diagnostic engine.
              </p>
            </div>

            <div className="limitation-item">
              <span className="limitation-badge dual-badge-item">Dual Engines</span>
              <p>
                The <strong>ML Classifier</strong> and <strong>Syntactic Diagnostics</strong>{' '}
                are independent outputs. The ML model classifies code patterns from 30 AST
                features, while diagnostics flag specific line-level issues.
              </p>
            </div>

            <div className="limitation-item">
              <span className="limitation-badge ml-badge-item">Model Behavior</span>
              <p>
                The ML model was trained on synthetic datasets across 13 error classes without
                an explicit &quot;clean code&quot; class. It may output an error class with
                moderate confidence even for valid code.
              </p>
            </div>

            <div className="limitation-item">
              <span className="limitation-badge scope-badge-item">Verification Scope</span>
              <p>
                Zero reported diagnostics means no syntax violations were caught under the
                implemented rules. It does not guarantee compiler-level completeness or
                semantic correctness.
              </p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default AboutAnalysis;
