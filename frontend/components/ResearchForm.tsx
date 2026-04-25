"use client";

import { useState, useRef, KeyboardEvent } from "react";
import { useRouter } from "next/navigation";
import { startResearch, ApiError } from "@/lib/api";
import clsx from "clsx";

const EXAMPLES = [
  "What are the latest breakthroughs in room-temperature superconductors?",
  "How do transformer architectures differ from state space models for long-context tasks?",
  "What is the current state of fusion energy commercialization?",
  "Compare the regulatory approaches to AI safety across the EU, US, and China.",
];

export function ResearchForm() {
  const router = useRouter();
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const charCount = question.trim().length;
  const isValid = charCount >= 10;

  async function handleSubmit() {
    if (!isValid || loading) return;
    setLoading(true);
    setError(null);

    try {
      const { id } = await startResearch(question.trim());
      router.push(`/research/${id}`);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Failed to start research. Is the backend running?"
      );
      setLoading(false);
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function fillExample(ex: string) {
    setQuestion(ex);
    textareaRef.current?.focus();
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Main input card */}
      <div
        className={clsx(
          "rounded-xl border transition-all duration-200 bg-[var(--bg-card)]",
          question.length > 0
            ? "border-[var(--border-hover)]"
            : "border-[var(--border)]"
        )}
      >
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="What do you want to research?"
          rows={4}
          className="w-full bg-transparent resize-none p-5 text-[var(--text)] placeholder:text-[var(--text-subtle)] text-base focus:outline-none leading-relaxed font-sans"
          disabled={loading}
        />

        <div className="flex items-center justify-between px-5 pb-4">
          <span
            className={clsx(
              "text-xs font-mono transition-colors",
              charCount < 10 && charCount > 0
                ? "text-amber-400"
                : "text-[var(--text-muted)]"
            )}
          >
            {charCount > 0 && `${charCount} chars`}
            {charCount > 0 && charCount < 10 && " (min 10)"}
          </span>

          <div className="flex items-center gap-3">
            <span className="text-xs text-[var(--text-muted)] font-mono hidden sm:block">
              ⌘ + Enter
            </span>
            <button
              onClick={handleSubmit}
              disabled={!isValid || loading}
              className={clsx(
                "px-5 py-2.5 rounded-lg text-sm font-medium font-mono transition-all duration-150",
                isValid && !loading
                  ? "bg-signal text-ink-900 hover:bg-signal-dark active:scale-[0.97]"
                  : "bg-[var(--bg-elevated)] text-[var(--text-muted)] cursor-not-allowed"
              )}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" strokeOpacity="0.3" />
                    <path d="M7 1.5A5.5 5.5 0 0 1 12.5 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                  Starting...
                </span>
              ) : (
                "Research →"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-3 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger font-mono animate-fade-in">
          {error}
        </div>
      )}

      {/* Example prompts */}
      <div className="mt-6">
        <p className="text-xs font-mono text-[var(--text-muted)] mb-3 uppercase tracking-widest">
          Try an example
        </p>
        <div className="grid gap-2">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              onClick={() => fillExample(ex)}
              className="text-left text-sm text-[var(--text-muted)] hover:text-[var(--text)] border border-[var(--border)] hover:border-[var(--border-hover)] rounded-lg px-4 py-2.5 transition-all duration-150 leading-snug"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
