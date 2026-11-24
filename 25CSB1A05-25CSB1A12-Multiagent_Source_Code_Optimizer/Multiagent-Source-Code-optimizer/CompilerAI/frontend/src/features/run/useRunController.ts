import { useRef, useCallback, useEffect } from 'react';
import { RunAction } from './runReducer';
import { RunState } from './runTypes';
import { runApi, RunResultsResponse } from '../../services/runApi';
import { RunEventStream, BackendRunEvent } from '../../services/eventStream';
import { sanitizeVendor } from '../../utils/sanitizeVendor';

export function formatRunSummary(results: RunResultsResponse): string {
  const lines: string[] = [
    `Run ID   : ${results.run_id}`,
    `Mode     : ${results.mode}`,
    `Status   : ${results.status}`,
  ];
  if (results.failure_reason) {
    lines.push(`Reason   : ${results.failure_reason}`);
  }
  if (results.optimization_result) {
    const opt = results.optimization_result;
    const m = opt.metrics || {};
    const speedup = m.overall_speedup || m.estimated_speedup || 'N/A';
    const tier = m.evidence_tier || 'N/A';
    const support = m.support_level || (m.unverified ? 'analysis_only' : 'full');
    lines.push(
      `Optimize : ${opt.status} (${opt.duration_ms}ms, support: ${support}, tier: ${tier}, speedup: ${speedup}${m.unverified ? ', UNVERIFIED' : ''}${opt.is_demo ? ', DEMO' : ''})`
    );
    if (m.complexity_before || m.complexity_after) {
      lines.push(`Complexity: ${m.complexity_before || '?'} -> ${m.complexity_after || '?'}`);
    }
    const outcome = opt.raw_result?.outcome;
    if (outcome?.stages && Array.isArray(outcome.stages) && outcome.stages.length > 0) {
      lines.push('');
      lines.push('Optimization Stages:');
      for (const st of outcome.stages) {
        const secs = typeof st.seconds === 'number' ? `${st.seconds.toFixed(2)}s` : '';
        lines.push(`  - ${st.name}: ${st.status}${secs ? ` (${secs})` : ''}`);
      }
    }
    if (outcome?.provenance) {
      const p = outcome.provenance;
      lines.push(
        `Provenance: heuristic=${p.counts?.heuristic ?? 0}, tool=${p.counts?.tool ?? 0}, llm=${p.counts?.llm ?? 0}, llm_calls=${p.llm_calls ?? 0}, cache_hits=${p.cache_hits ?? 0}`
      );
    }
    if (opt.diagnostics && opt.diagnostics.length > 0) {
      lines.push('');
      lines.push('Optimization Diagnostics:');
      for (const d of opt.diagnostics) {
        lines.push(`  * ${d}`);
      }
    }
  }
  if (results.security_result) {
    const sec = results.security_result;
    const risk = sec.raw_result?.overall_risk ? `, risk: ${String(sec.raw_result.overall_risk).toUpperCase()}` : '';
    lines.push('');
    lines.push(
      `Security : ${sec.status} (${sec.duration_ms}ms, target: ${sec.source_kind}, findings: ${sec.findings?.length ?? 0}${risk}${sec.is_demo ? ', DEMO' : ''})`
    );
  }
  return sanitizeVendor(lines.join('\n'));
}

export function useRunController(state: RunState, dispatch: React.Dispatch<RunAction>) {
  const activeStreamRef = useRef<RunEventStream | null>(null);
  const latestRunIdRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      activeStreamRef.current?.close();
    };
  }, []);

  const fetchAndApplyResults = useCallback(
    async (runId: string) => {
      if (latestRunIdRef.current !== runId) return null;
      const results = await runApi.getRunResults(runId);
      if (latestRunIdRef.current !== runId) return null;

      if (results.optimization_result) {
        dispatch({
          type: 'SET_OPTIMIZATION_RESULT',
          payload: results.optimization_result,
        });
      }
      if (results.security_result) {
        dispatch({
          type: 'SET_SECURITY_RESULT',
          payload: results.security_result,
        });
      }
      dispatch({
        type: 'SET_OUTPUT_LOG',
        payload: formatRunSummary(results),
      });
      return results;
    },
    [dispatch]
  );

  const startRun = useCallback(async () => {
    if (!state.sourceCode.trim()) {
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: new Date().toISOString(),
          category: 'error',
          message: 'Execution rejected: Source code cannot be empty.',
        },
      });
      return;
    }

    // Close any prior stream cleanly
    activeStreamRef.current?.close();

    try {
      const res = await runApi.startRun({
        mode: state.mode,
        language: state.language,
        source_code: state.sourceCode,
        inference_mode: state.inferenceMode,
      });

      const runId = res.run_id;
      latestRunIdRef.current = runId;
      dispatch({ type: 'START_RUN', payload: { runId } });

      const stream = new RunEventStream(
        runId,
        (event: BackendRunEvent) => {
          if (latestRunIdRef.current !== runId) return;
          handleBackendEvent(event, dispatch, runId);
        },
        async () => {
          if (latestRunIdRef.current !== runId) return;
          // Attempt one status/result recovery so Run button never stays stuck
          try {
            const results = await fetchAndApplyResults(runId);
            if (results && ['completed', 'partially_completed', 'failed', 'cancelled'].includes(results.status)) {
              dispatch({
                type: 'FINISH_RUN',
                payload: { status: results.status as RunState['status'] },
              });
              return;
            }
          } catch {
            // Backend unreachable
          }
          dispatch({
            type: 'ADD_MESSAGE',
            payload: {
              timestamp: new Date().toISOString(),
              category: 'error',
              message: 'Live event stream disconnected or interrupted before run completed.',
            },
          });
          dispatch({ type: 'FINISH_RUN', payload: { status: 'failed' } });
        },
        async () => {
          try {
            await fetchAndApplyResults(runId);
          } catch (err) {
            console.error('Failed to fetch final run results:', err);
          }
        }
      );

      activeStreamRef.current = stream;
      stream.connect();
    } catch (err: any) {
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: new Date().toISOString(),
          category: 'error',
          message: `Failed to initiate run: ${err.message || 'Network error'}`,
        },
      });
      dispatch({ type: 'FINISH_RUN', payload: { status: 'failed' } });
    }
  }, [state.mode, state.language, state.sourceCode, state.inferenceMode, dispatch, fetchAndApplyResults]);

  const stopRun = useCallback(async () => {
    const runId = state.currentRunId;
    if (!runId) return;

    // Invalidate run ref so late events cannot overwrite cancelled state
    latestRunIdRef.current = null;
    try {
      activeStreamRef.current?.close();
      await runApi.cancelRun(runId);
    } catch (err) {
      console.warn('Error during run cancellation:', err);
    } finally {
      dispatch({ type: 'CANCEL_RUN' });
    }
  }, [state.currentRunId, dispatch]);

  return {
    startRun,
    stopRun,
  };
}

