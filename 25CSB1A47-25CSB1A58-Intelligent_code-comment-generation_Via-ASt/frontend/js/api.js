/**
 * AST Studio · Nexus API Client
 * Typed, secure HTTP client for agentic endpoints with CSRF and error normalization.
 */

(function (window) {
    'use strict';

    class NexusApiError extends Error {
        constructor(message, status = 500, details = null) {
            super(message);
            this.name = 'NexusApiError';
            this.status = status;
            this.details = details;
        }
    }

    class NexusApiClient {
        constructor(baseUrl = '') {
            this.baseUrl = baseUrl.replace(/\/+$/, '');
        }

        _getCsrfToken() {
            const meta = document.querySelector('meta[name="csrf-token"]');
            if (meta && meta.content) {
                return meta.content;
            }
            const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/);
            return match ? decodeURIComponent(match[1]) : '';
        }

        async _fetch(endpoint, options = {}) {
            const url = `${this.baseUrl}${endpoint}`;
            const headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...(options.headers || {}),
            };

            const csrfToken = this._getCsrfToken();
            if (csrfToken && !headers['X-CSRFToken'] && !headers['X-CSRF-Token']) {
                headers['X-CSRFToken'] = csrfToken;
            }

            const fetchOptions = {
                ...options,
                headers,
                credentials: options.credentials || 'same-origin',
            };

            let response;
            try {
                response = await fetch(url, fetchOptions);
            } catch (networkErr) {
                throw new NexusApiError(`Network request failed: ${networkErr.message}`, 0);
            }

            let data;
            const text = await response.text();
            try {
                data = text ? JSON.parse(text) : {};
            } catch (parseErr) {
                data = { raw: text };
            }

            if (!response.ok) {
                const errorMsg = (data && (data.error || data.message)) || `Server returned ${response.status}`;
                throw new NexusApiError(errorMsg, response.status, data);
            }

            return data;
        }

        async getStatus() {
            return this._fetch('/agentic/status');
        }

        async previewPlan(task, code = '', intent = null, workspaceId = null, activeFile = null) {
            const payload = { task };
            if (code) payload.code = code;
            if (intent) payload.intent = intent;
            if (workspaceId) payload.workspace_id = workspaceId;
            if (activeFile) payload.active_file = activeFile;
            return this._fetch('/agentic/plan/preview', {
                method: 'POST',
                body: JSON.stringify(payload),
            });
        }

        async startRun({ task, code = '', intent = null, autoApprove = false, async = true, executionMode = null, workspaceId = null, activeFile = null }) {
            const payload = {
                task,
                code,
                auto_approve: Boolean(autoApprove),
                async: Boolean(async),
            };
            if (intent) payload.intent = intent;
            if (executionMode) payload.execution_mode = executionMode;
            if (workspaceId) payload.workspace_id = workspaceId;
            if (activeFile) payload.active_file = activeFile;

            return this._fetch('/agentic/run', {
                method: 'POST',
                body: JSON.stringify(payload),
            });
        }

        async getTicket(sessionId) {
            return this._fetch(`/agentic/session/${encodeURIComponent(sessionId)}/ticket`, {
                method: 'POST',
            });
        }

        async submitAction(sessionId, action, candidateDigest = null, feedback = '') {
            const payload = {
                session_id: sessionId,
                action,
                feedback,
            };
            if (candidateDigest) {
                payload.candidate_digest = candidateDigest;
            }
            return this._fetch('/agentic/action', {
                method: 'POST',
                body: JSON.stringify(payload),
            });
        }

        async cancelRun(sessionId) {
            return this._fetch(`/agentic/cancel/${encodeURIComponent(sessionId)}`, {
                method: 'POST',
            });
        }

        async getSession(sessionId) {
            return this._fetch(`/agentic/session/${encodeURIComponent(sessionId)}`);
        }
    }

    window.NexusApiError = NexusApiError;
    window.NexusApiClient = NexusApiClient;
    window.nexusApi = new NexusApiClient();
})(window);
