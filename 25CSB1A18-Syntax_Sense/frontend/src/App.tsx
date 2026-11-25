import { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import SummaryCard from './components/SummaryCard';
import ClassificationCard from './components/ClassificationCard';
import DiagnosticsList from './components/DiagnosticsList';
import TokenStream from './components/TokenStream';
import AboutAnalysis from './components/AboutAnalysis';
import {
  DEFAULT_CPP_CODE,
  getDefaultCodeForLanguage,
} from './constants/samples';
import { analyzeCode, AnalysisApiError } from './services/api';
import type {
  AnalyzeResponse,
  DiagnosticItem,
  DiagnosticNavigationTarget,
  SupportedLanguage,
} from './types';
import './App.css';

type AnalysisStatus = 'idle' | 'loading' | 'success' | 'error';

function App() {
  const [language, setLanguage] = useState<SupportedLanguage>('cpp');
  const [code, setCode] = useState<string>(DEFAULT_CPP_CODE);
  const [status, setStatus] = useState<AnalysisStatus>('idle');
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastAnalyzedCode, setLastAnalyzedCode] = useState<string | null>(null);
  const [lastAnalyzedLanguage, setLastAnalyzedLanguage] =
    useState<SupportedLanguage | null>(null);
  const [selectedLine, setSelectedLine] = useState<number | null>(null);
  const [navigationTarget, setNavigationTarget] =
    useState<DiagnosticNavigationTarget | null>(null);

  const isAnalyzing = status === 'loading';
  const isStale =
    result !== null &&
    ((lastAnalyzedCode !== null && code !== lastAnalyzedCode) ||
      (lastAnalyzedLanguage !== null && language !== lastAnalyzedLanguage));

  const getLanguageLabel = (lang: SupportedLanguage): string => {
    switch (lang) {
      case 'cpp':
        return 'C++';
      case 'python':
        return 'Python';
      case 'java':
        return 'Java';
      default:
        return lang;
    }
  };

  const handleLanguageChange = (newLanguage: SupportedLanguage) => {
    if (newLanguage === language) return;

    setLanguage(newLanguage);
    setCode(getDefaultCodeForLanguage(newLanguage));

    // Clear previous language results to avoid stale or mismatched diagnostics
    setResult(null);
    setStatus('idle');
    setErrorMessage(null);
    setLastAnalyzedCode(null);
    setLastAnalyzedLanguage(null);
    setSelectedLine(null);
    setNavigationTarget(null);
  };

  const handleAnalyze = async () => {
    if (isAnalyzing) return;

    const trimmed = code.trim();
    if (!trimmed) {
      setErrorMessage(
        `${getLanguageLabel(language)} source code is empty. Please enter or load code before analyzing.`,
      );
      setStatus('error');
      return;
    }

    setStatus('loading');
    setErrorMessage(null);
    setSelectedLine(null);
    setNavigationTarget(null);

    try {
      const response = await analyzeCode(code, language);
      setResult(response);
      setLastAnalyzedCode(code);
      setLastAnalyzedLanguage(language);
      setStatus('success');
    } catch (err: unknown) {
      if (err instanceof AnalysisApiError) {
        setErrorMessage(err.message);
      } else if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage('An unexpected error occurred during analysis.');
      }
      setStatus('error');
    }
  };

  const handleReset = () => {
    setStatus('idle');
    setResult(null);
    setErrorMessage(null);
    setLastAnalyzedCode(null);
    setLastAnalyzedLanguage(null);
    setSelectedLine(null);
    setNavigationTarget(null);
  };

  const handleSelectDiagnostic = (diag: DiagnosticItem) => {
    if (typeof diag.line === 'number') {
      setSelectedLine(diag.line);
      setNavigationTarget({
        line: diag.line,
        column: diag.column,
        timestamp: Date.now(),
      });
    }
  };

  // Only display Monaco squiggly markers if the displayed code matches the analysis
  const activeDiagnostics = !isStale && result ? result.diagnostics : [];

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="app-header">
        <div className="header-branding">
          <div className="app-logo">SS</div>
          <div>
            <h1>SyntaxSense</h1>
            <p className="app-subtitle">
              Multi-Language Syntax Error Diagnostics & AST Classification
            </p>
          </div>
        </div>

        <div className="header-meta">
          <span className="analyzer-badge" title="Active supported languages">
            Languages: C++, Python, Java
          </span>
          <span className="status-pill connected" title="Proxied to local backend">
            Backend: FastAPI :8000
          </span>
        </div>
      </header>

      {/* Action Controls Bar */}
      <section className="action-bar">
        <div className="action-group">
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <span className="spinner" /> Analyzing {getLanguageLabel(language)} Code...
              </>
            ) : (
              `▶ Analyze ${getLanguageLabel(language)} Code`
            )}
          </button>

          {(result || status === 'error') && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={isAnalyzing}
            >
              Reset Results
            </button>
          )}
        </div>

        <div className="action-hint">
          {isAnalyzing && (
            <span className="hint-text analyzing">
              Parsing AST and running diagnostic validation...
            </span>
          )}
          {!isAnalyzing && isStale && (
            <span className="hint-text stale-warning">
              ⚠️ Code or language changed since last run — click Analyze to refresh
            </span>
          )}
          {!isAnalyzing && !isStale && status === 'success' && (
            <span className="hint-text success">
              Analysis complete for current {getLanguageLabel(language)} code
            </span>
          )}
        </div>
      </section>

      {/* Stale Results Warning Banner */}
      {isStale && (
        <div className="stale-banner" role="alert">
          <span className="stale-icon">⚠️</span>
          <div className="stale-content">
            <strong>Results Outdated:</strong> The editor contents or selected language
            have changed since the last analysis. The dashboard below reflects the
            previous run. Click <strong>Analyze {getLanguageLabel(language)} Code</strong> to inspect the
            updated source.
          </div>
        </div>
      )}

      {/* Main Two-Column Workspace */}
      <main className="workspace-grid">
        {/* Left Column: Monaco Code Editor */}
        <section className="editor-column">
          <CodeEditor
            value={code}
            onChange={setCode}
            language={language}
            onLanguageChange={handleLanguageChange}
            diagnostics={activeDiagnostics}
            selectedLine={selectedLine}
            navigationTarget={navigationTarget}
            height="560px"
          />
        </section>

        {/* Right Column: Results Dashboard */}
        <section className="dashboard-column">
          {/* State 1: Idle (Empty State) */}
          {status === 'idle' && (
            <div className="empty-state-card">
              <div className="empty-state-icon">⚡</div>
              <h3>Ready for {getLanguageLabel(language)} Syntax Analysis</h3>
              <p>
                SyntaxSense combines <strong>Compiler AST Parsing</strong> with{' '}
                <strong>Deterministic Source Heuristics</strong> to locate and explain
                syntactic errors in real time.
              </p>
              <div className="empty-state-features">
                <div className="feature-item">
                  <span className="feature-icon">🔍</span>
                  <div>
                    <strong>Line & Column Diagnostics</strong>
                    <p>Pinpoint errors with actionable explanations and code fix suggestions.</p>
                  </div>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">🤖</span>
                  <div>
                    <strong>Multi-Language Architecture</strong>
                    <p>Modular pipeline supporting C++, Python, and Java analyzers.</p>
                  </div>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">🛡️</span>
                  <div>
                    <strong>Safe Non-Executing Engine</strong>
                    <p>Analysis validates grammar and AST trees without executing submitted code.</p>
                  </div>
                </div>
              </div>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleAnalyze}
              >
                Analyze Starter Code
              </button>
            </div>
          )}

          {/* State 2: Loading State */}
          {status === 'loading' && (
            <div className="loading-state-card">
              <div className="loading-pulse-spinner" />
              <h3>Analyzing {getLanguageLabel(language)} Source Code</h3>
              <p>1. Ingesting source code payload</p>
              <p>2. Dispatching to {getLanguageLabel(language)} analyzer</p>
              <p>3. Constructing Abstract Syntax Tree</p>
              <p>4. Extracting diagnostics and line locations</p>
            </div>
          )}

          {/* State 3: Error State */}
          {status === 'error' && (
            <div className="error-state-card" role="alert">
              <div className="error-icon">⚠️</div>
              <h3>Analysis Failed</h3>
              <p className="error-message-text">{errorMessage}</p>
              <div className="error-tips">
                <p>
                  <strong>Troubleshooting:</strong>
                </p>
                <ul>
                  <li>Ensure the FastAPI backend is running on <code>http://127.0.0.1:8000</code>.</li>
                  <li>Verify that the code does not exceed the 200,000 character limit.</li>
                  <li>Ensure the source contains valid non-empty {getLanguageLabel(language)} text.</li>
                </ul>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleAnalyze}
              >
                Retry Analysis
              </button>
            </div>
          )}

          {/* State 4: Success Dashboard */}
          {status === 'success' && result && (
            <div className="dashboard-results-stack">
              <SummaryCard
                summary={result.summary}
                analysisVersion={result.analysisVersion}
              />

              <ClassificationCard
                classification={result.classification}
                language={result.language}
              />

              <DiagnosticsList
                diagnostics={result.diagnostics}
                onSelectDiagnostic={handleSelectDiagnostic}
                selectedLine={selectedLine}
              />

              <TokenStream
                tokens={result.tokens}
                language={result.language}
              />
            </div>
          )}
        </section>
      </main>

      {/* About & Limitations Section */}
      <AboutAnalysis />
    </div>
  );
}

export default App;
