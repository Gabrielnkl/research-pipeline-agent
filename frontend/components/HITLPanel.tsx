"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FlaggedClaim, submitReview, ApiError } from "@/lib/api";
import clsx from "clsx";

interface Props {
  jobId: string;
  flaggedClaims: FlaggedClaim[];
  summaries: string[];
}

function SeverityBadge({ level }: { level: FlaggedClaim["severity"] }) {
  return (
    <span
      className={clsx(
        "inline-block text-xs font-mono px-2 py-0.5 rounded-full border",
        level === "high" && "text-danger border-danger/40 bg-danger/8",
        level === "medium" && "text-amber-400 border-amber-400/40 bg-amber-400/8",
        level === "low" && "text-ink-300 border-ink-600 bg-ink-800"
      )}
    >
      {level}
    </span>
  );
}

export function HITLPanel({ jobId, flaggedClaims, summaries }: Props) {
  const router = useRouter();
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState<"approve" | "reject" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleAction(action: "approve" | "reject") {
    setLoading(action);
    setError(null);

    try {
      await submitReview(jobId, {
        action,
        feedback: feedback.trim() || undefined,
      });
      router.push(`/research/${jobId}`);
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to submit review."
      );
      setLoading(null);
    }
  }

  return (
    <div className="space-y-6">
      {/* Flagged claims */}
      {flaggedClaims.length > 0 && (
        <section>
          <h2 className="text-sm font-mono text-[var(--text-muted)] uppercase tracking-widest mb-3">
            Flagged Claims ({flaggedClaims.length})
          </h2>
          <div className="space-y-3">
            {flaggedClaims.map((claim) => (
              <div
                key={claim.id}
                className={clsx(
                  "rounded-lg border p-4 space-y-2",
                  claim.severity === "high" && "border-danger/25 bg-danger/5",
                  claim.severity === "medium" && "border-amber-400/25 bg-amber-400/5",
                  claim.severity === "low" && "border-[var(--border)] bg-[var(--bg-card)]"
                )}
              >
                <div className="flex items-start gap-2">
                  <SeverityBadge level={claim.severity} />
                  {claim.source && (
                    <span className="text-xs font-mono text-[var(--text-muted)] mt-0.5">
                      {claim.source}
                    </span>
                  )}
                </div>
                <p className="text-sm text-[var(--text)] leading-relaxed">
                  {claim.claim}
                </p>
                <p className="text-xs text-[var(--text-muted)] border-t border-[var(--border)] pt-2">
                  <span className="font-medium text-amber-400">Why flagged: </span>
                  {claim.reason}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Summaries so far */}
      {summaries.length > 0 && (
        <section>
          <h2 className="text-sm font-mono text-[var(--text-muted)] uppercase tracking-widest mb-3">
            Research Summaries So Far
          </h2>
          <div className="space-y-3">
            {summaries.map((summary, i) => (
              <div
                key={i}
                className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-4"
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-mono text-[var(--text-muted)]">
                    Summary {i + 1}
                  </span>
                </div>
                <p className="text-sm text-[var(--text)] leading-relaxed whitespace-pre-wrap">
                  {summary}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Empty state */}
      {flaggedClaims.length === 0 && summaries.length === 0 && (
        <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-8 text-center">
          <p className="text-[var(--text-muted)] text-sm font-mono">
            No flagged claims or summaries yet.
          </p>
        </div>
      )}

      {/* Feedback textarea */}
      <section>
        <label className="block text-sm font-mono text-[var(--text-muted)] uppercase tracking-widest mb-2">
          Feedback (optional)
        </label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Add context, corrections, or guidance for the next research pass..."
          rows={4}
          disabled={loading !== null}
          className="w-full bg-[var(--bg-card)] border border-[var(--border)] focus:border-[var(--border-hover)] rounded-lg px-4 py-3 text-sm text-[var(--text)] placeholder:text-[var(--text-subtle)] resize-none focus:outline-none transition-colors leading-relaxed"
        />
      </section>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger font-mono animate-fade-in">
          {error}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex items-center gap-3 pt-1">
        <button
          onClick={() => handleAction("approve")}
          disabled={loading !== null}
          className={clsx(
            "flex-1 py-3 rounded-lg text-sm font-medium font-mono transition-all duration-150",
            loading === null
              ? "bg-success/15 text-success border border-success/30 hover:bg-success/25 active:scale-[0.98]"
              : "opacity-50 cursor-not-allowed bg-[var(--bg-elevated)] text-[var(--text-muted)] border border-[var(--border)]"
          )}
        >
          {loading === "approve" ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.3" />
                <path d="M7 1.5A5.5 5.5 0 0 1 12.5 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              Approving...
            </span>
          ) : (
            "✓ Approve & Continue"
          )}
        </button>

        <button
          onClick={() => handleAction("reject")}
          disabled={loading !== null}
          className={clsx(
            "flex-1 py-3 rounded-lg text-sm font-medium font-mono transition-all duration-150",
            loading === null
              ? "bg-danger/10 text-danger border border-danger/30 hover:bg-danger/20 active:scale-[0.98]"
              : "opacity-50 cursor-not-allowed bg-[var(--bg-elevated)] text-[var(--text-muted)] border border-[var(--border)]"
          )}
        >
          {loading === "reject" ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.3" />
                <path d="M7 1.5A5.5 5.5 0 0 1 12.5 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              Rejecting...
            </span>
          ) : (
            "↻ Reject & Refine"
          )}
        </button>
      </div>
    </div>
  );
}
