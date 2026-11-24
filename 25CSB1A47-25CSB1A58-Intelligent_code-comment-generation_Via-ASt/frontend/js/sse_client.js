/**
 * AST Studio · Nexus SSE Client
 * Reliable Server-Sent Events subscriber with ticket authentication and backoff reconnect.
 */

(function (window) {
    'use strict';

    class NexusSSEClient {
        constructor() {
            this._eventSource = null;
            this._sessionId = null;
            this._ticket = null;
            this._handlers = new Map();
            this._reconnectAttempts = 0;
            this._maxReconnectAttempts = 5;
            this._reconnectTimer = null;
            this._isManuallyClosed = false;
        }

        on(eventType, callback) {
            if (!this._handlers.has(eventType)) {
                this._handlers.set(eventType, new Set());
            }
            this._handlers.get(eventType).add(callback);
            return () => this.off(eventType, callback);
        }

        off(eventType, callback) {
            if (this._handlers.has(eventType)) {
                this._handlers.get(eventType).delete(callback);
            }
        }

        _emit(eventType, data) {
            const listeners = this._handlers.get(eventType);
            if (listeners) {
                for (const fn of listeners) {
                    try {
                        fn(data);
                    } catch (err) {
                        console.error(`[NexusSSEClient] Error in handler for '${eventType}':`, err);
                    }
                }
            }
            // Also notify wildcard listeners
            const allListeners = this._handlers.get('*');
            if (allListeners) {
                for (const fn of allListeners) {
                    try {
                        fn(eventType, data);
                    } catch (err) {
                        console.error('[NexusSSEClient] Error in wildcard handler:', err);
                    }
                }
            }
        }

        connect(sessionId, ticket = '') {
            this.disconnect();
            this._isManuallyClosed = false;
            this._sessionId = sessionId;
            this._ticket = ticket;

            let url = `/agentic/session/${encodeURIComponent(sessionId)}/events`;
            if (ticket) {
                url += `?ticket=${encodeURIComponent(ticket)}`;
            }

            try {
                this._eventSource = new EventSource(url);
            } catch (err) {
                this._emit('error', { error: err.message });
                return;
            }

            this._eventSource.onopen = (e) => {
                this._reconnectAttempts = 0;
                this._emit('connected', { sessionId });
            };

            this._eventSource.onmessage = (e) => {
                try {
                    const data = JSON.parse(e.data);
                    const eventType = data.event || 'message';
                    this._emit(eventType, data);
                } catch (parseErr) {
                    this._emit('message', { raw: e.data });
                }
            };

            this._eventSource.onerror = (e) => {
                if (this._isManuallyClosed) return;
                this._emit('disconnected', { error: 'Connection closed or lost' });
                this._eventSource.close();
                this._eventSource = null;

                if (this._reconnectAttempts < this._maxReconnectAttempts) {
                    this._reconnectAttempts++;
                    const delay = Math.min(1000 * Math.pow(2, this._reconnectAttempts), 10000);
                    this._reconnectTimer = setTimeout(() => {
                        this._attemptReconnect();
                    }, delay);
                } else {
                    this._emit('error', { error: 'Max reconnection attempts exceeded' });
                }
            };
        }

        async _attemptReconnect() {
            if (this._isManuallyClosed || !this._sessionId) return;
            try {
                // Request a fresh ticket if available
                if (window.nexusApi) {
                    const ticketResp = await window.nexusApi.getTicket(this._sessionId);
                    if (ticketResp && ticketResp.ticket) {
                        this._ticket = ticketResp.ticket;
                    }
                }
            } catch (err) {
                // Proceed with existing or no ticket
            }
            this.connect(this._sessionId, this._ticket);
        }

        disconnect() {
            this._isManuallyClosed = true;
            if (this._reconnectTimer) {
                clearTimeout(this._reconnectTimer);
                this._reconnectTimer = null;
            }
            if (this._eventSource) {
                this._eventSource.close();
                this._eventSource = null;
            }
        }
    }

    window.NexusSSEClient = NexusSSEClient;
    window.nexusSSE = new NexusSSEClient();
})(window);
