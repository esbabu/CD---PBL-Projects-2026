import { describe, it } from 'node:test';
import assert from 'node:assert';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { SUPPORTED_LANGUAGES, STARTER_CODE_BY_LANGUAGE } from '../app/appConfig.js';
import { runReducer, initialRunState } from '../features/run/runReducer.js';
import { handleBackendEvent, formatRunSummary } from '../features/run/useRunController.js';
import { AppHeader } from '../components/header/AppHeader.js';
import { LivePipelinePanel } from '../components/workspace/LivePipelinePanel.js';
import { OutputTab } from '../components/results/OutputTab.js';
import { ResultsTabs } from '../components/results/ResultsTabs.js';
import { OptimizedCodeTab } from '../components/results/OptimizedCodeTab.js';
import { SecurityTab } from '../components/results/SecurityTab.js';
import { MessagesTab } from '../components/results/MessagesTab.js';

describe('Frontend E2E UI & State Integration Audit', () => {
  it('includes C++, Python, JavaScript, and C in language selector (excluding Rust)', () => {
    const ids = SUPPORTED_LANGUAGES.map((l) => l.id);
    assert.ok(ids.includes('cpp'));
    assert.ok(ids.includes('c'));
    assert.ok(ids.includes('python'));
    assert.ok(ids.includes('javascript'));
    assert.ok(!ids.includes('rust'), 'Rust should not be an option in the language selector');
    assert.ok(STARTER_CODE_BY_LANGUAGE.javascript.includes('twoSum'));
  });

  it('renders honest LLM Online vs LLM Offline badges in AppHeader', () => {
    const offlineHtml = renderToStaticMarkup(
      React.createElement(AppHeader, {
        mode: 'pipeline',
        onModeChange: () => {},
        inferenceMode: 'llm',
        onInferenceModeChange: () => {},
        status: 'idle',
        onRunClick: () => {},
        onStopClick: () => {},
        backendConnected: true,
        health: {
          status: 'healthy',
          service: 'CompilerAI',
          version: '0.2.0',
          demo_mode: false,
          adapters: { optimization: 'real', security: 'real' },
          llm_connection: 'unreachable',
          ollama: { reachable: false, base_url: 'http://localhost:11434', models: [], remediation: 'Start Ollama' },
          supported_modes: ['pipeline', 'optimize', 'security'],
          supported_languages: ['cpp', 'c', 'python', 'javascript'],
        },
        isDark: false,
        onToggleTheme: () => {},
      })
    );
    assert.ok(offlineHtml.includes('LLM Offline'));
    assert.ok(offlineHtml.includes('Real Agents Ready'));

    const onlineHtml = renderToStaticMarkup(
      React.createElement(AppHeader, {
        mode: 'pipeline',
        onModeChange: () => {},
        inferenceMode: 'llm',
        onInferenceModeChange: () => {},
        status: 'idle',
        onRunClick: () => {},
        onStopClick: () => {},
        backendConnected: true,
        health: {
          status: 'healthy',
          service: 'CompilerAI',
          version: '0.2.0',
          demo_mode: false,
          adapters: { optimization: 'real', security: 'real' },
          llm_connection: 'connected',
          ollama: {
            reachable: true,
            base_url: 'http://localhost:11434',
            models: ['qwen2.5-coder:7b'],
            active_model: 'qwen2.5-coder:7b',
          },
          supported_modes: ['pipeline', 'optimize', 'security'],
          supported_languages: ['cpp', 'c', 'python', 'javascript'],
        },
        isDark: false,
        onToggleTheme: () => {},
      })
    );
    assert.ok(onlineHtml.includes('LLM Online (qwen2.5-coder:7b)'));
  });

  it('handles degraded C++ Analysis-Only SSE stream and renders honest UI without Apply to Source', () => {
    let state = runReducer(initialRunState, { type: 'START_RUN', payload: { runId: 'run-cpp-1' } });
    const dispatch = (action: any) => {
      state = runReducer(state, action);
    };

    const events = [
      { run_id: 'run-cpp-1', seq: 1, type: 'run_started', status: 'running', timestamp: new Date().toISOString(), message: "Run started in 'pipeline' mode (cpp)", data: {} },
      { run_id: 'run-cpp-1', seq: 2, type: 'agent_started', agent: 'optimization', stage: 'optimization', status: 'running', timestamp: new Date().toISOString(), message: 'OptAgent initialized', data: {} },
      { run_id: 'run-cpp-1', seq: 3, type: 'warning', agent: 'optimization', stage: 'optimization', status: 'running', timestamp: new Date().toISOString(), message: '[TOOLCHAIN_MISSING] Native compiler unavailable', data: {} },
      { run_id: 'run-cpp-1', seq: 4, type: 'agent_completed', agent: 'optimization', stage: 'optimization', status: 'degraded', timestamp: new Date().toISOString(), message: 'Optimization Agent returned static analysis only (unverified, Tier T0)', data: { unverified: true } },
      { run_id: 'run-cpp-1', seq: 5, type: 'pipeline_stage_changed', stage: 'security', status: 'running', timestamp: new Date().toISOString(), message: 'Proceeding to Security on original source', data: { optimization_degraded: true } },
      { run_id: 'run-cpp-1', seq: 6, type: 'agent_completed', agent: 'security', stage: 'security', status: 'completed', timestamp: new Date().toISOString(), message: 'Security completed (2 findings)', data: {} },
      { run_id: 'run-cpp-1', seq: 7, type: 'run_partially_completed', status: 'partially_completed', timestamp: new Date().toISOString(), message: 'Full Pipeline partially completed', data: { unverified: true } },
    ];

    for (const ev of events) {
      handleBackendEvent(ev, dispatch, 'run-cpp-1');
    }

    assert.strictEqual(state.status, 'partially_completed');
    assert.strictEqual(state.stages.find((s) => s.id === 'optimization')?.status, 'degraded');
    assert.strictEqual(state.stages.find((s) => s.id === 'security')?.status, 'completed');
    assert.strictEqual(state.stages.find((s) => s.id === 'completed')?.status, 'degraded');
    assert.ok(state.messages.some((m) => m.message.includes('TOOLCHAIN_MISSING')));
    assert.ok(state.messages.some((m) => m.message.includes('static analysis only')));

    const mockResults: any = {
      run_id: 'run-cpp-1',
      mode: 'pipeline',
      status: 'partially_completed',
      failure_reason: 'Optimization degraded (Analysis-Only, unverified)',
      optimization_result: {
        run_id: 'run-cpp-1',
        status: 'completed',
        optimized_code: 'void f() {}',
        transformations: ['Static analysis only (unverified — no executable verification performed)'],
        metrics: { support_level: 'analysis_only', evidence_tier: 'T0', unverified: true, overall_speedup: '1.00x' },
        raw_result: { outcome: { stages: [{ name: 'triage', status: 'ok', seconds: 0.02 }, { name: 'oracle', status: 'skipped', seconds: 0 }], provenance: { counts: { heuristic: 2, tool: 0, llm: 0 }, llm_calls: 0, cache_hits: 0 } } },
        diagnostics: ['[TOOLCHAIN_MISSING] Native compiler unavailable'],
        duration_ms: 45,
        is_demo: false,
      },
      security_result: {
        run_id: 'run-cpp-1',
        status: 'completed',
        source_kind: 'original',
        findings: [{ id: 'SEC-1', title: 'Unsafe Gets', severity: 'high', description: 'gets() unsafe', line_number: 6, rule_or_cwe: 'CWE-242' }],
        raw_result: { overall_risk: 'critical' },
        diagnostics: [],
        duration_ms: 20,
        is_demo: false,
      },
    };

    const summary = formatRunSummary(mockResults);
    assert.ok(!summary.includes('No native binary execution runtime is attached'));
    assert.ok(summary.includes('UNVERIFIED'));
    assert.ok(summary.includes('TOOLCHAIN_MISSING'));
    assert.ok(summary.includes('triage: ok'));

    const pipeHtml = renderToStaticMarkup(React.createElement(LivePipelinePanel, { stages: state.stages, runStatus: state.status, currentRunId: state.currentRunId }));
    assert.ok(pipeHtml.includes('degraded'));
    assert.ok(pipeHtml.includes('partially completed'));

    const tabsHtml = renderToStaticMarkup(
      React.createElement(ResultsTabs, { activeTab: 'optimized_code', onTabChange: () => {}, hasOptimizedCode: true, isUnverified: true, securityFindingsCount: 1, messagesCount: state.messages.length })
    );
    assert.ok(tabsHtml.includes('Analysis Only'));
    assert.ok(!tabsHtml.includes('>Ready<'));

    const optHtml = renderToStaticMarkup(
      React.createElement(OptimizedCodeTab, { optimizationResult: mockResults.optimization_result, language: 'cpp', onApplyToSource: () => {} })
    );
    assert.ok(optHtml.includes('STATIC ANALYSIS (UNVERIFIED)'));
    assert.ok(optHtml.includes('ANALYSIS ONLY'));
    assert.ok(!optHtml.includes('Apply to Source'));
    assert.ok(optHtml.includes('Diagnostics &amp; Remediation'));
    assert.ok(optHtml.includes('TOOLCHAIN_MISSING'));

    const secHtml = renderToStaticMarkup(React.createElement(SecurityTab, { securityResult: mockResults.security_result }));
    assert.ok(secHtml.includes('Target: original Code'));
    assert.ok(secHtml.includes('CWE-242'));

    const msgHtml = renderToStaticMarkup(React.createElement(MessagesTab, { messages: state.messages }));
    assert.ok(msgHtml.includes('TOOLCHAIN_MISSING'));

    const idleOutHtml = renderToStaticMarkup(React.createElement(OutputTab, { outputLog: null, runStatus: 'idle' }));
    assert.ok(!idleOutHtml.includes('In this milestone, no target binary runtime is connected'));
  });

  it('renders verified Python optimization with Apply to Source, Ready badge, and complexity', () => {
    const verifiedResult: any = {
      run_id: 'run-py-1',
      status: 'completed',
      optimized_code: 'def two_sum(nums, target):\n    seen = {}\n    return []',
      transformations: ['Nested loop replaced with hash map'],
      metrics: { support_level: 'full', evidence_tier: 'T1', unverified: false, overall_speedup: '1.74x', complexity_before: 'O(n^2)', complexity_after: 'O(n log n)' },
      raw_result: { outcome: { stages: [{ name: 'triage', status: 'ok' }, { name: 'search', status: 'ok' }] } },
      diagnostics: [],
      duration_ms: 9900,
      is_demo: false,
    };
    const optHtml = renderToStaticMarkup(
      React.createElement(OptimizedCodeTab, { optimizationResult: verifiedResult, language: 'python', onApplyToSource: () => {} })
    );
    assert.ok(optHtml.includes('OPTIMIZED OUTPUT'));
    assert.ok(optHtml.includes('FULL · T1'));
    assert.ok(optHtml.includes('Apply to Source'));
    assert.ok(optHtml.includes('1.74x'));
  });

  it('guarantees no duplicate cards for the same line in SecurityTab', () => {
    const mockSecWithDuplicates: any = {
      run_id: 'sec-dup-test',
      status: 'completed',
      source_kind: 'original',
      findings: [
        {
          id: 'f1',
          title: 'Unsafe Gets',
          severity: 'high',
          description: 'gets() is unsafe',
          line_number: 6,
          rule_or_cwe: 'CWE-242',
          remediation: 'Use fgets()',
        },
        {
          id: 'f2',
          title: 'Deprecated Function',
          severity: 'medium',
          description: 'Obsolete function gets called',
          line_number: 6,
          rule_or_cwe: 'CWE-477',
          remediation: 'Use fgets()',
        },
        {
          id: 'f3',
          title: 'Format String Bug',
          severity: 'critical',
          description: 'printf non-constant format',
          line_number: 7,
          rule_or_cwe: 'CWE-134',
          remediation: 'Use %s',
        },
      ],
      raw_result: {},
      diagnostics: [],
      duration_ms: 50,
      is_demo: false,
    };

    const secHtml = renderToStaticMarkup(
      React.createElement(SecurityTab, { securityResult: mockSecWithDuplicates })
    );

    // There were 2 findings on line 6, but in the UI there should only be 1 button for Line 6
    const line6Matches = secHtml.match(/Line 6/g);
    assert.strictEqual(line6Matches?.length, 1, 'There should be exactly one card/button for Line 6');

    // Line 7 has 1 card
    const line7Matches = secHtml.match(/Line 7/g);
    assert.strictEqual(line7Matches?.length, 1, 'There should be exactly one card/button for Line 7');

    // Both CWEs from Line 6 should be merged
    assert.ok(secHtml.includes('CWE-242, CWE-477'));
  });
});
