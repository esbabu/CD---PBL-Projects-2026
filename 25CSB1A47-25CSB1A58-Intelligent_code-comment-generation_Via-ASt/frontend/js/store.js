/**
 * AST Studio · Nexus State Store
 * Single centralized state machine and store for workspace and workflow state.
 */

(function (window) {
    'use strict';

    const WorkflowState = Object.freeze({
        IDLE: 'idle',
        PLANNING: 'planning',
        RUNNING: 'running',
        AWAITING_APPROVAL: 'awaiting_approval',
        COMPLETED: 'completed',
        FAILED: 'failed',
        CANCELLED: 'cancelled',
    });

    class NexusStateStore {
        constructor() {
            this._state = WorkflowState.IDLE;
            this._session = null;
            this._plan = null;
            this._audit = null;
            this._candidate = null;
            this._subscribers = new Set();
        }

        get state() {
            return this._state;
        }

        get session() {
            return this._session;
        }

        get plan() {
            return this._plan;
        }

        get audit() {
            return this._audit;
        }

        get candidate() {
            return this._candidate;
        }

        subscribe(listener) {
            if (typeof listener === 'function') {
                this._subscribers.add(listener);
                return () => this._subscribers.delete(listener);
            }
            return () => {};
        }

        _notify(prevState, meta = {}) {
            for (const listener of this._subscribers) {
                try {
                    listener(this._state, prevState, meta);
                } catch (err) {
                    console.error('[NexusStateStore] Listener error:', err);
                }
            }
        }

        setState(nextState, meta = {}) {
            const prevState = this._state;
            this._state = nextState;
            this._notify(prevState, meta);
        }

        setSession(session) {
            this._session = session;
            if (session && session.status) {
                const s = session.status.toLowerCase();
                if (s === 'awaiting_approval') {
                    this.setState(WorkflowState.AWAITING_APPROVAL, { session });
                } else if (s === 'completed') {
                    this.setState(WorkflowState.COMPLETED, { session });
                } else if (s === 'failed') {
                    this.setState(WorkflowState.FAILED, { session });
                } else if (s === 'cancelled') {
                    this.setState(WorkflowState.CANCELLED, { session });
                } else if (s === 'running') {
                    this.setState(WorkflowState.RUNNING, { session });
                }
            }
        }

        setPlan(plan) {
            this._plan = plan;
            if (plan) {
                this.setState(WorkflowState.PLANNING, { plan });
            }
        }

        setAudit(audit) {
            this._audit = audit;
        }

        setCandidate(candidate) {
            this._candidate = candidate;
        }

        reset() {
            const prevState = this._state;
            this._state = WorkflowState.IDLE;
            this._session = null;
            this._plan = null;
            this._audit = null;
            this._candidate = null;
            this._notify(prevState, { action: 'reset' });
        }
    }

    window.WorkflowState = WorkflowState;
    window.NexusStateStore = NexusStateStore;
    window.nexusStore = new NexusStateStore();
})(window);
