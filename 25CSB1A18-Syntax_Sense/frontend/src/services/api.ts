import type {
  AnalyzeRequest,
  AnalyzeResponse,
  ApiErrorResponse,
  SupportedLanguage,
} from '../types';

/**
 * Custom error class capturing structured information returned by the API or network.
 */
export class AnalysisApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details?: unknown[];

  constructor(
    message: string,
    code: string = 'unknown_error',
    status: number = 0,
    details?: unknown[],
  ) {
    super(message);
    this.name = 'AnalysisApiError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

/**
 * Sends source code to the SyntaxSense API for syntax analysis and diagnostics.
 *
 * @param code - The source code to analyze.
 * @param language - Target programming language ('cpp', 'python', 'java').
 * @returns Parsed AnalyzeResponse on success.
 * @throws AnalysisApiError on network failure, validation errors, or server issues.
 */
export async function analyzeCode(
  code: string,
  language: SupportedLanguage = 'cpp',
): Promise<AnalyzeResponse> {
  const trimmed = code.trim();
  const langLabel = language === 'cpp' ? 'C++' : language.toUpperCase();
  if (!trimmed) {
    throw new AnalysisApiError(
      `${langLabel} source code cannot be empty.`,
      'invalid_source',
      400,
    );
  }

  const payload: AnalyzeRequest = {
    language,
    code,
  };

  let response: Response;
  try {
    response = await fetch('/api/v1/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  } catch (err: unknown) {
    const detail = err instanceof Error ? err.message : 'Connection failed';
    throw new AnalysisApiError(
      `Unable to reach the backend analysis service: ${detail}. Please ensure FastAPI is running on port 8000.`,
      'network_error',
      0,
    );
  }

  const rawText = await response.text();
  let json: unknown;
  try {
    json = JSON.parse(rawText);
  } catch {
    if (
      response.status === 500 &&
      (rawText.includes('ECONNREFUSED') || rawText.includes('connect ECONNREFUSED'))
    ) {
      throw new AnalysisApiError(
        'Unable to reach backend service: connection refused at http://127.0.0.1:8000. Please ensure FastAPI is running.',
        'backend_offline',
        500,
      );
    }
    if (rawText && rawText.length < 200 && !rawText.includes('<html')) {
      throw new AnalysisApiError(
        `The server returned an error (HTTP ${response.status}): ${rawText.trim()}`,
        'invalid_json_response',
        response.status,
      );
    }
    throw new AnalysisApiError(
      `The server responded with invalid JSON (HTTP ${response.status}).`,
      'invalid_json_response',
      response.status,
    );
  }

  if (!response.ok) {
    // Attempt to extract structured error response from FastAPI
    if (
      json &&
      typeof json === 'object' &&
      'error' in json &&
      json.error &&
      typeof json.error === 'object' &&
      'message' in json.error &&
      typeof (json as ApiErrorResponse).error.message === 'string'
    ) {
      const apiErr = (json as ApiErrorResponse).error;
      throw new AnalysisApiError(
        apiErr.message,
        apiErr.code || 'api_error',
        response.status,
        apiErr.details,
      );
    }

    // Fallback if the error envelope is non-standard
    throw new AnalysisApiError(
      `Analysis request failed with HTTP ${response.status}`,
      'http_error',
      response.status,
    );
  }

  return json as AnalyzeResponse;
}

/**
 * Health check response structure returned by GET /api/v1/health.
 */
export interface HealthStatusResponse {
  status: string;
  service: string;
  version: string;
  supportedLanguages: string[];
  plannedLanguages?: string[];
  supportedLanguage?: string;
}

/**
 * Checks backend availability and retrieves active language metadata.
 */
export async function checkBackendHealth(): Promise<HealthStatusResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 4000);
  try {
    const res = await fetch('/api/v1/health', {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return (await res.json()) as HealthStatusResponse;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Backward-compatible wrapper for C++ analysis.
 */
export async function analyzeCppCode(code: string): Promise<AnalyzeResponse> {
  return analyzeCode(code, 'cpp');
}
