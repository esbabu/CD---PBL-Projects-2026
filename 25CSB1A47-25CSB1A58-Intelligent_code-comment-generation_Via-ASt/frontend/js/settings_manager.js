/**
 * AST Studio · Settings & AI Provider Manager
 * Manages provider configuration, credentials status, connectivity verification, and modal UI.
 */

(function (window) {
    'use strict';

    class SettingsManager {
        constructor() {
            this.currentSettings = {
                provider: 'ast',
                model: '',
                docstring_style: 'google',
                has_api_key: false,
                ai_ready: true,
            };
        }

        getSettings() {
            return this.currentSettings;
        }

        setSettings(s) {
            this.currentSettings = Object.assign(this.currentSettings || {}, s || {});
        }

        async loadSettings(requestJsonFn = window.requestJson) {
            try {
                const req = requestJsonFn || (async (url, opts) => {
                    const res = await fetch(url, opts);
                    return { data: await res.json() };
                });
                const { data } = await req('/api/settings');
                this.currentSettings = data;
                if (data.provider_status) {
                    this.currentSettings.provider_status = data.provider_status;
                }
                this.updateSettingsUI(data);
                return data;
            } catch (e) {
                console.warn('Could not load /api/settings:', e);
                return null;
            }
        }

        updateSettingsUI(settings) {
            if (!settings) return;
            const providerLabel = document.getElementById('active-provider-label');
            if (providerLabel) {
                providerLabel.textContent = settings.provider_display || settings.provider || 'AI Engine Settings';
            }

            const providerSelect = document.getElementById('settings-provider-select');
            if (providerSelect && settings.provider) {
                providerSelect.value = settings.provider;
            }

            const styleSelect = document.getElementById('settings-docstring-style');
            if (styleSelect && settings.docstring_style) {
                styleSelect.value = settings.docstring_style;
            }

            const modelInput = document.getElementById('settings-model-name');
            if (modelInput && settings.model) {
                modelInput.value = settings.model;
            }

            const baseUrlInput = document.getElementById('settings-base-url');
            if (baseUrlInput && typeof settings.base_url === 'string') {
                baseUrlInput.value = settings.base_url;
            }
            this.updateBaseUrlAvailability(
                settings.provider,
                settings.supports_base_url
            );

            const keyStatus = document.getElementById('settings-key-status');
            if (keyStatus) {
                if (['ast', 'ollama'].includes(settings.provider)) {
                    keyStatus.textContent = 'No API key required';
                    keyStatus.className = 'settings-key-status';
                } else if (settings.has_api_key) {
                    keyStatus.textContent = '✓ Key configured';
                    keyStatus.className = 'settings-key-status';
                } else {
                    keyStatus.textContent = 'Key not configured';
                    keyStatus.className = 'settings-key-status missing';
                }
            }

            const connectivityStatus = document.getElementById('provider-connectivity-status');
            if (connectivityStatus) {
                if (settings.provider_status_detail) {
                    connectivityStatus.textContent = settings.provider_status_detail;
                } else if (settings.provider_status === 'connected') {
                    connectivityStatus.textContent = 'The live provider request succeeded.';
                } else if (settings.provider_status === 'configured') {
                    connectivityStatus.textContent = 'CONFIGURED / NOT TESTED';
                } else {
                    connectivityStatus.textContent = settings.provider_status || 'CONFIGURED / NOT TESTED';
                }
            }
        }

        updateBaseUrlAvailability(provider, supported = null) {
            const group = document.getElementById('settings-baseurl-group');
            if (!group) return;
            const canConfigure = supported === null
                ? !['ast', 'huggingface'].includes(provider)
                : Boolean(supported);
            group.style.display = canConfigure ? '' : 'none';
        }

        showSettingsModal() {
            const modal = document.getElementById('settings-modal');
            if (modal) {
                modal.style.display = 'flex';
                this.loadSettings();
            }
        }

        hideSettingsModal() {
            const modal = document.getElementById('settings-modal');
            if (modal) {
                modal.style.display = 'none';
            }
            const testBanner = document.getElementById('settings-test-result');
            if (testBanner) testBanner.style.display = 'none';
        }

        async testProviderConnection(requestJsonFn = window.requestJson, escapeFn = window.escapeHtml, showToastFn = window.showToast) {
            const provider = document.getElementById('settings-provider-select').value;
            const apiKey = document.getElementById('settings-api-key').value.trim();
            const model = document.getElementById('settings-model-name').value.trim();
            const baseUrl = document.getElementById('settings-base-url').value.trim();
            const testBanner = document.getElementById('settings-test-result');
            const spinner = document.getElementById('test-provider-spinner');
            const testBtn = document.getElementById('btn-test-provider');
            const escape = escapeFn || window.escapeHtml || ((s) => String(s));

            if (spinner) spinner.style.display = 'inline-block';
            if (testBtn) testBtn.disabled = true;

            try {
                const req = requestJsonFn || (async (url, opts) => {
                    const res = await fetch(url, opts);
                    return { data: await res.json() };
                });

                const { data } = await req('/api/test-provider', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        provider,
                        api_key: apiKey || undefined,
                        model: model || undefined,
                        base_url: baseUrl || undefined,
                    }),
                });

                testBanner.style.display = 'flex';
                if (data.success) {
                    testBanner.className = 'settings-test-banner success';
                    testBanner.innerHTML = `
                        <strong>✓ Connection Successful (${data.latency_ms} ms)</strong>
                        <span>Provider: ${escape(data.provider || provider)} · Model: ${escape(data.model || model || 'Default')}</span>
                        ${data.sample_response ? `<span>Sample response: <code>${escape(data.sample_response)}</code></span>` : ''}
                    `;
                    if (showToastFn) showToastFn(`Provider ${data.provider} verified (${data.latency_ms} ms)`, 'success');
                } else {
                    testBanner.className = 'settings-test-banner error';
                    testBanner.innerHTML = `
                        <strong>✗ Connection Test Failed</strong>
                        <span>${escape(data.error || 'Could not connect to model provider.')}</span>
                    `;
                    if (showToastFn) showToastFn(`Connection failed: ${data.error || 'Check settings'}`, 'error');
                }
                return data;
            } catch (e) {
                testBanner.style.display = 'flex';
                testBanner.className = 'settings-test-banner error';
                testBanner.innerHTML = `<strong>✗ Request Error:</strong> <span>${escape(e.message)}</span>`;
                throw e;
            } finally {
                if (spinner) spinner.style.display = 'none';
                if (testBtn) testBtn.disabled = false;
            }
        }

        async saveSettings(requestJsonFn = window.requestJson, showToastFn = window.showToast, checkHealthFn = window.checkHealth) {
            const provider = document.getElementById('settings-provider-select').value;
            const apiKey = document.getElementById('settings-api-key').value.trim();
            const model = document.getElementById('settings-model-name').value.trim();
            const baseUrl = document.getElementById('settings-base-url').value.trim();
            const docstringStyle = document.getElementById('settings-docstring-style').value;
            const saveBtn = document.getElementById('btn-save-settings');

            if (saveBtn) saveBtn.disabled = true;

            try {
                const payload = {
                    provider,
                    docstring_style: docstringStyle,
                    base_url: baseUrl,
                };
                if (apiKey) payload.api_key = apiKey;
                if (model) payload.model = model;

                const req = requestJsonFn || (async (url, opts) => {
                    const res = await fetch(url, opts);
                    return { data: await res.json() };
                });

                const { data } = await req('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });

                this.currentSettings = data;
                this.updateSettingsUI(data);
                this.hideSettingsModal();
                if (showToastFn) showToastFn(`Saved settings for ${data.provider_display || provider}`, 'success');
                if (checkHealthFn) checkHealthFn();
                return data;
            } catch (e) {
                if (showToastFn) showToastFn(`Failed to save settings: ${e.message}`, 'error');
                throw e;
            } finally {
                if (saveBtn) saveBtn.disabled = false;
            }
        }
    }

    window.SettingsManager = SettingsManager;
    window.settingsManager = new SettingsManager();
})(typeof window !== 'undefined' ? window : this);
