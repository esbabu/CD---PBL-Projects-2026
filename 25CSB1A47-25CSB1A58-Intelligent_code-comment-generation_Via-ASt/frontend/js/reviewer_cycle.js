/**
 * AST Studio · Autonomous Reviewer Cycle (Pedagogical QA Loop)
 * Coordinates engineering and reviewer agent iterations, grading, and diff inspection.
 */

(function (window) {
    'use strict';

    class ReviewerCycle {
        constructor() {
            this.lastApprovedCode = '';
        }

        getLastApprovedCode() {
            return this.lastApprovedCode;
        }

        setLastApprovedCode(code) {
            this.lastApprovedCode = code || '';
        }

        renderIterationCards(iterations, container, escapeFn) {
            if (!container || !Array.isArray(iterations)) return;
            const escape = escapeFn || window.escapeHtml || ((s) => String(s));
            container.innerHTML = '';

            iterations.forEach((it) => {
                const card = document.createElement('div');
                card.className = 'prof-iteration-card';

                const itGrade = it.grade || '-';
                const gradeClass = ['A+', 'A'].includes(itGrade)
                    ? 'prof-grade-a'
                    : itGrade === 'B'
                    ? 'prof-grade-b'
                    : itGrade === 'C'
                    ? 'prof-grade-c'
                    : 'prof-grade-df';

                const header = document.createElement('div');
                header.className = 'prof-iteration-header';
                header.innerHTML = `
                    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                        <span class="badge" style="background:rgba(255,255,255,0.08);">Iteration #${it.iteration}</span>
                        <span class="prof-grade-pill ${gradeClass}">Grade ${itGrade}</span>
                        <span style="font-size:0.8rem; color:var(--text-secondary,#94a3b8);">Score: ${it.score}/100</span>
                    </div>
                    <span class="badge ${it.passed ? 'success' : 'error'}">${it.passed ? 'Verified' : 'Revision Requested'}</span>
                `;
                card.appendChild(header);

                if (Array.isArray(it.findings) && it.findings.length > 0) {
                    const findingsContainer = document.createElement('div');
                    findingsContainer.style.marginTop = '10px';
                    findingsContainer.style.display = 'flex';
                    findingsContainer.style.flexDirection = 'column';
                    findingsContainer.style.gap = '8px';

                    it.findings.forEach((f) => {
                        const item = document.createElement('div');
                        item.className = 'prof-finding-item';
                        item.style.padding = '8px 12px';
                        item.style.borderRadius = '6px';
                        item.style.background = 'rgba(255,255,255,0.03)';
                        item.style.border = '1px solid rgba(255,255,255,0.08)';

                        const cat = f.category || 'Quality';
                        const catBadgeClass = cat === 'Security'
                            ? 'badge error'
                            : cat === 'Performance'
                            ? 'badge warning'
                            : cat === 'Documentation'
                            ? 'badge purple'
                            : 'badge';

                        item.innerHTML = `
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px; flex-wrap:wrap;">
                                <span class="${catBadgeClass}" style="font-size:0.75rem; padding:2px 6px;">${escape(cat)}</span>
                                <strong style="font-size:0.85rem; color:var(--text-primary,#f8fafc);">${escape(f.title || f.message || 'Issue')}</strong>
                                ${f.line ? `<span style="font-size:0.75rem; color:var(--text-secondary,#94a3b8); margin-left:auto;">Line ${f.line}</span>` : ''}
                            </div>
                            ${f.explanation ? `<div style="font-size:0.8rem; color:var(--text-secondary,#cbd5e1); margin-top:4px;"><strong>🔍 What is wrong:</strong> ${escape(f.explanation)}</div>` : ''}
                            ${f.why_it_matters ? `<div style="font-size:0.8rem; color:#f59e0b; margin-top:2px;"><strong>⚠️ Why it matters:</strong> ${escape(f.why_it_matters)}</div>` : ''}
                            ${f.suggested_fix ? `<div style="font-size:0.8rem; color:#10b981; margin-top:2px;"><strong>💡 Recommended fix:</strong> ${escape(f.suggested_fix)}</div>` : ''}
                        `;
                        findingsContainer.appendChild(item);
                    });
                    card.appendChild(findingsContainer);
                } else if (Array.isArray(it.critique) && it.critique.length > 0) {
                    const ul = document.createElement('ul');
                    ul.className = 'prof-critique-list';
                    it.critique.forEach((c) => {
                        const li = document.createElement('li');
                        li.textContent = c;
                        ul.appendChild(li);
                    });
                    card.appendChild(ul);
                }
                container.appendChild(card);
            });
        }

        async runReview({
            code,
            maxIterations = 5,
            requestJsonFn = window.requestJson,
            escapeFn = window.escapeHtml,
            showToastFn = window.showToast,
            showProgressFn = window.showProgress,
            hideProgressFn = window.hideProgress,
            describeFetchIssueFn = window.describeFetchIssue,
            renderUnifiedDiffFn = window.renderUnifiedDiff,
        }) {
            if (!code || !code.trim()) {
                if (showToastFn) {
                    showToastFn('Please enter Python code in the active editor before running the review.', 'warning');
                }
                return null;
            }

            const btn = document.getElementById('btn-run-professor-student');
            const loopStatus = document.getElementById('prof-loop-status');
            const resultsBox = document.getElementById('prof-student-results');
            const gradeBadge = document.getElementById('prof-final-grade-badge');
            const scoreText = document.getElementById('prof-final-score-text');
            const iterCountBadge = document.getElementById('prof-iterations-count');
            const approvalPill = document.getElementById('prof-approval-pill');
            const summaryText = document.getElementById('prof-summary-text');
            const timelineContainer = document.getElementById('prof-timeline-container');
            const diffBox = document.getElementById('prof-diff-box');
            const diffContainer = document.getElementById('prof-diff-container');

            if (btn) btn.disabled = true;
            if (loopStatus) {
                loopStatus.className = 'badge purple';
                loopStatus.textContent = 'Auditing...';
            }
            if (showProgressFn) {
                showProgressFn('Reviewer Agent is assessing the Engineering Agent output within the configured review-cycle limit...');
            }

            try {
                const req = requestJsonFn || (async (url, opts) => {
                    const res = await fetch(url, opts);
                    return { data: await res.json() };
                });

                const { data } = await req('/agent/professor-student', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, max_iterations: maxIterations }),
                });

                if (resultsBox) resultsBox.style.display = 'block';

                const grade = data.final_grade || 'F';
                const score = data.final_score !== undefined ? data.final_score : 0;
                const approved = Boolean(data.approved);

                if (gradeBadge) {
                    gradeBadge.textContent = `Grade ${grade}`;
                    gradeBadge.className = 'badge prof-grade-pill ' + (
                        ['A+', 'A'].includes(grade)
                            ? 'prof-grade-a'
                            : grade === 'B'
                            ? 'prof-grade-b'
                            : grade === 'C'
                            ? 'prof-grade-c'
                            : 'prof-grade-df'
                    );
                }

                if (scoreText) scoreText.textContent = `Score: ${score}/100`;
                if (iterCountBadge) iterCountBadge.textContent = `${data.iterations_count || 1} iteration(s)`;

                const resolvedCount = data.resolved_count !== undefined
                    ? data.resolved_count
                    : (data.resolved_issues ? data.resolved_issues.length : 0);
                const remainingCount = data.remaining_count !== undefined
                    ? data.remaining_count
                    : (data.remaining_issues ? data.remaining_issues.length : 0);

                const resolvedPill = document.getElementById('prof-resolved-pill');
                const remainingPill = document.getElementById('prof-remaining-pill');
                if (resolvedPill) {
                    resolvedPill.textContent = `${resolvedCount} Resolved`;
                    resolvedPill.style.display = 'inline-block';
                }
                if (remainingPill) {
                    remainingPill.textContent = `${remainingCount} Remaining`;
                    remainingPill.style.display = remainingCount > 0 ? 'inline-block' : 'none';
                }

                if (approvalPill) {
                    approvalPill.className = approved ? 'badge success' : 'badge error';
                    approvalPill.textContent = approved ? 'Reviewer Approved' : 'Improvements Requested';
                }
                if (summaryText) summaryText.textContent = data.summary || '';

                if (timelineContainer && Array.isArray(data.iterations)) {
                    this.renderIterationCards(data.iterations, timelineContainer, escapeFn);
                }

                this.lastApprovedCode = data.final_code || '';

                if (diffBox && diffContainer) {
                    if (data.code_modified && data.diff) {
                        diffBox.style.display = 'block';
                        if (renderUnifiedDiffFn) {
                            renderUnifiedDiffFn(code, data.final_code || code, diffContainer);
                        }
                    } else {
                        diffBox.style.display = 'none';
                    }
                }

                if (loopStatus) {
                    loopStatus.className = approved ? 'badge success' : 'badge';
                    loopStatus.textContent = approved ? 'Approved' : 'Completed';
                }
                if (showToastFn) {
                    showToastFn(`Agent review complete: Grade ${grade} (${score}/100)`, approved ? 'success' : 'info');
                }
                return data;
            } catch (err) {
                if (showToastFn && describeFetchIssueFn) {
                    showToastFn(describeFetchIssueFn(err), 'error');
                }
                if (loopStatus) {
                    loopStatus.className = 'badge error';
                    loopStatus.textContent = 'Failed';
                }
                throw err;
            } finally {
                if (hideProgressFn) hideProgressFn();
                if (btn) btn.disabled = false;
            }
        }

        applyApprovedCode(editorElem, onApplied) {
            if (!this.lastApprovedCode) {
                if (window.showToast) {
                    window.showToast('No approved code available to apply.', 'warning');
                }
                return false;
            }
            if (editorElem) {
                editorElem.value = this.lastApprovedCode;
                if (typeof onApplied === 'function') {
                    onApplied();
                } else {
                    if (window.updateEditorOverlay) window.updateEditorOverlay();
                    if (window.updateSandboxSourceStatus) window.updateSandboxSourceStatus();
                    if (window.showToast) {
                        window.showToast('Applied the reviewer-approved code to the active editor.', 'success');
                    }
                }
                return true;
            }
            return false;
        }
    }

    window.ReviewerCycle = ReviewerCycle;
    window.reviewerCycle = new ReviewerCycle();
})(typeof window !== 'undefined' ? window : this);