export function handleBackendEvent(
  rawEvent: BackendRunEvent,
  dispatch: React.Dispatch<RunAction>,
  currentRunId: string
) {
  if (rawEvent.run_id !== currentRunId) return;
  const event: BackendRunEvent = {
    ...rawEvent,
    message: sanitizeVendor(rawEvent.message),
  };

  switch (event.type) {
    case 'run_started':
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'lifecycle',
          message: event.message,
        },
      });
      break;

    case 'agent_started':
      if (event.agent === 'optimization' || event.stage === 'optimization') {
        dispatch({
          type: 'UPDATE_STAGE',
          payload: { stageId: 'optimization', status: 'running', message: event.message },
        });
      } else if (event.agent === 'security' || event.stage === 'security') {
        dispatch({
          type: 'UPDATE_STAGE',
          payload: { stageId: 'security', status: 'running', message: event.message },
        });
      }
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'info',
          message: `[${event.agent?.toUpperCase() || 'AGENT'}] ${event.message}`,
        },
      });
      break;

    case 'agent_progress':
      dispatch({
        type: 'UPDATE_STAGE',
        payload: {
          stageId: event.stage || (event.agent === 'security' ? 'security' : 'optimization'),
          status: 'running',
          message: event.message,
        },
      });
      break;

    case 'agent_log':
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'info',
          message: event.message,
        },
      });
      break;

    case 'agent_artifact':
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'info',
          message: `Artifact generated: ${event.message}`,
        },
      });
      break;

    case 'agent_completed': {
      const isDegraded = event.status === 'degraded' || Boolean(event.data?.unverified);
      const nextStageStatus = isDegraded ? 'degraded' : 'completed';
      if (event.agent === 'optimization' || event.stage === 'optimization') {
        dispatch({
          type: 'UPDATE_STAGE',
          payload: { stageId: 'optimization', status: nextStageStatus, message: event.message },
        });
      } else if (event.agent === 'security' || event.stage === 'security') {
        dispatch({
          type: 'UPDATE_STAGE',
          payload: { stageId: 'security', status: nextStageStatus, message: event.message },
        });
      }
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: isDegraded ? 'warning' : 'info',
          message: `[${event.agent?.toUpperCase() || 'AGENT'}] ${event.message}`,
        },
      });
      break;
    }

    case 'agent_failed':
      if (event.agent === 'optimization' || event.stage === 'optimization') {
        dispatch({
          type: 'UPDATE_STAGE',
          payload: { stageId: 'optimization', status: 'failed', message: event.message },
        });
      } else if (event.agent === 'security' || event.stage === 'security') {
        dispatch({
          type: 'UPDATE_STAGE',
          payload: { stageId: 'security', status: 'failed', message: event.message },
        });
      }
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'error',
          message: event.message,
        },
      });
      break;

    case 'pipeline_stage_changed':
      if (event.stage === 'security') {
        if (!event.data?.optimization_degraded) {
          dispatch({
            type: 'UPDATE_STAGE',
            payload: { stageId: 'optimization', status: 'completed' },
          });
        }
        dispatch({
          type: 'UPDATE_STAGE',
          payload: { stageId: 'security', status: 'running', message: event.message },
        });
      }
      break;

    case 'warning':
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'warning',
          message: event.message,
        },
      });
      break;

    case 'error':
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'error',
          message: event.message,
        },
      });
      break;

    case 'run_completed':
      dispatch({
        type: 'FINISH_RUN',
        payload: { status: event.status === 'completed' ? 'completed' : 'failed' },
      });
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'lifecycle',
          message: event.message,
        },
      });
      break;

    case 'run_partially_completed':
      dispatch({
        type: 'FINISH_RUN',
        payload: { status: 'partially_completed' },
      });
      dispatch({
        type: 'ADD_MESSAGE',
        payload: {
          timestamp: event.timestamp,
          category: 'warning',
          message: event.message,
        },
      });
      break;

    case 'run_cancelled':
      dispatch({ type: 'CANCEL_RUN' });
      break;
  }
}
