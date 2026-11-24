/**
 * AST Studio · AST Visualizer & Quality Gauge
 * Renders AST metrics, structural components, explanations, and animated SVG quality gauge.
 */

(function (window) {
    'use strict';

    class AstVisualizer {
        static getComplexityClass(cc) {
            if (cc > 10) return 'error';
            if (cc > 5) return 'warning';
            return 'success';
        }

        static createCollapsible(title, content, open = false) {
            return `
                <div class="collapsible ${open ? 'open' : ''}">
                    <div class="collapsible-header">
                        <span>${title}</span>
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"></polyline></svg>
                    </div>
                    <div class="collapsible-content">${content}</div>
                </div>
            `;
        }

        static createItemList(items, formatter) {
            if (!items || items.length === 0) return '<div>No items</div>';
            return `<ul class="item-list">${items.map((i) => `<li>${formatter(i)}</li>`).join('')}</ul>`;
        }

        static renderAstAnalysis(analysis, warnings, escapeFn = window.escapeHtml) {
            if (!analysis) return;
            const escape = escapeFn || ((s) => String(s));

            const emptyAst = document.getElementById('empty-ast');
            const astContent = document.getElementById('ast-content');
            if (emptyAst) emptyAst.style.display = 'none';
            if (astContent) astContent.style.display = 'flex';

            const metricsGrid = document.getElementById('ast-metrics');
            if (metricsGrid) {
                metricsGrid.innerHTML = `
                    <div class="metric-card"><div class="metric-value">${analysis.functions?.length || 0}</div><div class="metric-label">Functions</div></div>
                    <div class="metric-card"><div class="metric-value">${analysis.classes?.length || 0}</div><div class="metric-label">Classes</div></div>
                    <div class="metric-card"><div class="metric-value">${analysis.imports?.length || 0}</div><div class="metric-label">Imports</div></div>
                    <div class="metric-card"><div class="metric-value">${analysis.calls?.length || 0}</div><div class="metric-label">Calls</div></div>
                    <div class="metric-card"><div class="metric-value">${analysis.branches?.length || 0}</div><div class="metric-label">Branches</div></div>
                    <div class="metric-card"><div class="metric-value">${analysis.summary?.file_cc || 1}</div><div class="metric-label">Max Cyclomatic CC</div></div>
                `;
            }

            const sections = document.getElementById('ast-sections');
            if (sections) {
                sections.innerHTML = '';

                if (analysis.functions && analysis.functions.length > 0) {
                    sections.innerHTML += this.createCollapsible('Functions & Methods', this.createItemList(analysis.functions, (f) => `
                        <span class="item-name">${escape(f.name)}()</span>
                        <div class="item-details">
                            <span>Line ${f.lineno}</span>
                            ${f.complexity ? `<span class="badge ${this.getComplexityClass(f.complexity)}">CC: ${f.complexity}</span>` : ''}
                        </div>
                    `), true);
                }

                if (analysis.classes && analysis.classes.length > 0) {
                    sections.innerHTML += this.createCollapsible('Classes & Structs', this.createItemList(analysis.classes, (c) => `
                        <span class="item-name">class ${escape(c.name)}</span>
                        <div class="item-details">Line ${c.lineno}</div>
                    `));
                }

                if (analysis.imports && analysis.imports.length > 0) {
                    sections.innerHTML += this.createCollapsible('Import Dependencies', this.createItemList(analysis.imports, (imp) => `
                        <span class="item-name">import ${escape(imp.name || imp.module || imp)}</span>
                        <div class="item-details">Line ${imp.lineno || 1}</div>
                    `));
                }

                if (warnings && warnings.length > 0) {
                    sections.innerHTML += this.createCollapsible('Static Security & Rule Warnings', this.createItemList(warnings, (w) => `
                        <span class="item-name" style="color: ${w.rule_id?.startsWith('SEC') ? 'var(--accent-crimson)' : 'var(--accent-amber)'}">
                            ${escape(w.rule_id ? `[${w.rule_id}] ${w.message || w}` : w.message || w)}
                        </span>
                        <div class="item-details">
                            ${w.line ? `<span>Line ${w.line}</span>` : ''}
                            ${w.severity ? `<span class="badge ${w.severity === 'error' ? 'error' : w.severity === 'info' ? 'cyan' : 'warning'}">${escape(w.severity)}</span>` : ''}
                        </div>
                    `), true);
                }

                sections.querySelectorAll('.collapsible-header').forEach((h) => {
                    h.addEventListener('click', function () {
                        this.parentElement.classList.toggle('open');
                    });
                });
            }
        }

        static renderExplanations(explanations, escapeFn = window.escapeHtml) {
            const emptyState = document.getElementById('empty-explanations');
            const container = document.getElementById('explanations-content');
            if (!container) return;
            const escape = escapeFn || ((s) => String(s));

            if (!explanations || explanations.length === 0) {
                if (emptyState) emptyState.style.display = 'flex';
                container.style.display = 'none';
                container.innerHTML = '';
                return;
            }

            container.innerHTML = explanations.map((ex) => `
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">${escape(ex.function || ex.name || 'AST Block')}</span>
                        <div class="item-details">
                            <span class="badge ${ex.kind === 'branch' ? 'purple' : 'cyan'}">${escape(ex.kind || 'function')}</span>
                            ${ex.line ? `<span>Line ${ex.line}</span>` : ''}
                        </div>
                    </div>
                    <div class="card-body">${escape(ex.reason || ex.explanation || '')}</div>
                </div>
            `).join('');

            if (emptyState) emptyState.style.display = 'none';
            container.style.display = 'flex';
        }

        static renderQuality(score, validation, warnings, aiStatus, reviewScore, qualitySummary, generationNotice, escapeFn = window.escapeHtml) {
            const emptyQuality = document.getElementById('empty-quality');
            const qualityContent = document.getElementById('quality-content');
            if (emptyQuality) emptyQuality.style.display = 'none';
            if (qualityContent) qualityContent.style.display = 'flex';

            const safeScore = score != null ? Math.max(0, Math.min(100, Math.round(score))) : 0;
            const escape = escapeFn || ((s) => String(s));

            const circle = document.getElementById('gauge-circle');
            const circumference = 2 * Math.PI * 70; // 439.82
            const strokeOffset = circumference - (safeScore / 100) * circumference;
            if (circle) {
                circle.style.strokeDashoffset = strokeOffset;
            }
            const scoreValueElem = document.getElementById('score-value');
            if (scoreValueElem) scoreValueElem.textContent = safeScore;

            const valBadge = document.getElementById('validation-badge');
            const hasSyntax = (warnings || []).some((w) => w.rule_id === 'SYNTAX001' || /syntax/i.test(w.message || ''));
            const hasSec = (warnings || []).some((w) => String(w.rule_id || '').startsWith('SEC'));

            if (valBadge) {
                if (hasSyntax || safeScore === 0) {
                    valBadge.className = 'badge error';
                    valBadge.textContent = 'Syntax Failure ✗';
                } else if (hasSec) {
                    valBadge.className = 'badge error';
                    valBadge.textContent = 'Vulnerabilities Flagged ✗';
                } else if (safeScore >= 85) {
                    valBadge.className = 'badge success';
                    valBadge.textContent = 'High Static Quality ✓';
                } else if (safeScore >= 60) {
                    valBadge.className = 'badge warning';
                    valBadge.textContent = 'Moderate Quality ⚠';
                } else {
                    valBadge.className = 'badge warning';
                    valBadge.textContent = 'Remediation Recommended';
                }
            }

            const secDeductions = (warnings || []).filter((w) => String(w.rule_id || '').startsWith('SEC')).length * 30;
            const secVal = Math.max(0, 100 - secDeductions);
            const maintVal = Math.max(0, Math.min(100, safeScore + 5));
            const compVal = Math.max(20, 100 - ((reviewScore?.complexity_issues || 0) * 20));
            const typeVal = (warnings || []).some((w) => w.rule_id === 'TYPE001' || w.rule_id === 'NAME001') ? 50 : 100;

            let docVal = 75;
            if (reviewScore && typeof reviewScore.doc_coverage === 'number') {
                docVal = Math.round(reviewScore.doc_coverage);
            } else if (qualitySummary && typeof qualitySummary.doc_coverage === 'number') {
                docVal = Math.round(qualitySummary.doc_coverage);
            } else if (warnings) {
                const docWarnings = warnings.filter((w) => /docstring/i.test(w.message || '') || w.rule_id === 'DOC001');
                docVal = docWarnings.length > 0 ? Math.max(20, 100 - (docWarnings.length * 25)) : (safeScore > 80 ? 95 : 70);
            }

            this.setDimBar('dim-sec', secVal, secVal >= 80 ? 'emerald' : secVal >= 50 ? 'amber' : 'crimson');
            this.setDimBar('dim-maint', maintVal, maintVal >= 80 ? 'cyan' : 'amber');
            this.setDimBar('dim-comp', compVal, compVal >= 75 ? 'violet' : 'amber');
            this.setDimBar('dim-type', typeVal, typeVal === 100 ? 'emerald' : 'amber');
            this.setDimBar('dim-doc', docVal, docVal >= 80 ? 'cyan' : docVal >= 50 ? 'amber' : 'crimson');

            const details = document.getElementById('quality-details');
            if (details) {
                details.innerHTML = '';
                if (qualitySummary) {
                    details.innerHTML += `<div class="warning-item warning-info"><span><strong>Methodology:</strong> ${escape(qualitySummary.score_method || 'Heuristic AST-grounded score calculated without source execution.')}</span></div>`;
                }

                if (warnings && warnings.length > 0) {
                    warnings.forEach((w) => {
                        const severity = w.severity || (String(w.rule_id || '').startsWith('SEC') ? 'error' : 'warning');
                        const label = w.rule_id ? `[${w.rule_id}] ` : '';
                        details.innerHTML += `<div class="warning-item warning-${severity}"><span>${escape(label + (w.message || w))} ${w.line ? `(Line ${w.line})` : ''}</span></div>`;
                    });
                } else {
                    details.innerHTML += `<div class="warning-item warning-info" style="border-left-color: var(--accent-emerald);"><span>✓ No static quality or security warnings identified in this file.</span></div>`;
                }
            }
        }

        static setDimBar(idPrefix, val, colorClass) {
            const valElem = document.getElementById(`${idPrefix}-val`);
            const fillElem = document.getElementById(`${idPrefix}-fill`);
            if (valElem) valElem.textContent = `${val}%`;
            if (fillElem) {
                fillElem.style.width = `${val}%`;
                fillElem.className = `progress-fill ${colorClass}`;
            }
        }
    }

    window.AstVisualizer = AstVisualizer;
})(typeof window !== 'undefined' ? window : this);
