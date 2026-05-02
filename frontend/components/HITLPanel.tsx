"use client";

import { useState } from "react";
import { submitReview } from "@/lib/api";
import { useRouter } from "next/navigation";

export function HITLPanel({ jobId }: { jobId: string }) {
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const [focused, setFocused] = useState(false);
  const router = useRouter();

  async function handle(action: "approve" | "reject") {
    setLoading(true);
    try {
      await submitReview(jobId, { action, feedback });
      router.push(`/research/${jobId}`);
    } catch (err) {
      console.error(err);
      alert("Failed to submit review");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="hitl-panel">
      <div className="hitl-header">
        <div className="hitl-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 1a3 3 0 100 6 3 3 0 000-6zM2 13c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
          </svg>
        </div>
        <div>
          <h2 className="hitl-title">Human Review Required</h2>
          <p className="hitl-subtitle">The agent has paused and is awaiting your decision before continuing.</p>
        </div>
      </div>

      <div className={`hitl-textarea-wrap ${focused ? "focused" : ""}`}>
        <textarea
          className="hitl-textarea"
          placeholder="Optional feedback or instructions for the next iteration..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          rows={3}
        />
      </div>

      <div className="hitl-actions">
        <button disabled={loading} onClick={() => handle("reject")} className="hitl-btn reject">
          {loading ? <span className="btn-spinner" /> : (
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          )}
          Reject & Refine
        </button>
        <button disabled={loading} onClick={() => handle("approve")} className="hitl-btn approve">
          {loading ? <span className="btn-spinner dark" /> : (
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 7l3.5 3.5L12 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          )}
          Approve & Continue
        </button>
      </div>
    </div>
  );
}
