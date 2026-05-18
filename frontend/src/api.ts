export type PhaseId =
  | "FASE_0"
  | "FASE_1"
  | "FASE_2"
  | "FASE_3"
  | "FASE_3B"
  | "FASE_4"
  | "FASE_5"
  | "FASE_6"
  | "FASE_7"
  | "FASE_7B"
  | "FASE_7C"
  | "FASE_8"
  | "FASE_8B"
  | "FASE_9"
  | "FASE_10"
  | "FASE_11"
  | "FASE_12"
  | "FASE_13"
  | "FASE_14"
  | "FASE_15"
  | "FASE_16"
  | "FASE_17"
  | "FASE_18";

export type GateResult = {
  status: string;
  errors: string[];
  repair_phase?: PhaseId | null;
  max_retries_remaining?: number | null;
  blocking_rules: string[];
  next_phase?: PhaseId | null;
  score?: ScoreReport | null;
};

export type TurnResult = {
  session_id: string;
  current_phase: PhaseId;
  next_phase?: PhaseId | null;
  prompt?: string | null;
  artifacts_summary: Record<string, unknown>;
  gate?: GateResult | null;
  blocked: boolean;
};

export type RuleResult = {
  rule_id: string;
  label: string;
  max_points: number;
  points: number;
  passed: boolean;
  failures: string[];
  repair_phase?: PhaseId | null;
  evidence_paths: string[];
};

export type ScoreReport = {
  score_id: string;
  phase_id: PhaseId;
  total_points: number;
  max_points: number;
  percent: number;
  status: string;
  risk?: string | null;
  rules: RuleResult[];
  repair_targets: PhaseId[];
};

export type GraphNode = {
  id: string;
  tipo: string;
  criticidad: string;
  metadata: Record<string, unknown>;
};

export type GraphEdge = {
  source: string;
  target: string;
  tipo: string;
  criticidad: string;
  consistencia: string;
};

export type SystemGraph = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type TraceabilityNode = {
  id: string;
  nivel: string;
  tipo: string;
  refs: string[];
};

export type TraceabilityGraph = {
  hierarchy: TraceabilityNode[];
  matrix: {
    rows: Array<Record<string, string>>;
  };
  traceability_type: string;
};

export type CheckpointState = {
  phase_11: "pending" | "approved" | "change_requested" | "incomplete";
  phase_18:
    | "pending"
    | "approved"
    | "change_requested"
    | "incomplete"
    | "revalidate";
};

export type AuditEvent = {
  timestamp: string;
  phase_id: PhaseId;
  input_hash: string;
  output_hash: string;
  gate_result: string;
};

export type InterviewSession = {
  session_id: string;
  current_phase: PhaseId;
  artifacts: {
    dimensions_12d: Record<string, unknown>;
    sec_initial?: Record<string, unknown> | null;
    sec_extended?: Record<string, unknown> | null;
    system_graph?: SystemGraph | null;
    traceability_graph?: TraceabilityGraph | null;
    estimations?: { entries: unknown[] };
    decision_records?: unknown[];
    sec_state?: Record<string, unknown>;
  };
  scores: Record<string, ScoreReport>;
  checkpoints: CheckpointState;
  audit_log: AuditEvent[];
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

export class ApiError extends Error {
  status: number;
  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(readableError(detail, status));
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    const detail = await parseError(response);
    throw new ApiError(response.status, detail);
  }
  return response.json() as Promise<T>;
}

export function createSession(sessionId: string): Promise<TurnResult> {
  return request<TurnResult>("/sessions", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId })
  });
}

export function getSession(sessionId: string): Promise<InterviewSession> {
  return request<InterviewSession>(`/sessions/${sessionId}`);
}

export function advanceSession(
  sessionId: string,
  userInput: string
): Promise<TurnResult> {
  return request<TurnResult>(`/sessions/${sessionId}/advance`, {
    method: "POST",
    body: JSON.stringify({ user_input: userInput })
  });
}

export function submitCheckpoint(
  sessionId: string,
  verdict: string
): Promise<TurnResult> {
  return request<TurnResult>(`/sessions/${sessionId}/checkpoint`, {
    method: "POST",
    body: JSON.stringify({ verdict })
  });
}

async function parseError(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function readableError(detail: unknown, status: number): string {
  if (typeof detail === "string") return detail;
  if (
    detail &&
    typeof detail === "object" &&
    "detail" in detail &&
    typeof detail.detail === "string"
  ) {
    return detail.detail;
  }
  return `HTTP ${status}`;
}
