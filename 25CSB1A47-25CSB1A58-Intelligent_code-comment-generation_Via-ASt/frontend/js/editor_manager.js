/**
 * AST Studio · Editor Manager
 * Modular editor synchronization, pair completion, indentation, and overlay rendering.
 */

(function (window) {
    'use strict';

    class EditorManager {
        static syncScroll(editorElem, highlightElem, lineNumbersElem, ghostTextElem) {
            if (!editorElem) return;
            const top = editorElem.scrollTop;
            const left = editorElem.scrollLeft;
            if (highlightElem) {
                highlightElem.scrollTop = top;
                highlightElem.scrollLeft = left;
            }
            if (lineNumbersElem) {
                lineNumbersElem.scrollTop = top;
            }
            if (ghostTextElem) {
                ghostTextElem.scrollTop = top;
                ghostTextElem.scrollLeft = left;
            }
        }

        static updateOverlay(editorElem, lineNumbersElem, highlightElem, charCountElem, lineCountElem, tokenElem) {
            if (!editorElem) return;
            const code = editorElem.value;
            if (charCountElem) charCountElem.textContent = code.length;
            const lines = code.split('\n');
            if (lineCountElem) lineCountElem.textContent = lines.length;
            if (tokenElem) {
                tokenElem.textContent = `~${Math.ceil(code.length / 4)}`;
            }
            if (lineNumbersElem) {
                lineNumbersElem.innerHTML = Array.from(
                    { length: lines.length || 1 },
                    (_, i) => `<div class="line-num">${i + 1}</div>`
                ).join('');
            }
            if (highlightElem) {
                const escape = window.escapeHtml || ((s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'));
                const htmlCode = escape(code);
                highlightElem.innerHTML = `<code class="language-python">${htmlCode}</code>`;
                if (window.hljs) {
                    const codeBlock = highlightElem.querySelector('code');
                    if (codeBlock) window.hljs.highlightElement(codeBlock);
                }
            }
        }

        static handleKeydown(e, editorElem, onEnterCtrl = null, onClearAll = null) {
            if (!editorElem) return false;

            // 4-spaces tab
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = editorElem.selectionStart;
                const end = editorElem.selectionEnd;
                editorElem.value = editorElem.value.substring(0, start) + '    ' + editorElem.value.substring(end);
                editorElem.selectionStart = editorElem.selectionEnd = start + 4;
                editorElem.dispatchEvent(new Event('input', { bubbles: true }));
                return true;
            }

            // Enter with auto-indent
            if (e.key === 'Enter') {
                if (e.ctrlKey) {
                    if (typeof onEnterCtrl === 'function') {
                        e.preventDefault();
                        onEnterCtrl();
                        return true;
                    }
                }
                const start = editorElem.selectionStart;
                const lineStr = editorElem.value.substring(0, start).split('\n').pop();
                const match = lineStr.match(/^(\s*)/);
                let indent = match ? match[1] : '';
                if (lineStr.trim().endsWith(':')) {
                    indent += '    ';
                }
                e.preventDefault();
                editorElem.value = editorElem.value.substring(0, start) + '\n' + indent + editorElem.value.substring(editorElem.selectionEnd);
                editorElem.selectionStart = editorElem.selectionEnd = start + 1 + indent.length;
                editorElem.dispatchEvent(new Event('input', { bubbles: true }));
                return true;
            }

            // Ctrl+L clear
            if (e.key === 'l' && e.ctrlKey) {
                if (typeof onClearAll === 'function') {
                    e.preventDefault();
                    onClearAll();
                    return true;
                }
            }

            // Pair completion
            const pairs = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" };
            const closingPairs = new Set(Object.values(pairs));
            if (!e.ctrlKey && !e.altKey && !e.metaKey && closingPairs.has(e.key)
                && editorElem.selectionStart === editorElem.selectionEnd
                && editorElem.value[editorElem.selectionStart] === e.key) {
                e.preventDefault();
                editorElem.selectionStart = editorElem.selectionEnd = editorElem.selectionStart + 1;
                return true;
            }

            if (e.key === 'Backspace' && editorElem.selectionStart === editorElem.selectionEnd) {
                const start = editorElem.selectionStart;
                if (pairs[editorElem.value[start - 1]] === editorElem.value[start]) {
                    e.preventDefault();
                    editorElem.value = editorElem.value.substring(0, start - 1) + editorElem.value.substring(start + 1);
                    editorElem.selectionStart = editorElem.selectionEnd = start - 1;
                    editorElem.dispatchEvent(new Event('input', { bubbles: true }));
                    return true;
                }
            }

            if (pairs[e.key] && !e.ctrlKey && !e.altKey && !e.metaKey) {
                e.preventDefault();
                const start = editorElem.selectionStart;
                const end = editorElem.selectionEnd;
                const selected = editorElem.value.substring(start, end);
                editorElem.value = editorElem.value.substring(0, start) + e.key + selected + pairs[e.key] + editorElem.value.substring(end);
                editorElem.selectionStart = editorElem.selectionEnd = start + 1;
                editorElem.dispatchEvent(new Event('input', { bubbles: true }));
                return true;
            }

            return false;
        }

        static renderErrorSquiggles(warnings, editorElem, highlightElem) {
            if (!editorElem || !highlightElem) return;
            const escape = window.escapeHtml || ((s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'));
            const syntaxWarnings = (warnings || []).filter((item) => {
                const rule = String(item.rule_id || '');
                const msg = String(item.message || '');
                return rule === 'SYNTAX001' || /syntax/i.test(msg);
            });

            if (!syntaxWarnings.length) {
                return false;
            }

            const code = editorElem.value;
            const lines = code.split('\n');
            const htmlLines = lines.map((line, index) => {
                const warning = syntaxWarnings.find((item) => Number(item.line) === index + 1);
                if (!warning) {
                    return escape(line);
                }

                const column = Math.max(1, Number(warning.column ?? warning.col ?? warning.offset ?? 1));
                const start = Math.min(column - 1, Math.max(0, line.length - 1));
                const reportedEnd = Number(warning.end_column);
                const width = Number.isFinite(reportedEnd) && reportedEnd > column
                    ? reportedEnd - column
                    : 3;
                const end = Math.min(line.length, Math.max(start + 1, start + width));
                const prefix = escape(line.slice(0, start));
                const errorText = escape(line.slice(start, end));
                const suffix = escape(line.slice(end));
                return `${prefix}<span class="squiggles">${errorText}</span>${suffix}`;
            });

            highlightElem.innerHTML = `<code class="language-python">${htmlLines.join('\n')}</code>`;
            return true;
        }
    }

    window.EditorManager = EditorManager;
})(typeof window !== 'undefined' ? window : this);
