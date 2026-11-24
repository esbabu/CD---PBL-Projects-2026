/**
 * AST Studio · Nexus Workflow Controller
 * Orchestrates user intentions, plan preview, run dispatch, approvals, and cancellation.
 */

(function (window) {
    'use strict';

    class NexusWorkflowController {
        constructor(store = window.nexusStore, api = window.nexusApi, sse = window.nexusSSE) {
            this.store = store;
            this.api = api;
            this.sse = sse;
        }

        async previewPlan(task, code = '', intent = null, workspaceId = null, activeFile = null) {
            if (!task || !task.trim()) {
                throw new Error('A task or engineering goal is required.');
            }
            try {
                const planData = await this.api.previewPlan(task, code, intent, workspaceId, activeFile);
                if (this.store) {
                    this.store.setPlan(planData);
                }
                return planData;
            } catch (err) {
                console.error('[NexusWorkflowController] Plan preview failed:', err);
                throw err;
            }
        }

        async startWorkflow({ task, code = '', intent = null, autoApprove = false, async = true, executionMode = null, workspaceId = null, activeFile = null }) {
            if (!task || !task.trim()) {
                throw new Error('A task or engineering goal is required to start.');
            }
            try {
                if (this.store) {
                    this.store.setState(window.WorkflowState.RUNNING);
                }
                const runResponse = await this.api.startRun({
                    task,
                    code,
                    intent,
                    autoApprove,
                    async,
                    executionMode,
                    workspaceId,
                    activeFile,
                });

                if (runResponse && runResponse.session_id) {
                    if (this.store) {
                        this.store.setSession(runResponse);
                    }
                    if (this.sse && runResponse.execution_mode === 'async') {
                        let ticket = '';
                        try {
                            const ticketData = await this.api.getTicket(runResponse.session_id);
                            ticket = ticketData.ticket || '';
                        } catch (ticketErr) {
                            console.warn('[NexusWorkflowController] Ticket acquisition skipped:', ticketErr);
                        }
                        this.sse.connect(runResponse.session_id, ticket);
                    }
                }
                return runResponse;
            } catch (err) {
                if (this.store) {
                    this.store.setState(window.WorkflowState.FAILED, { error: err.message });
                }
                throw err;
            }
        }

        async submitApproval(sessionId, action, candidateDigest = null, feedback = '') {
            if (!sessionId) {
                throw new Error('No active session ID provided for approval.');
            }
            const res = await this.api.submitAction(sessionId, action, candidateDigest, feedback);
            if (this.store && res.session) {
                this.store.setSession(res.session);
            }
            return res;
        }

        async cancelWorkflow(sessionId) {
            if (!sessionId) return null;
            const res = await this.api.cancelRun(sessionId);
            if (this.store) {
                this.store.setState(window.WorkflowState.CANCELLED);
            }
            if (this.sse) {
                this.sse.disconnect();
            }
            return res;
        }
    }

    window.NexusWorkflowController = NexusWorkflowController;
    window.nexusController = new NexusWorkflowController();
})(window);
