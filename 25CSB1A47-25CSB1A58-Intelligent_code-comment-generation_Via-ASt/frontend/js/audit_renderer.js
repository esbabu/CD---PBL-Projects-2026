/**
 * AST Studio · Nexus Audit & Verification Renderer
 * Strict verification contract normalizer and DOM renderer for independent audit results.
 */

(function (window) {
    'use strict';

    function escapeHtml(str) {
        if (str === null || str === undefined) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function migrateLegacyAudit(raw) {
        if (!raw || typeof raw !== 'object') {
            return {
                schema_version: 1,
                status: 'not_run',
                verification_level: 'static_only',
                checks: {
                    syntax: { status: 'not_run', evidence: 'Not run', details: 'No audit recorded' },
                    definitions: { status: 'not_run', evidence: 'Not run', details: 'No audit recorded' },
                    security: { status: 'not_run', evidence: 'Not run', details: 'No audit recorded' },
                    types: { status: 'not_run', evidence: 'Not run', details: 'No audit recorded' },
                    behavior: { status: 'not_run', evidence: 'Not run', details: 'No audit recorded' },
                    approval: { status: 'not_run', evidence: 'Not run', details: 'No audit recorded' }
                },
                summary: 'Independent verification: NOT RUN. No audit payload recorded.',
                failures: [],
                warnings: ['No audit recorded']
            };
        }

        // Already valid schema_version 1
        if (raw.schema_version === 1 && raw.checks && typeof raw.checks === 'object') {
            const required = ['syntax', 'definitions', 'security', 'types', 'behavior', 'approval'];
            const checks = { ...raw.checks };
            required.forEach(k => {
                if (!checks[k] || typeof checks[k] !== 'object' || !checks[k].status) {
                    checks[k] = { status: 'not_run', evidence: 'Check missing from audit payload', details: 'Not evaluated' };
                }
            });

            // Derive final status strictly from required checks
            let derivedStatus = 'passed';
            let hasFailure = false;
            let hasNotRun = false;

            for (const key of required) {
                const s = checks[key].status;
                if (s === 'failed') {
                    hasFailure = true;
                    break;
                }
                if (s === 'not_run' || s === 'unknown') {
                    hasNotRun = true;
                }
            }

            if (hasFailure) {
                derivedStatus = 'failed';
            } else if (hasNotRun) {
                derivedStatus = (raw.status === 'failed') ? 'failed' : 'not_run';
            } else {
                derivedStatus = 'passed';
            }

            return {
                schema_version: 1,
                status: derivedStatus,
                verification_level: raw.verification_level === 'full' ? 'full' : 'static_only',
                checks,
                summary: raw.summary || `Independent verification: ${derivedStatus.toUpperCase()}.`,
                failures: Array.isArray(raw.failures) ? raw.failures : [],
                warnings: Array.isArray(raw.warnings) ? raw.warnings : []
            };
        }

        // Legacy payload migration
        const checks = {
            syntax: { status: 'not_run', evidence: 'Legacy audit omitted syntax verification', details: '' },
            definitions: { status: 'not_run', evidence: 'Legacy audit omitted definition preservation check', details: '' },
            security: { status: 'not_run', evidence: 'Legacy audit omitted security verification', details: '' },
            types: { status: 'not_run', evidence: 'Legacy audit omitted type consistency check', details: '' },
            behavior: { status: 'not_run', evidence: 'Legacy audit omitted sandbox behavioral test', details: '' },
            approval: { status: 'not_run', evidence: 'Legacy audit omitted operator approval validation', details: '' }
        };

        if (raw.syntax_valid === true) {
            checks.syntax = { status: 'passed', evidence: 'Syntax valid', details: 'Parsed successfully via ast.parse' };
        } else if (raw.syntax_valid === false) {
            checks.syntax = { status: 'failed', evidence: 'Syntax error detected', details: raw.syntax_error || 'Syntax invalid' };
        }

        if (raw.definitions_preserved === true) {
            checks.definitions = { status: 'passed', evidence: 'Top-level functions & classes preserved', details: '' };
        } else if (raw.definitions_preserved === false) {
            checks.definitions = { status: 'failed', evidence: 'Definition contract broken', details: 'Missing definitions' };
        }

        if (raw.security_verified === true) {
            checks.security = { status: 'passed', evidence: 'Static AST security checks clean', details: '' };
        } else if (raw.security_verified === false) {
            checks.security = { status: 'failed', evidence: 'Security vulnerabilities or regressions found', details: '' };
        }

        if (raw.types_consistent === true) {
            checks.types = { status: 'passed', evidence: 'Type annotations preserved', details: '' };
        } else if (raw.types_consistent === false) {
            checks.types = { status: 'failed', evidence: 'Type inconsistencies flagged', details: '' };
        }

        if (raw.behavior_verified === true) {
            checks.behavior = { status: 'passed', evidence: 'Behavior preserved in sandbox execution', details: '' };
        } else if (raw.behavior_verified === false) {
            checks.behavior = { status: 'failed', evidence: 'Behavior regression detected in sandbox', details: '' };
        }

        if (raw.operator_approved === true) {
            checks.approval = { status: 'passed', evidence: 'Approved by operator', details: '' };
        } else if (raw.operator_approved === false) {
            checks.approval = { status: 'failed', evidence: 'Operator approval rejected or pending', details: '' };
        }

        let legacyStatus = 'not_run';
        if (Object.values(checks).some(c => c.status === 'failed')) {
            legacyStatus = 'failed';
        } else if (Object.values(checks).every(c => c.status === 'passed')) {
            legacyStatus = 'passed';
        }

        return {
            schema_version: 1,
            status: legacyStatus,
            verification_level: raw.verification_level === 'full' ? 'full' : 'static_only',
            checks,
            summary: raw.summary || `Migrated legacy audit: ${legacyStatus.toUpperCase()}.`,
            failures: raw.failures || [],
            warnings: ['Payload migrated from legacy unversioned audit contract'],
            passed: legacyStatus === 'passed'
        };
    }

    class NexusAuditRenderer {
        static escapeHtml(str) {
            return escapeHtml(str);
        }

        static migrate(raw) {
            return migrateLegacyAudit(raw);
        }

        static renderVerificationBox(container, audit) {
            if (!container) return;
            const norm = migrateLegacyAudit(audit);
            const levelLabel = norm.verification_level === 'full'
                ? '<span class="badge success" style="font-size:11px; padding:2px 8px;">FULL VERIFICATION</span>'
                : '<span class="badge warning" style="font-size:11px; padding:2px 8px;">STATIC ONLY</span>';

            let verHtml = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding:8px 12px; background:#f8fafc; border-radius:6px; border:1px solid var(--border-subtle);">
                    <div>
                        <strong>Verification Level:</strong> ${levelLabel}
                        <span style="font-size:12px; color:var(--text-secondary); margin-left:8px;">${norm.verification_level === 'full' ? 'Verified in isolated disposable sandbox' : 'Static AST & heuristic verification (sandbox not executed)'}</span>
                    </div>
                    <div>
                        <strong>Audit Status:</strong> <span class="badge ${norm.status === 'passed' ? 'success' : norm.status === 'failed' ? 'error' : ''}">${norm.status.toUpperCase().replace(/_/g, ' ')}</span>
                    </div>
                </div>
                <table class="results-audit-table"><thead><tr><th>Verification Check</th><th>Result</th><th>Auditor Evidence &amp; Details</th></tr></thead><tbody>
            `;

            const checkRows = [
                ['Syntax Validity', norm.checks.syntax],
                ['Definition Preservation', norm.checks.definitions],
                ['Security Vulnerabilities & Regressions', norm.checks.security],
                ['Static Type Consistency', norm.checks.types],
                ['Behavioral Sandbox Tests', norm.checks.behavior],
                ['Operator Approval', norm.checks.approval]
            ];

            checkRows.forEach(([label, check]) => {
                const chk = check || { status: 'not_run', evidence: 'Not run', details: '' };
                const statusBadge = chk.status === 'passed'
                    ? '<span class="badge success">PASSED</span>'
                    : chk.status === 'failed'
                        ? '<span class="badge error">FAILED</span>'
                        : '<span class="badge" style="background:#e2e8f0; color:#475569;">NOT RUN</span>';
                const extra = chk.details && chk.details !== chk.evidence ? ` <span style="opacity:0.7;">(${escapeHtml(chk.details)})</span>` : '';
                verHtml += `<tr><td><strong>${escapeHtml(label)}</strong></td><td>${statusBadge}</td><td>${escapeHtml(chk.evidence || '')}${extra}</td></tr>`;
            });
            verHtml += `</tbody></table>`;
            container.innerHTML = verHtml;
        }
    }

    window.escapeHtml = window.escapeHtml || escapeHtml;
    window.migrateLegacyAudit = migrateLegacyAudit;
    window.NexusAuditRenderer = NexusAuditRenderer;
})(window);
