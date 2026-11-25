import React, { useRef, useEffect, useState } from 'react';
import Editor, { type OnChange, type OnMount, type Monaco } from '@monaco-editor/react';
import {
  getSamplesForLanguage,
  type CodeSample,
} from '../constants/samples';
import type {
  DiagnosticItem,
  DiagnosticNavigationTarget,
  SupportedLanguage,
} from '../types';
import './CodeEditor.css';

type StandaloneEditor = Parameters<OnMount>[0];

export interface CodeEditorProps {
  /** Current code content */
  value: string;
  /** Callback triggered when user edits the code */
  onChange: (value: string) => void;
  /** Active programming language mode (e.g. 'cpp' | 'python' | 'java') */
  language?: SupportedLanguage;
  /** Callback triggered when user changes language */
  onLanguageChange?: (language: SupportedLanguage) => void;
  /** Callback triggered when user clears code */
  onClear?: () => void;
  /** Active diagnostics to display as markers in the editor */
  diagnostics?: DiagnosticItem[];
  /** Line number to navigate to when selected in diagnostics */
  selectedLine?: number | null;
  /** Target location for navigating to a specific diagnostic finding */
  navigationTarget?: DiagnosticNavigationTarget | null;
  /** Editor theme (defaults to 'vs' light theme) */
  theme?: string;
  /** Height of the code editor region */
  height?: string;
  /** Whether the editor is read-only */
  readOnly?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  value,
  onChange,
  language = 'cpp',
  onLanguageChange,
  onClear,
  diagnostics,
  selectedLine,
  navigationTarget,
  theme = 'vs',
  height = '540px',
  readOnly = false,
}) => {
  const editorRef = useRef<StandaloneEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const sampleSelectRef = useRef<HTMLSelectElement | null>(null);
  const [copyFeedback, setCopyFeedback] = useState<'idle' | 'copied' | 'error'>('idle');

  const handleOnMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
  };

  // Synchronize diagnostic markers with Monaco model
  useEffect(() => {
    const editor = editorRef.current;
    const monaco = monacoRef.current;
    if (!editor || !monaco) return;

    const model = editor.getModel();
    if (!model || model.isDisposed()) return;

    if (!diagnostics || diagnostics.length === 0) {
      monaco.editor.setModelMarkers(model, 'syntaxsense', []);
      return;
    }

    const lineCount = model.getLineCount();
    const markers: Parameters<typeof monaco.editor.setModelMarkers>[2] = [];

    for (const diag of diagnostics) {
      if (typeof diag.line !== 'number') continue;

      const safeLine = Math.min(Math.max(1, diag.line), lineCount);
      const lineMaxCol = model.getLineMaxColumn(safeLine);
      let startCol = 1;
      let endCol = lineMaxCol;

      if (typeof diag.column === 'number' && diag.column > 0) {
        startCol = Math.min(diag.column, lineMaxCol);
        endCol = Math.min(startCol + 1, lineMaxCol);
      }

      markers.push({
        severity: monaco.MarkerSeverity.Error,
        message: `${diag.category}: ${diag.explanation}`,
        startLineNumber: safeLine,
        startColumn: startCol,
        endLineNumber: safeLine,
        endColumn: endCol,
      });
    }

    monaco.editor.setModelMarkers(model, 'syntaxsense', markers);
  }, [diagnostics]);

  // Clear markers when language changes
  useEffect(() => {
    if (editorRef.current && monacoRef.current) {
      const model = editorRef.current.getModel();
      if (model && !model.isDisposed()) {
        monacoRef.current.editor.setModelMarkers(model, 'syntaxsense', []);
      }
    }
    // Reset sample dropdown to empty placeholder
    if (sampleSelectRef.current) {
      sampleSelectRef.current.value = '';
    }
  }, [language]);

  // Focus and reveal line when navigationTarget or selectedLine updates
  useEffect(() => {
    const targetLine = navigationTarget?.line ?? selectedLine;
    if (typeof targetLine !== 'number') return;

    const animId = requestAnimationFrame(() => {
      const editor = editorRef.current;
      if (!editor) return;

      const model = editor.getModel();
      if (!model || model.isDisposed()) return;

      const lineCount = model.getLineCount();
      const safeLine = Math.min(Math.max(1, targetLine), lineCount);
      const safeCol = navigationTarget?.column
        ? Math.min(Math.max(1, navigationTarget.column), model.getLineMaxColumn(safeLine))
        : 1;

      editor.revealPositionInCenter(
        { lineNumber: safeLine, column: safeCol },
        0, // Immediate scroll without animation lag
      );

      editor.setPosition({ lineNumber: safeLine, column: safeCol });

      const domNode = editor.getDomNode();
      if (domNode && document.activeElement !== domNode) {
        editor.focus();
      }
    });

    return () => cancelAnimationFrame(animId);
  }, [navigationTarget, selectedLine]);

  const handleEditorChange: OnChange = (newVal) => {
    // Clear markers when code is modified
    if (editorRef.current && monacoRef.current) {
      const model = editorRef.current.getModel();
      if (model && !model.isDisposed()) {
        monacoRef.current.editor.setModelMarkers(model, 'syntaxsense', []);
      }
    }
    onChange(newVal ?? '');
  };

  const currentSamples = getSamplesForLanguage(language);

  const handleSelectSample = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = event.target.value;
    if (!selectedId) return;
    const match = currentSamples.find((s) => s.id === selectedId);
    if (match) {
      if (editorRef.current && monacoRef.current) {
        const model = editorRef.current.getModel();
        if (model && !model.isDisposed()) {
          monacoRef.current.editor.setModelMarkers(model, 'syntaxsense', []);
        }
      }
      onChange(match.code);
    }
    // Reset select to allow selecting the same sample again if edited
    event.target.value = '';
  };

  const handleCopyCode = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(value);
      } else {
        const tempTextarea = document.createElement('textarea');
        tempTextarea.value = value;
        tempTextarea.style.position = 'fixed';
        tempTextarea.style.opacity = '0';
        document.body.appendChild(tempTextarea);
        tempTextarea.select();
        document.execCommand('copy');
        document.body.removeChild(tempTextarea);
      }
      setCopyFeedback('copied');
      setTimeout(() => setCopyFeedback('idle'), 2000);
    } catch {
      setCopyFeedback('error');
      setTimeout(() => setCopyFeedback('idle'), 2500);
    }
  };

  const handleClearCode = () => {
    if (editorRef.current && monacoRef.current) {
      const model = editorRef.current.getModel();
      if (model && !model.isDisposed()) {
        monacoRef.current.editor.setModelMarkers(model, 'syntaxsense', []);
      }
    }
    onChange('');
    onClear?.();
  };

  const getLanguageLabel = (lang: SupportedLanguage) => {
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

  return (
    <div className="code-editor-container">
      {/* Editor Toolbar */}
      <div className="code-editor-toolbar">
        <div className="code-editor-toolbar-left">
          <div className="code-editor-toolbar-title">
            <span className={`language-badge lang-${language}`}>
              {getLanguageLabel(language)}
            </span>
            <span className="toolbar-label">Source Editor</span>
          </div>

          <div className="toolbar-select-group">
            {/* Language Selector */}
            <label htmlFor="language-selector" className="selector-label">
              Language:
            </label>
            <select
              id="language-selector"
              className="toolbar-select language-select"
              value={language}
              onChange={(e) => onLanguageChange?.(e.target.value as SupportedLanguage)}
              aria-label="Select Programming Language"
            >
              <option value="cpp">C++</option>
              <option value="python">Python</option>
              <option value="java">Java</option>
            </select>

            {/* Sample Snippet Selector */}
            <label htmlFor="sample-selector" className="selector-label">
              Sample:
            </label>
            <select
              id="sample-selector"
              ref={sampleSelectRef}
              className="toolbar-select sample-select"
              defaultValue=""
              onChange={handleSelectSample}
              aria-label="Load Sample Snippet"
            >
              <option value="" disabled>
                Load a sample snippet...
              </option>
              {currentSamples.map((sample: CodeSample) => (
                <option key={sample.id} value={sample.id} title={`${sample.name} - ${sample.description}`}>
                  {sample.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="code-editor-toolbar-actions">
          {/* Copy Code Action Button */}
          <button
            type="button"
            className={`btn-toolbar btn-copy ${copyFeedback === 'copied' ? 'success' : ''}`}
            onClick={handleCopyCode}
            title="Copy editor source code to clipboard"
          >
            {copyFeedback === 'copied' ? (
              <>
                <span className="btn-icon">✓</span> Copied!
              </>
            ) : copyFeedback === 'error' ? (
              <>
                <span className="btn-icon">⚠</span> Failed
              </>
            ) : (
              <>
                <span className="btn-icon">📋</span> Copy
              </>
            )}
          </button>

          {/* Clear Code Action Button */}
          <button
            type="button"
            className="btn-toolbar btn-clear"
            onClick={handleClearCode}
            title="Clear editor contents"
            disabled={!value}
          >
            <span className="btn-icon">🗑️</span> Clear
          </button>
        </div>
      </div>

      {/* Editor Body */}
      <div className="code-editor-body" style={{ height }}>
        <Editor
          height="100%"
          language={language}
          theme={theme}
          value={value}
          onMount={handleOnMount}
          onChange={handleEditorChange}
          options={{
            readOnly,
            lineNumbers: 'on',
            fontSize: 14,
            tabSize: 4,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            automaticLayout: true,
            glyphMargin: true,
            folding: true,
            suggestOnTriggerCharacters: true,
            renderLineHighlight: 'all',
            renderLineHighlightOnlyWhenFocus: false,
            fontFamily: "JetBrains Mono, Menlo, Monaco, 'Courier New', monospace",
          }}
        />
      </div>

      {/* Editor Footer */}
      <div className="code-editor-footer">
        <div className="footer-meta-left">
          <span className="footer-indicator">
            <span className="indicator-dot" /> Mode: {getLanguageLabel(language)}
          </span>
          {diagnostics && diagnostics.length > 0 && (
            <span className="footer-diag-count">
              {diagnostics.length} issue{diagnostics.length === 1 ? '' : 's'} flagged
            </span>
          )}
        </div>
        <div className="footer-meta-right">
          <span>{value.length} characters</span>
          <span>{value.split('\n').length} lines</span>
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;
