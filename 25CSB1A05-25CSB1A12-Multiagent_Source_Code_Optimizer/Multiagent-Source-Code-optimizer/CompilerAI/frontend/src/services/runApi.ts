import { apiRequest } from './apiClient';
import { RunMode, InferenceMode } from '../features/run/runTypes';

export interface CreateRunPayload {
  mode: RunMode;
  language: string;
  source_code: string;
  inference_mode: InferenceMode;
  options?: Record<string, any>;
}

export interface RunStartResponse {
  run_id: string;
  status: string;
  mode: RunMode;
  created_at: string;
  message: string;
}

export interface RunResultsResponse {
  run_id: string;
  status: string;
  mode: RunMode;
  optimization_result: any;
  security_result: any;
  failure_reason?: string;
  created_at: string;
  completed_at?: string;
}

export const runApi = {
  async startRun(payload: CreateRunPayload): Promise<RunStartResponse> {
    return apiRequest<RunStartResponse>('/api/runs', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getRunResults(runId: string): Promise<RunResultsResponse> {
    return apiRequest<RunResultsResponse>(`/api/runs/${runId}/results`);
  },

  async cancelRun(runId: string): Promise<{ run_id: string; status: string; message: string }> {
    return apiRequest<{ run_id: string; status: string; message: string }>(`/api/runs/${runId}/cancel`, {
      method: 'POST',
    });
  },

  async checkHealth(): Promise<any> {
    return apiRequest<any>('/api/health');
  },
};
