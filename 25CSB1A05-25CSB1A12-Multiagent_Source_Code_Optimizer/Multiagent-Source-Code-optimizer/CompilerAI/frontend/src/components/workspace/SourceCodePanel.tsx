import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { FileCode, Copy, Check, Trash2 } from 'lucide-react';
import { SUPPORTED_LANGUAGES } from '../../app/appConfig';

interface SourceCodePanelProps {
  sourceCode: string;
  language: string;
  onSourceChange: (val: string) => void;
  onLanguageChange: (lang: string) => void;
  readOnly?: boolean;
  isDark?: boolean;
  targetLine?: { line: number; timestamp: number } | null;
}

export const SourceCodePanel: React.FC<SourceCodePanelProps> = ({
  sourceCode,
  language,
  onSourceChange,
  onLanguageChange,
  readOnly = false,
  isDark = false,
  targetLine,
}) => {
  const [copied, setCopied] = useState(false);
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<any>(null);
  const decorationsRef = useRef<any[]>([]);

  const handleEditorMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    monacoRef.current = monaco;
  };

  // Scroll to and highlight target line when triggered
  useEffect(() => {
    if (!targetLine || !editorRef.current) return;
    const { line } = targetLine;
    const editor = editorRef.current;

    // Reveal line in center of editor
    editor.revealLineInCenter(line);

    // Set cursor position
    editor.setPosition({ lineNumber: line, column: 1 });

    // Focus editor
    editor.focus();

    // Apply temporary line highlight decoration
    if (monacoRef.current) {
      const monaco = monacoRef.current;
      const newDecorations = [
        {
          range: new monaco.Range(line, 1, line, 1),
          options: {
            isWholeLine: true,
            className: 'monaco-highlight-line',
          },
        },
      ];
      decorationsRef.current = editor.deltaDecorations(decorationsRef.current, newDecorations);

      const timer = setTimeout(() => {
        if (editorRef.current) {
          decorationsRef.current = editorRef.current.deltaDecorations(decorationsRef.current, []);
        }
      }, 2500);

      return () => clearTimeout(timer);
    }
  }, [targetLine]);

  const handleCopy = () => {
    navigator.clipboard.writeText(sourceCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    if (confirm('Clear the source code editor?')) {
      onSourceChange('');
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
      {/* Panel Header */}
      <div className="h-10 border-b border-slate-200 dark:border-slate-800 px-3 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/80">
        <div className="flex items-center gap-2">
          <FileCode className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          <span className="text-xs font-bold text-slate-700 dark:text-slate-200 tracking-wider">SOURCE CODE</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Language Selector */}
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value)}
            disabled={readOnly}
            className="text-xs font-semibold bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 text-slate-700 dark:text-slate-200 hover:border-slate-300 dark:hover:border-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.id} value={lang.id}>
                {lang.label}
              </option>
            ))}
          </select>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            title="Copy Source Code"
            className="p-1.5 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 hover:bg-slate-200/60 dark:hover:bg-slate-800 rounded-md transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
          </button>

          {/* Clear Button */}
          <button
            onClick={handleClear}
            disabled={readOnly}
            title="Clear Source Code"
            className="p-1.5 text-slate-500 dark:text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-md transition-colors disabled:opacity-40"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Monaco Editor Container */}
      <div className="flex-1 min-h-0 relative">
        <Editor
          height="100%"
          language={language === 'c' || language === 'cpp' ? 'cpp' : language}
          value={sourceCode}
          onChange={(val) => onSourceChange(val || '')}
          onMount={handleEditorMount}
          theme={isDark ? 'vs-dark' : 'vs'}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            fontFamily: "'JetBrains Mono', Consolas, monospace",
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            readOnly: readOnly,
            padding: { top: 12, bottom: 12 },
          }}
        />
      </div>
    </div>
  );
};
