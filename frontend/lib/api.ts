// ─── Types ────────────────────────────────────────────────────────────────────

export type JobStatus =
  | "queued"
  | "running"
  | "awaiting_review"
  | "complete"
  | "failed";

export interface AgentStep {
  id: string;
  name: string;
  status: "pending" | "running" | "complete" | "failed";
}

export interface FlaggedClaim {
  id: string;
  claim: string;
  reason: string;
  source?: string;
  severity: "low" | "medium" | "high";
}

export interface ResearchJob {
  id: string;
  question: string;
  status: JobStatus;
  steps: AgentStep[];
  flaggedClaims?: FlaggedClaim[];
  report?: string | null;
}

export interface StartResearchResponse {
  id: string;
}

export interface ApproveRequest {
  action: "approve" | "reject";
  feedback?: string;
}

export interface ApproveResponse {
  success: boolean;
  message?: string;
}


// ─── Config ───────────────────────────────────────────────────────────────────

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let message = `API error ${res.status}`;
    try {
      const body = await res.json();
      message = body.detail ?? body.message ?? message;
    } catch {}
    throw new ApiError(message, res.status);
  }

  return res.json();
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}


// ─── Status Mapping ───────────────────────────────────────────────────────────

const STATUS_MAP: Record<string, JobStatus> = {
  queued: "queued",
  pending: "queued",
  running: "running",
  in_progress: "running",
  awaiting_review: "awaiting_review",
  pending_review: "awaiting_review",
  complete: "complete",
  completed: "complete",
  failed: "failed",
  error: "failed",
};

function normalizeJob(raw: Record<string, unknown>): ResearchJob {
  const rawStatus = String(raw.status ?? "queued").toLowerCase();

  return {
    id: String(raw.id),
    question: String(raw.question ?? ""),
    status: STATUS_MAP[rawStatus] ?? "queued",
    steps: (raw.steps ?? []) as AgentStep[],
    flaggedClaims: (raw.flaggedClaims ?? []) as FlaggedClaim[],
    report: (raw.report ?? null) as string | null,
  };
}


// ─── Endpoints ────────────────────────────────────────────────────────────────

export async function startResearch(
  question: string
): Promise<StartResearchResponse> {
  return apiFetch<StartResearchResponse>("/api/research/start", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export async function getResearchStatus(
  id: string
): Promise<ResearchJob> {
  const raw = await apiFetch<Record<string, unknown>>(
    `/api/research/${id}/status`
  );
  return normalizeJob(raw);
}

export async function getResearch(
  id: string
): Promise<ResearchJob> {
  const raw = await apiFetch<Record<string, unknown>>(
    `/api/research/${id}`
  );
  return normalizeJob(raw);
}

export async function submitReview(
  id: string,
  payload: ApproveRequest
): Promise<ApproveResponse> {
  return apiFetch<ApproveResponse>(
    `/api/research/${id}/approve`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}