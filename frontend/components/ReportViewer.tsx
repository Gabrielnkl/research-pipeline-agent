"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github-dark.css";
import clsx from "clsx";

interface Props {
  report: string;
  question?: string;
}

export function ReportViewer({ report, question }: Props) {
  const [copied, setCopied] = useState(false);

  async function copyMarkdown() {
    try {
      await navigator.clipboard.writeText(report);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback
      const el = document.createElement("textarea");
      el.value = report;
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  const wordCount = report.split(/\s+/).filter(Boolean).length;
  const readTime = Math.max(1, Math.ceil(wordCount / 200));

  return (
    <div className="space-y-4">
      {/* Report header */}
      <div className="rounded-xl border border-success/20 bg-success/5 px-5 py-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-success text-xs font-mono font-medium uppercase tracking-widest">
                Research Complete
              </span>
            </div>
            {question && (
              <p className="text-sm text-[var(--text)] leading-snug font-display italic">
                "{question}"
              </p>
            )}
          </div>
          <div className="text-right flex-shrink-0">
            <p className="text-xs font-mono text-[var(--text-muted)]">
              {wordCount.toLocaleString()} words
            </p>
            <p className="text-xs font-mono text-[var(--text-muted)]">
              ~{readTime} min read
            </p>
          </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono text-[var(--text-muted)] uppercase tracking-widest">
          Final Report
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={copyMarkdown}
            className={clsx(
              "flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded border transition-all duration-150",
              copied
                ? "text-success border-success/40 bg-success/8"
                : "text-[var(--text-muted)] border-[var(--border)] hover:border-[var(--border-hover)] hover:text-[var(--text)]"
            )}
          >
            {copied ? (
              <>
                <svg className="w-3 h-3" viewBox="0 0 12 12" fill="none">
                  <path d="M2 6L5 9L10 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg className="w-3 h-3" viewBox="0 0 12 12" fill="none">
                  <rect x="4" y="1" width="7" height="8" rx="1" stroke="currentColor" strokeWidth="1.2" />
                  <path d="M1 4h1.5M1 4v6a1 1 0 0 0 1 1h5.5V9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
                </svg>
                Copy as Markdown
              </>
            )}
          </button>

          <a
            href="/"
            className="flex items-center gap-1.5 text-xs font-mono px-3 py-1.5 rounded border border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--border-hover)] hover:text-[var(--text)] transition-all duration-150"
          >
            <svg className="w-3 h-3" viewBox="0 0 12 12" fill="none">
              <path d="M6 1L11 4V8L6 11L1 8V4L6 1Z" stroke="currentColor" strokeWidth="1.2" />
            </svg>
            New Research
          </a>
        </div>
      </div>

      {/* Report body */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-6 sm:p-8">
        <div className="prose-research">
          <ReactMarkdown
            rehypePlugins={[rehypeHighlight]}
          >
            {report}
          </ReactMarkdown>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-5 py-4 flex items-center justify-between">
        <p className="text-sm text-[var(--text-muted)]">
          Start a new research session
        </p>
        <a
          href="/"
          className="text-sm font-mono font-medium text-signal border border-signal/40 px-4 py-1.5 rounded hover:bg-signal/10 transition-colors"
        >
          New Research →
        </a>
      </div>
    </div>
  );
}
