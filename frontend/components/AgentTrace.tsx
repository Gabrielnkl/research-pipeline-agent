"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { getResearchStatus, ResearchJob, AgentStep, JobStatus } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";
import clsx from "clsx";

// Icons
function CheckIcon() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
      <path d="M2.5 7L5.5 10L11.5 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function SpinnerIcon() {
  return (
    <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 14 14" fill="none">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.2" />
      <path d="M7 1.5A5.5 5.5 0 0 1 12.5 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}
function XIcon() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
      <path d="M3 3L11 11M11 3L3 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
function ClockIcon() {
  return (
    <svg className="w-3.5 h-3.5" viewBox="0 0 14 14" fill="none">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M7 4V7L9 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function StepCard({ step, index }: { step: AgentStep; index: number }) {
  const isComplete = step.status === "complete";
  const isRunning = step.status === "running";
  const isFailed = step.status === "failed";
  const isPending = step.status === "pending";

  return (
    <div
      className={clsx(
        "flex items-start gap-3 p-3.5 rounded-lg border transition-all duration-300 animate-slide-up",
        isComplete && "border-[var(--border)] bg-[var(--bg-card)]",
        isRunning && "border-signal/30 bg-signal/5",
        isFailed && "border-danger/30 bg-danger/5",
        isPending && "border-[var(--border)] bg-[var(--bg-elevated)] opacity-50"
      )}
      style={{ animationDelay: `${index * 60}ms`, animationFillMode: "both" }}
    >
      {/* Step icon */}
      <div
        className={clsx(
          "flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mt-0.5",
          isComplete && "bg-success/15 text-success",
          isRunning && "bg-signal/15 text-signal",
          isFailed && "bg-danger/15 text-danger",
          isPending && "bg-ink-700 text-ink-500"
        )}
      >
        {isComplete && <CheckIcon />}
        {isRunning && <SpinnerIcon />}
        {isFailed && <XIcon />}
        {isPending && <ClockIcon />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span
            className={clsx(
              "text-sm font-medium",
              isComplete && "text-[var(--text)]",
              isRunning && "text-signal",
              isFailed && "text-danger",
              isPending && "text-[var(--text-muted)]"
            )}
          >
            {step.name}
          </span>
          {step.durationMs && (
            <span className="text-xs font-mono text-[var(--text-muted)] flex-shrink-0">
              {step.durationMs < 1000
                ? `${step.durationMs}ms`
                : `${(step.durationMs / 1000).toFixed(1)}s`}
            </span>
          )}
        </div>
        {step.detail && (
          <p className="text-xs text-[var(--text-muted)] mt-0.5 leading-relaxed line-clamp-2">
            {step.detail}
          </p>
        )}
      </div>
    </div>
  );
}

interface Props {
  jobId: string;
  initialJob?: ResearchJob;
}

export function AgentTrace({ jobId, initialJob }: Props) {
  const router = useRouter();
  const [job, setJob] = useState<ResearchJob | null>(initialJob ?? null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const TERMINAL: JobStatus[] = ["complete", "failed", "awaiting_review"];

  const poll = useCallback(async () => {
    try {
      const data = await getResearchStatus(jobId);
      setJob(data);
      setError(null);

      if (TERMINAL.includes(data.status)) {
        if (intervalRef.current) clearInterval(intervalRef.current);

        if (data.status === "awaiting_review") {
          // small delay so user sees the status change before redirect
          setTimeout(() => router.push(`/research/${jobId}/review`), 800);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Polling error");
    }
  }, [jobId, router]);

  useEffect(() => {
    poll(); // immediate first fetch
    intervalRef.current = setInterval(poll, 2000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [poll]);

  if (error) {
    return (
      <div className="rounded-lg border border-danger/30 bg-danger/5 p-4 text-sm text-danger font-mono">
        Error polling status: {error}
      </div>
    );
  }

  if (!job) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 rounded-lg bg-[var(--bg-card)] animate-pulse" />
        ))}
      </div>
    );
  }

  const completedCount = job.steps.filter((s) => s.status === "complete").length;
  const totalCount = job.steps.length;
  const progress = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  return (
    <div className="space-y-4">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <StatusBadge status={job.status} />
          {job.status === "running" && (
            <span className="text-xs font-mono text-[var(--text-muted)]">
              {completedCount}/{totalCount} steps
            </span>
          )}
        </div>
        {job.status === "running" && (
          <div className="flex items-center gap-1.5">
            <div className="w-24 h-1 rounded-full bg-[var(--bg-card)] overflow-hidden">
              <div
                className="h-full bg-signal rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Review banner */}
      {job.status === "awaiting_review" && (
        <div className="rounded-lg border border-amber-400/40 bg-amber-400/8 px-4 py-3 flex items-center justify-between animate-fade-in">
          <div className="flex items-center gap-2">
            <span className="text-amber-400 text-sm font-medium">
              ⚠ Human review required
            </span>
            <span className="text-xs text-[var(--text-muted)]">
              {job.flaggedClaims?.length ?? 0} claim(s) flagged
            </span>
          </div>
          <a
            href={`/research/${jobId}/review`}
            className="text-xs font-mono font-medium text-amber-400 border border-amber-400/40 px-3 py-1 rounded hover:bg-amber-400/10 transition-colors"
          >
            Review →
          </a>
        </div>
      )}

      {/* Step cards */}
      <div className="space-y-2">
        {job.steps.length === 0 ? (
          <div className="text-sm text-[var(--text-muted)] text-center py-8 font-mono">
            Initializing agent...
          </div>
        ) : (
          job.steps.map((step, i) => (
            <StepCard key={step.id} step={step} index={i} />
          ))
        )}
      </div>

      {/* Complete state */}
      {job.status === "complete" && (
        <div className="rounded-lg border border-success/30 bg-success/5 px-4 py-3 text-sm text-success font-medium animate-fade-in">
          ✓ Research complete — report ready below
        </div>
      )}

      {/* Failed state */}
      {job.status === "failed" && job.error && (
        <div className="rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 animate-fade-in">
          <p className="text-sm text-danger font-medium mb-1">Research failed</p>
          <p className="text-xs text-[var(--text-muted)] font-mono">{job.error}</p>
        </div>
      )}
    </div>
  );
}
