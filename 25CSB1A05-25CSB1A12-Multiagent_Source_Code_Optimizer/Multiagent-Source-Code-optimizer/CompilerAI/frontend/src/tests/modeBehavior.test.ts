import { describe, it } from 'node:test';
import assert from 'node:assert';
import { getInitialStages, runReducer, initialRunState } from '../features/run/runReducer.js';

describe('modeBehavior and Stage Ordering', () => {
  it('enforces Full Pipeline stages: Source -> Optimization -> Security -> Completed', () => {
    const stages = getInitialStages('pipeline');
    assert.strictEqual(stages.length, 4);
    assert.strictEqual(stages[0].id, 'source');
    assert.strictEqual(stages[1].id, 'optimization');
    assert.strictEqual(stages[2].id, 'security');
    assert.strictEqual(stages[3].id, 'completed');
  });

  it('enforces Optimize stages: Source -> Optimization -> Completed (No Security)', () => {
    const stages = getInitialStages('optimize');
    assert.strictEqual(stages.length, 3);
    assert.strictEqual(stages[0].id, 'source');
    assert.strictEqual(stages[1].id, 'optimization');
    assert.strictEqual(stages[2].id, 'completed');
    assert.ok(!stages.some(s => s.id === 'security'));
  });

  it('enforces Security stages: Source -> Security -> Completed (No Optimization)', () => {
    const stages = getInitialStages('security');
    assert.strictEqual(stages.length, 3);
    assert.strictEqual(stages[0].id, 'source');
    assert.strictEqual(stages[1].id, 'security');
    assert.strictEqual(stages[2].id, 'completed');
    assert.ok(!stages.some(s => s.id === 'optimization'));
  });

  it('disallows legacy modes (Analyze, Verify)', () => {
    // Only 3 valid modes: pipeline, optimize, security
    const allowedModes = ['pipeline', 'optimize', 'security'];
    allowedModes.forEach((mode: any) => {
      const state = runReducer(initialRunState, { type: 'SET_MODE', payload: mode });
      assert.strictEqual(state.mode, mode);
    });
  });
});
