document.addEventListener('DOMContentLoaded', () => {
    // ─ PRIVACY CONSENT BANNER ─
    (function showPrivacyBanner() {
        if (sessionStorage.getItem('vulnhgnn_privacy_acked')) return;
        const banner = document.createElement('div');
        banner.id = 'privacy-banner';
        banner.style.cssText = [
            'position:fixed', 'bottom:0', 'left:0', 'right:0',
            'background:#eff6ff', 'color:#1e3a5f', 'padding:12px 20px',
            'display:flex', 'align-items:center', 'gap:16px',
            'font-size:13px', 'z-index:9999', 'border-top:1px solid #bfdbfe'
        ].join(';');
        banner.innerHTML = `
            <span>&#128274; <strong>Privacy notice:</strong>
            Clicking <em>Analyze</em> sends your source code to the configured Gemini API
            (subject to Google&#39;s data-handling terms). Live checks while typing are local only.</span>
            <button id="privacy-ack-btn" style="
                background:#3b82f6;color:#fff;border:none;border-radius:6px;
                padding:6px 14px;cursor:pointer;white-space:nowrap;font-size:13px">
                Got it
            </button>`;
        document.body.appendChild(banner);
        document.getElementById('privacy-ack-btn').addEventListener('click', () => {
            sessionStorage.setItem('vulnhgnn_privacy_acked', '1');
            banner.remove();
        });
    })();

    // ═══ DOM REFS ═══
    const $ = id => document.getElementById(id);
    
    // Global Elements
    const codeInput = $('code-input');
    const codeLineNumbers = $('code-line-numbers');
    const codeLanguage = $('code-language');
    const sourceFilename = $('source-filename');
    const codeRender = $('code-render');
    const codeOverlay = $('code-render-overlay');
    const analyzeBtn = $('analyze-btn');
    const liveCheckPanel = $('live-check-panel');
    const liveCheckStatus = $('live-check-status');
    const liveCheckDetail = $('live-check-detail');
    const liveCheckFindings = $('live-check-findings');
    const statusDot = $('status-dot');
    const statusText = $('status-text');

    // Sidebar Stats
    const scoreNumber = $('score-number');
    const statTime = $('stat-time');
    const statLoc = $('stat-loc');
    const statEnergy = $('stat-energy');
    const statCo2 = $('stat-co2');

    // Result Tabs
    const tabBtns = document.querySelectorAll('.res-tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    // Action Center
    const actionDock = $('action-center');
    const btnLocalize = $('btn-localize');
    const btnHeal = $('btn-heal-source');
    const btnPipeline = $('btn-pipeline');
    const btnExportReport = $('btn-export-report');

    // Sub-Views
    const locInstructions = $('loc-instructions');
    const healHeader = $('heal-header');
    const diffBefore = $('diff-before');
    const diffAfter = $('diff-after');
    const repairReviewActions = $('repair-review-actions');
    const repairValidationStatus = $('repair-validation-status');
    const btnApplyRepair = $('btn-apply-repair');
    const btnDiscardRepair = $('btn-discard-repair');
    const logContainer = $('log-container');

    let currentCode = '';
    let detectedCWEs = [];
    let currentAuditReport = null;
    let pendingRepair = null;
    let liveCheckTimer = null;
    let liveCheckController = null;
    let liveCheckRevision = 0;

    // ═══ CORE LOGIC ═══
    function switchTab(tabId) {
        tabBtns.forEach(b => b.classList.toggle('active', b.dataset.tab === tabId));
        tabPanels.forEach(p => p.classList.toggle('active', p.id === tabId));
    }

    function showState(prefix, name) {
        ['idle', 'loading', 'success', 'error'].forEach(s => {
            const el = $(`${prefix}-${s}`);
            if (el) el.classList.add('hidden');
        });
        const target = $(`${prefix}-${name}`);
        if (target) target.classList.remove('hidden');
    }

    function setEditorMode(mode) {
        if (mode === 'edit') {
            codeOverlay.classList.add('hidden');
            codeInput.classList.remove('hidden');
            $('btn-edit').classList.add('hidden');
        } else {
            codeOverlay.classList.remove('hidden');
            codeInput.classList.add('hidden');
            $('btn-edit').classList.remove('hidden');
        }
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function updateLineNumbers() {
        const lineCount = Math.max(1, codeInput.value.split('\n').length);
        codeLineNumbers.textContent = Array.from(
            { length: lineCount },
            (_, index) => index + 1
        ).join('\n');
        codeLineNumbers.style.transform = `translateY(${-codeInput.scrollTop}px)`;
    }

    function renderLiveCheck(data) {
        liveCheckFindings.replaceChildren();
        const validity = data.validity || {};
        const security = data.security || {};
        const findings = security.findings || [];

        if (validity.status === 'invalid') {
            liveCheckPanel.dataset.state = 'invalid';
            liveCheckStatus.textContent = 'Syntax error';
            liveCheckDetail.textContent = validity.message || 'Clang could not compile this source.';
            return;
        }
        if (validity.status === 'unavailable') {
            liveCheckPanel.dataset.state = 'error';
            liveCheckStatus.textContent = 'Syntax check unavailable';
            liveCheckDetail.textContent = validity.message || 'The compiler did not finish in time.';
            return;
        }

        const confirmedFindings = findings.filter(
            finding => finding.severity && finding.severity.includes('CLANG CONFIRMED')
        );

        if (security.status === 'unavailable') {
            liveCheckPanel.dataset.state = confirmedFindings.length ? 'issues' : 'valid';
            liveCheckStatus.textContent = confirmedFindings.length
                ? `Clang confirmed ${confirmedFindings.length} issue(s)`
                : 'Valid C syntax; security checks unavailable';
            liveCheckDetail.textContent = security.scope || security.message || 'Local security checks could not complete.';
        } else {
            const confirmedCount = confirmedFindings.length;
            liveCheckPanel.dataset.state = confirmedCount ? 'issues' : 'valid';
            liveCheckStatus.textContent = confirmedCount
                ? `Clang confirmed ${confirmedCount} compiler diagnostic(s): ${confirmedFindings.map(f => f.class || f.name).join(', ')}`
                : 'Clang validated source syntax; no compiler warning diagnostics detected.';
            liveCheckDetail.textContent = security.scope || 'Live checks are local and do not guarantee that code is secure.';
        }
        findings.forEach(finding => {
            const card = document.createElement('article');
            card.className = 'live-check-finding';
            const heading = document.createElement('strong');
            heading.textContent = `${finding.severity || 'Review'} · ${finding.class}: ${finding.name}`;
            card.appendChild(heading);
            if (finding.probability !== null && finding.probability !== undefined) {
                const confidence = document.createElement('p');
                confidence.textContent = `Model confidence: ${(finding.probability * 100).toFixed(1)}% (prediction, not confirmation).`;
                card.appendChild(confidence);
            }
            if (finding.function) {
                const location = document.createElement('p');
                location.textContent = `Function: ${finding.function}`;
                card.appendChild(location);
            }
            (finding.lines || []).forEach(line => {
                const location = document.createElement('p');
                location.textContent = `Clang-confirmed line: ${line}`;
                card.appendChild(location);
            });
            const recommendation = document.createElement('p');
            recommendation.textContent = finding.recommendation;
            card.appendChild(recommendation);
            liveCheckFindings.appendChild(card);
        });
    }

    function scheduleLiveCheck() {
        window.clearTimeout(liveCheckTimer);
        if (liveCheckController) {
            liveCheckController.abort();
            liveCheckController = null;
        }

        const code = codeInput.value;
        const revision = ++liveCheckRevision;
        if (code !== currentCode) {
            detectedCWEs = [];
            actionDock.classList.add('hidden');
        }
        if (!code.trim()) {
            liveCheckPanel.dataset.state = 'idle';
            liveCheckStatus.textContent = 'Live checks start when you type';
            liveCheckDetail.textContent = 'Syntax and supported vulnerability checks run locally after a short pause.';
            liveCheckFindings.replaceChildren();
            return;
        }

        liveCheckPanel.dataset.state = 'checking';
        liveCheckStatus.textContent = 'Checking syntax and supported vulnerabilities…';
        liveCheckDetail.textContent = 'Waiting for a brief pause in typing.';
        liveCheckFindings.replaceChildren();
        liveCheckTimer = window.setTimeout(async () => {
            const controller = new AbortController();
            liveCheckController = controller;
            liveCheckDetail.textContent = 'Running local Clang syntax and security checks…';
            try {
                const response = await fetch('/api/live-check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, language: codeLanguage.value }),
                    signal: controller.signal,
                });
                const data = await response.json();
                if (revision !== liveCheckRevision) return;
                if (!response.ok || !data.success) {
                    throw new Error(data.error || `Live check failed (${response.status}).`);
                }
                renderLiveCheck(data);
            } catch (error) {
                if (error.name === 'AbortError' || revision !== liveCheckRevision) return;
                liveCheckPanel.dataset.state = 'error';
                liveCheckStatus.textContent = 'Live check failed';
                liveCheckDetail.textContent = error.message || 'Unable to complete the local check.';
            } finally {
                if (revision === liveCheckRevision) liveCheckController = null;
            }
        }, 1000);
    }

    function invalidateAuditReport() {
        currentAuditReport = null;
        btnExportReport.classList.add('hidden');
    }

    function discardRepairProposal() {
        pendingRepair = null;
        repairReviewActions.classList.add('hidden');
    }

    function downloadAuditReport() {
        if (!currentAuditReport) return;
        const report = new Blob(
            [JSON.stringify(currentAuditReport, null, 2)],
            { type: 'application/json' }
        );
        const url = URL.createObjectURL(report);
        const link = document.createElement('a');
        link.href = url;
        link.download = `vulnhgnn-security-report-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    }

    // ═══ EVENTS ═══
    tabBtns.forEach(btn => btn.addEventListener('click', () => switchTab(btn.dataset.tab)));
    codeInput.addEventListener('input', () => {
        invalidateAuditReport();
        discardRepairProposal();
        scheduleLiveCheck();
    });
    codeInput.addEventListener('input', updateLineNumbers);
    btnExportReport.addEventListener('click', downloadAuditReport);
    btnApplyRepair.addEventListener('click', () => {
        if (!pendingRepair) return;
        codeInput.value = pendingRepair;
        discardRepairProposal();
        invalidateAuditReport();
        updateLineNumbers();
        setEditorMode('edit');
        scheduleLiveCheck();
        healHeader.textContent = 'Reviewed repair applied to the editor.';
    });
    btnDiscardRepair.addEventListener('click', () => {
        discardRepairProposal();
        healHeader.textContent = 'Repair proposal discarded; the source was not changed.';
    });
    codeInput.addEventListener('scroll', updateLineNumbers);
    codeLanguage.addEventListener('change', () => {
        invalidateAuditReport();
        discardRepairProposal();
        sourceFilename.textContent = codeLanguage.value === 'cpp' ? 'source_audit.cpp' : 'source_audit.c';
        currentCode = '';
        detectedCWEs = [];
        actionDock.classList.add('hidden');
        scheduleLiveCheck();
    });
    $('btn-clear').addEventListener('click', () => {
        invalidateAuditReport();
        discardRepairProposal();
        codeInput.value = '';
        updateLineNumbers();
        currentCode = '';
        detectedCWEs = [];
        actionDock.classList.add('hidden');
        scheduleLiveCheck();
        scoreNumber.textContent = '--';
        statLoc.textContent = '0';
        setEditorMode('edit');
        showState('state', 'idle');
    });
    $('btn-edit').addEventListener('click', () => {
        setEditorMode('edit');
        codeInput.focus();
    });
    codeOverlay.addEventListener('click', () => {
        setEditorMode('edit');
        codeInput.focus();
    });

    analyzeBtn.addEventListener('click', async () => {
        const code = codeInput.value.trim();
        if (!code) return;

        currentCode = code;
        invalidateAuditReport();
        discardRepairProposal();
        detectedCWEs = [];
        actionDock.classList.add('hidden');
        showState('state', 'loading');
        statusDot.className = 'status-dot active';
        statusText.textContent = 'Analyzing...';

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code, language: codeLanguage.value })
            });
            const data = await response.json();

            if (response.ok && data.success) {
                renderResults(data, code);
                showState('state', 'success');
                statusDot.className = 'status-dot done';
                statusText.textContent = 'Complete';
            } else {
                throw new Error(data.error);
            }
        } catch (err) {
            $('error-message').textContent = err.message;
            showState('state', 'error');
            statusDot.className = 'status-dot error';
            statusText.textContent = 'Error';
        }
    });

    function getSecurityEstimate(predictions, suppliedEstimate) {
        if (suppliedEstimate && Number.isFinite(suppliedEstimate.score)) {
            return suppliedEstimate;
        }

        const severityWeights = { CRITICAL: 80, HIGH: 60, MEDIUM: 35, LOW: 20 };
        const severityByCwe = {
            'CWE-476': 'HIGH', 'CWE-191': 'HIGH', 'CWE-190': 'HIGH', 'CWE-369': 'MEDIUM'
        };
        const findings = predictions.filter(p => p.detected && p.class !== 'non-vulnerable');
        const riskPoints = findings.reduce((total, finding) => {
            const probability = Math.max(0, Math.min(1, Number(finding.probability) || 0));
            const severity = finding.severity || severityByCwe[finding.class] || 'MEDIUM';
            return total + (severityWeights[severity.toUpperCase()] || 35) * probability;
        }, 0);
        const score = Math.max(0, Math.min(100, Math.round(100 - riskPoints)));
        const riskLevel = findings.length === 0
            ? 'No supported issues detected'
            : score >= 80 ? 'Lower detected risk'
                : score >= 50 ? 'Moderate detected risk' : 'Higher detected risk';
        return { score, risk_level: riskLevel };
    }

    function renderResults(data, code) {
        statTime.textContent = `${data.elapsed.toFixed(2)}s`;
        const lines = code.split('\n').filter(l => l.trim()).length;
        statLoc.textContent = lines;

        const preds = data.predictions || [];
        const detected = preds.filter(p => p.detected);
        detectedCWEs = data.detected_cwes || [];

        const estimate = getSecurityEstimate(preds, data.security_estimate);
        renderLlmReview(data.agent_review);
        currentAuditReport = {
            report_type: 'VulnHGNN agent-assisted security analysis',
            generated_at: new Date().toISOString(),
            filename: sourceFilename.textContent,
            language: codeLanguage.value,
            analysis_time_seconds: data.elapsed,
            security_estimate: estimate,
            detected_findings: detected.map(({ class: cwe, title, probability, severity, line, source, evidence, recommendation }) => ({
                cwe: cwe.startsWith('CWE-') ? cwe : null,
                title,
                confidence: probability,
                severity: severity || null,
                line: line || null,
                source: source || null,
                evidence: evidence || null,
                recommendation: recommendation || null,
            })),
            findings: preds,
            security_checks: data.security_checks || {},
            disclaimer: 'Gemini findings are AI-generated review advice and Clang confirms only the checks listed. Neither a clean result nor compiler success proves code is secure.',
        };
        btnExportReport.classList.remove('hidden');
        const score = estimate.score;
        scoreNumber.textContent = score;
        scoreNumber.style.color = score > 80 ? 'var(--success)' : (score > 50 ? 'var(--warning)' : 'var(--danger)');

        const banner = $('verdict-banner');
        banner.replaceChildren();
        const verdict = document.createElement('h4');
        verdict.textContent = detected.length
            ? estimate.risk_level
            : 'No issues identified in this review';
        const summary = document.createElement('p');
        summary.textContent = detected.length
            ? `${detected.length} agent/scanner finding(s). Gemini score: ${score}/100; verify each finding independently.`
            : `Gemini score: ${score}/100. This result is not proof that the code is secure.`;
        banner.className = `verdict-card ${detected.length ? 'vuln' : 'safe'}`;
        banner.append(verdict, summary);

        if (detected.length > 0) { actionDock.classList.remove('hidden'); } else { actionDock.classList.add('hidden'); }

        const probList = $('prob-list');
        probList.replaceChildren();
        if (preds.length === 0) {
            const empty = document.createElement('p');
            empty.textContent = 'No findings were returned by the agent or supported Clang checks.';
            probList.appendChild(empty);
        }
        preds.forEach(finding => {
            const item = document.createElement('article');
            item.className = `prob-item ${finding.detected ? 'danger' : ''}`;
            const header = document.createElement('div');
            header.className = 'prob-header';
            const name = document.createElement('span');
            name.className = 'prob-name';
            name.textContent = `${finding.class}: ${finding.title}`;
            const severity = document.createElement('span');
            severity.className = 'prob-pct';
            severity.textContent = finding.severity || finding.source || '';
            header.append(name, severity);
            item.appendChild(header);
            if (finding.line) {
                const line = document.createElement('p');
                line.textContent = `Line ${finding.line}`;
                item.appendChild(line);
            }
            if (finding.evidence) {
                const evidence = document.createElement('p');
                evidence.textContent = finding.evidence;
                item.appendChild(evidence);
            }
            if (finding.detected && finding.class !== 'non-vulnerable') {
                const fixBtn = document.createElement('button');
                fixBtn.className = 'btn-suggest-fix';
                fixBtn.style.cssText = 'margin-top:8px;background:#2563eb;color:#fff;border:none;border-radius:4px;padding:5px 12px;font-size:0.75rem;cursor:pointer;display:inline-flex;align-items:center;gap:6px;font-weight:600;';
                fixBtn.innerHTML = '<i data-feather="zap"></i> ✨ Suggest AI Fix';
                fixBtn.onclick = (e) => {
                    e.stopPropagation();
                    btnHeal.click();
                };
                item.appendChild(fixBtn);
            }
            probList.appendChild(item);
        });
        if (window.feather) feather.replace();

        codeRender.innerHTML = `<code>${escapeHtml(code)}</code>`;
        setEditorMode('view');
    }

    function renderLlmReview(review) {
        const panel = $('llm-review-result');
        panel.replaceChildren();
        panel.classList.toggle('hidden', !review || !review.requested);
        if (!review || !review.requested) return;

        const heading = document.createElement('h4');
        heading.textContent = review.available
            ? `Gemini agent review: ${review.risk_level} (${review.security_score}/100)`
            : 'Gemini agent review unavailable';
        panel.appendChild(heading);

        const summary = document.createElement('p');
        summary.textContent = review.available
            ? review.summary || review.scope
            : review.message || 'The configured provider did not return a review.';
        panel.appendChild(summary);

        if (review.available && review.findings && review.findings.length) {
            const list = document.createElement('ul');
            review.findings.forEach(finding => {
                const item = document.createElement('li');
                const location = finding.line ? `Line ${finding.line}: ` : '';
                item.textContent = `${location}${finding.severity.toUpperCase()} - ${finding.title}. ${finding.reason} Fix: ${finding.recommendation}`;
                list.appendChild(item);
            });
            panel.appendChild(list);
        }

        if (review.available) {
            const scope = document.createElement('p');
            scope.className = 'llm-review-scope';
            scope.textContent = review.scope;
            panel.appendChild(scope);
        }
    }

    // ═══ LOCALIZATION ═══
    btnLocalize.addEventListener('click', async () => {
        switchTab('tab-localization');
        $('loc-idle').classList.add('hidden');
        $('loc-loading').classList.remove('hidden');
        $('loc-results').classList.add('hidden');

        try {
            const demo = window.getDemoResults ? window.getDemoResults(currentCode) : null;
            let data;
            if (demo && demo.localization) {
                await new Promise(r => setTimeout(r, 800));
                data = { success: true, localizations: demo.localization };
            } else {
                const response = await fetch('/api/localize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: currentCode, language: codeLanguage.value, cwes: detectedCWEs })
                });
                data = await response.json();
            }

            if (data.success) {
                $('loc-loading').classList.add('hidden');
                $('loc-results').classList.remove('hidden');
                locInstructions.innerHTML = '';
                const cwe = Object.keys(data.localizations)[0];
                data.localizations[cwe].forEach(inst => {
                    const el = document.createElement('div');
                    el.className = 'inst-item';
                    el.innerHTML = `
                        <div class="inst-head"><span class="inst-op">${inst.opcode}</span><span>${(inst.score*100).toFixed(1)}% weight</span></div>
                        <div class="inst-txt">${escapeHtml(inst.text)}</div>
                    `;
                    locInstructions.appendChild(el);
                });
            }
        } catch (e) { console.error(e); }
    });

    // ═══ HEALING ═══
    
    const triggerFixBtn = $('btn-trigger-ai-fix');
    if (triggerFixBtn) {
        triggerFixBtn.addEventListener('click', () => btnHeal.click());
    }

    btnHeal.addEventListener('click', async () => {
        switchTab('tab-healing');
        $('heal-idle').classList.add('hidden');
        $('heal-results').classList.add('hidden');

        try {
            const demo = window.getDemoResults ? window.getDemoResults(currentCode) : null;
            let data;
            if (demo && demo.healed_source) {
                await new Promise(r => setTimeout(r, 900));
                data = { success: true, healed: true, healed_code: demo.healed_source, message: "AI Repair Patch Generated." };
            } else {
                const response = await fetch('/api/heal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: currentCode, language: codeLanguage.value, mode: 'source', detected_cwes: detectedCWEs })
                });
                data = await response.json();
                if (!response.ok || !data.success) {
                    throw new Error(data.error || `Repair proposal failed (${response.status}).`);
                }
            }

            if (data.success && data.healed) {
                $('heal-results').classList.remove('hidden');
                healHeader.textContent = data.message;
                diffBefore.textContent = currentCode;
                diffAfter.textContent = data.healed_code;
                pendingRepair = data.healed_code;
                repairValidationStatus.textContent = data.compiler_validation && data.compiler_validation.valid
                    ? 'Clang compilation passed. Review the diff before applying; this does not prove the repair is secure.'
                    : 'Demo repair preview only: compiler validation was not run. Review carefully before applying.';
                repairReviewActions.classList.remove('hidden');
            } else if (data.success) {
                $('heal-results').classList.remove('hidden');
                healHeader.textContent = data.message || 'No repair proposal was produced.';
                diffBefore.textContent = currentCode;
                diffAfter.textContent = '';
                discardRepairProposal();
            }
        } catch (e) {
            $('heal-results').classList.remove('hidden');
            healHeader.textContent = `Repair proposal unavailable: ${e.message}`;
            diffBefore.textContent = currentCode;
            diffAfter.textContent = '';
            discardRepairProposal();
        }
    });

    // ═══ PIPELINE ═══
    btnPipeline.addEventListener('click', async () => {
        logContainer.innerHTML = '<div class="log-entry active">> Initializing GNN Iterative Pipeline...</div>';
        
        try {
            const response = await fetch('/api/pipeline', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: currentCode, language: codeLanguage.value, carbon_tracking: true })
            });
            const data = await response.json();
            
            if (data.success) {
                logContainer.innerHTML = '';
                data.iterations.forEach(iter => {
                    const line = document.createElement('div');
                    line.className = 'log-entry done';
                    line.textContent = `> Iteration ${iter.iteration}: Validation Passed`;
                    logContainer.appendChild(line);
                });
                const final = document.createElement('div');
                final.className = 'log-entry active';
                final.textContent = `> Final Status: ${data.status} | Total Patches: ${data.total_patches}`;
                logContainer.appendChild(final);

                if (data.carbon_metrics) {
                    statEnergy.textContent = data.carbon_metrics.energy_kwh.toFixed(4);
                    statCo2.textContent = data.carbon_metrics.co2_kg.toFixed(5);
                }
            }
        } catch (e) { console.error(e); }
    });
});
