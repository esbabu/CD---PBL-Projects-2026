import { RunState, RunMode, InferenceMode, ActiveTab, PipelineStageState, OptimizationResult, SecurityResult, RunMessage } from './runTypes';
import { DEFAULT_SOURCE_CODE, STARTER_CODE_BY_LANGUAGE } from '../../app/appConfig';

export type RunAction =
  | { type: 'SET_MODE'; payload: RunMode }
  | { type: 'SET_INFERENCE_MODE'; payload: InferenceMode }
  | { type: 'SET_LANGUAGE'; payload: string }
  | { type: 'SET_SOURCE_CODE'; payload: string }
  | { type: 'SET_ACTIVE_TAB'; payload: ActiveTab }
  | { type: 'START_RUN'; payload: { runId: string } }
  | { type: 'UPDATE_STAGE'; payload: { stageId: string; status: PipelineStageState['status']; message?: string } }
  | { type: 'SET_OPTIMIZATION_RESULT'; payload: OptimizationResult }
  | { type: 'SET_SECURITY_RESULT'; payload: SecurityResult }
  | { type: 'SET_OUTPUT_LOG'; payload: string }
  | { type: 'ADD_MESSAGE'; payload: Omit<RunMessage, 'id'> }
  | { type: 'FINISH_RUN'; payload: { status: RunState['status'] } }
  | { type: 'CANCEL_RUN' }
  | { type: 'APPLY_OPTIMIZED_TO_SOURCE' };

export function getInitialStages(mode: RunMode): PipelineStageState[] {
  const sourceStage: PipelineStageState = { id: 'source', label: 'Source Code', status: 'completed' };
  const optStage: PipelineStageState = { id: 'optimization', label: 'Optimization Agent', agent: 'Optimization', status: 'pending' };
  const secStage: PipelineStageState = { id: 'security', label: 'Security Agent', agent: 'Security', status: 'pending' };
  const completedStage: PipelineStageState = { id: 'completed', label: 'Completed', status: 'pending' };

  if (mode === 'optimize') {
    return [sourceStage, optStage, completedStage];
  } else if (mode === 'security') {
    return [sourceStage, secStage, completedStage];
  } else {
    return [sourceStage, optStage, secStage, completedStage];
  }
}

export const initialRunState: RunState = {
  currentRunId: null,
  mode: 'pipeline',
  inferenceMode: 'llm',
  language: 'cpp',
  sourceCode: DEFAULT_SOURCE_CODE,
  status: 'idle',
  activeTab: 'output',
  stages: getInitialStages('pipeline'),
  optimizationResult: null,
  securityResult: null,
  outputLog: null,
  messages: [],
  isStale: false,
};

export function runReducer(state: RunState, action: RunAction): RunState {
  switch (action.type) {
    case 'SET_MODE': {
      if (state.mode === action.payload) return state;
      return {
        ...state,
        mode: action.payload,
        stages: getInitialStages(action.payload),
      };
    }

    case 'SET_INFERENCE_MODE':
      return { ...state, inferenceMode: action.payload };

    case 'SET_LANGUAGE': {
      const nextLang = action.payload;
      const isUnmodifiedStarter =
        !state.sourceCode.trim() ||
        Object.values(STARTER_CODE_BY_LANGUAGE).some((tpl) => tpl.trim() === state.sourceCode.trim());
      return {
        ...state,
        language: nextLang,
        sourceCode:
          isUnmodifiedStarter && STARTER_CODE_BY_LANGUAGE[nextLang]
            ? STARTER_CODE_BY_LANGUAGE[nextLang]
            : state.sourceCode,
      };
    }

    case 'SET_SOURCE_CODE':
      return { ...state, sourceCode: action.payload, isStale: state.currentRunId !== null };

    case 'SET_ACTIVE_TAB':
      return { ...state, activeTab: action.payload };

    case 'START_RUN':
      return {
        ...state,
        currentRunId: action.payload.runId,
        status: 'running',
        isStale: false,
        stages: getInitialStages(state.mode).map((s, idx) =>
          idx === 0 ? { ...s, status: 'completed' } : { ...s, status: 'pending' }
        ),
        optimizationResult: null,
        securityResult: null,
        outputLog: null,
        messages: [
          {
            id: `msg-${Date.now()}-init`,
            timestamp: new Date().toISOString(),
            category: 'lifecycle',
            message: `Run started (${action.payload.runId}) in '${state.mode}' mode with inference='${state.inferenceMode}'.`,
          },
        ],
      };

    case 'UPDATE_STAGE':
      return {
        ...state,
        stages: state.stages.map((stage) =>
          stage.id === action.payload.stageId
            ? { ...stage, status: action.payload.status, message: action.payload.message ?? stage.message }
            : stage
        ),
      };

    case 'SET_OPTIMIZATION_RESULT':
      return {
        ...state,
        optimizationResult: action.payload,
      };

    case 'SET_SECURITY_RESULT':
      return {
        ...state,
        securityResult: action.payload,
      };

    case 'SET_OUTPUT_LOG':
      return {
        ...state,
        outputLog: action.payload,
      };

    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            ...action.payload,
            id: `msg-${Date.now()}-${state.messages.length}`,
          },
        ],
      };

    case 'FINISH_RUN':
      return {
        ...state,
        status: action.payload.status,
        stages: state.stages.map((stage) => {
          if (stage.id === 'completed') {
            return {
              ...stage,
              status:
                action.payload.status === 'completed'
                  ? 'completed'
                  : action.payload.status === 'partially_completed'
                  ? 'degraded'
                  : 'failed',
            };
          }
          if (stage.status === 'pending' && action.payload.status !== 'completed') {
            return { ...stage, status: 'skipped' };
          }
          return stage;
        }),
      };

    case 'CANCEL_RUN':
      return {
        ...state,
        status: 'cancelled',
        stages: state.stages.map((stage) =>
          stage.status === 'running' ? { ...stage, status: 'cancelled' } : stage
        ),
        messages: [
          ...state.messages,
          {
            id: `msg-${Date.now()}-cancel`,
            timestamp: new Date().toISOString(),
            category: 'warning',
            message: 'Run cancelled by user.',
          },
        ],
      };

    case 'APPLY_OPTIMIZED_TO_SOURCE':
      if (state.optimizationResult?.optimized_code) {
        return {
          ...state,
          sourceCode: state.optimizationResult.optimized_code,
          activeTab: 'output',
          messages: [
            ...state.messages,
            {
              id: `msg-${Date.now()}-apply`,
              timestamp: new Date().toISOString(),
              category: 'info',
              message: 'Optimized code applied to Source Code editor.',
            },
          ],
        };
      }
      return state;

    default:
      return state;
  }
}
