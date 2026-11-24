import { describe, it } from 'node:test';
import assert from 'node:assert';
import { runReducer, initialRunState, getInitialStages } from '../features/run/runReducer.js';

describe('runReducer', () => {
  it('correctly sets mode and switches stage topology', () => {
    // 1. Full Pipeline mode has 4 stages: Source -> Optimization -> Security -> Completed
    const pipelineStages = getInitialStages('pipeline');
    assert.strictEqual(pipelineStages.length, 4);
    assert.deepStrictEqual(pipelineStages.map(s => s.id), ['source', 'optimization', 'security', 'completed']);

    // 2. Optimize mode has 3 stages: Source -> Optimization -> Completed
    const optState = runReducer(initialRunState, { type: 'SET_MODE', payload: 'optimize' });
    assert.strictEqual(optState.mode, 'optimize');
    assert.strictEqual(optState.stages.length, 3);
    assert.deepStrictEqual(optState.stages.map(s => s.id), ['source', 'optimization', 'completed']);

    // 3. Security mode has 3 stages: Source -> Security -> Completed
    const secState = runReducer(initialRunState, { type: 'SET_MODE', payload: 'security' });
    assert.strictEqual(secState.mode, 'security');
    assert.strictEqual(secState.stages.length, 3);
    assert.deepStrictEqual(secState.stages.map(s => s.id), ['source', 'security', 'completed']);
  });

  it('resets results and marks active on START_RUN', () => {
    let state = runReducer(initialRunState, {
      type: 'SET_OPTIMIZATION_RESULT',
      payload: {
        run_id: 'old-run',
        status: 'completed',
        optimized_code: '// old code',
        transformations: [],
        metrics: {},
        raw_result: {},
        diagnostics: [],
        duration_ms: 10,
        is_demo: true,
      },
    });
    assert.ok(state.optimizationResult !== null);

    // Starting new run cleans stale results
    state = runReducer(state, { type: 'START_RUN', payload: { runId: 'run-new-123' } });
    assert.strictEqual(state.currentRunId, 'run-new-123');
    assert.strictEqual(state.status, 'running');
    assert.strictEqual(state.optimizationResult, null);
    assert.strictEqual(state.securityResult, null);
    assert.strictEqual(state.isStale, false);
  });

  it('applies optimized code to source code', () => {
    let state = runReducer(initialRunState, {
      type: 'SET_OPTIMIZATION_RESULT',
      payload: {
        run_id: 'run-apply-test',
        status: 'completed',
        optimized_code: '// transformed new source code',
        transformations: ['unroll'],
        metrics: {},
        raw_result: {},
        diagnostics: [],
        duration_ms: 20,
        is_demo: true,
      },
    });

    state = runReducer(state, { type: 'APPLY_OPTIMIZED_TO_SOURCE' });
    assert.strictEqual(state.sourceCode, '// transformed new source code');
  });

  it('cancels active run correctly', () => {
    let state = runReducer(initialRunState, { type: 'START_RUN', payload: { runId: 'run-cancel' } });
    state = runReducer(state, { type: 'CANCEL_RUN' });
    assert.strictEqual(state.status, 'cancelled');
    assert.ok(state.messages.some(m => m.message.includes('cancelled')));
  });
});
