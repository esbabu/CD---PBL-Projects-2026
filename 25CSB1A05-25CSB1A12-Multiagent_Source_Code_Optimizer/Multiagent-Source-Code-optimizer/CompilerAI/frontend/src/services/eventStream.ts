export interface BackendRunEvent {
  run_id: string;
  seq: number;
  type: string;
  agent?: string;
  stage?: string;
  status?: string;
  timestamp: string;
  message: string;
  data: Record<string, any>;
}

export type EventCallback = (event: BackendRunEvent) => void;
export type ErrorCallback = (error: any) => void;

export class RunEventStream {
  private eventSource: EventSource | null = null;
  private isClosed = false;

  constructor(
    private runId: string,
    private onEvent: EventCallback,
    private onError?: ErrorCallback,
    private onComplete?: () => void
  ) {}

  connect(): void {
    if (this.eventSource) {
      this.close();
    }

    this.isClosed = false;
    const url = `/api/runs/${this.runId}/events`;
    this.eventSource = new EventSource(url);

    this.eventSource.onmessage = (e) => {
      if (this.isClosed) return;
      try {
        const parsed: BackendRunEvent = JSON.parse(e.data);
        this.onEvent(parsed);

        if (
          parsed.type === 'run_completed' ||
          parsed.type === 'run_partially_completed' ||
          parsed.type === 'run_cancelled'
        ) {
          this.close();
          this.onComplete?.();
        }
      } catch (err) {
        console.error('Failed to parse SSE event data:', err);
      }
    };

    this.eventSource.onerror = (e) => {
      if (this.isClosed) return;
      this.onError?.(e);
      this.close();
    };
  }

  close(): void {
    this.isClosed = true;
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}
