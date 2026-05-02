"use client";

import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import { useState } from "react";

export function ReportViewer({ report }: { report: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const wordCount = report.trim().split(/\s+/).length;

  return (
    <div className="report-viewer">
      <div className="report-toolbar">
        <div className="report-meta">
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
            <rect x="1" y="1" width="11" height="11" rx="2" stroke="currentColor" strokeWidth="1.2"/>
            <path d="M3.5 4h6M3.5 6.5h6M3.5 9h4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
          </svg>
          <span>{wordCount.toLocaleString()} words</span>
        </div>
        <button onClick={copy} className={`copy-btn ${copied ? "copied" : ""}`}>
          {copied ? (
            <>
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M2 6.5l3 3 6-6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Copied
            </>
          ) : (
            <>
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <rect x="4" y="4" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.2"/>
                <path d="M9 4V2.5A1.5 1.5 0 007.5 1h-5A1.5 1.5 0 001 2.5v5A1.5 1.5 0 002.5 9H4" stroke="currentColor" strokeWidth="1.2"/>
              </svg>
              Copy Markdown
            </>
          )}
        </button>
      </div>
      <div className="report-divider" />
      <div className="prose-research report-body">
        <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{report}</ReactMarkdown>
      </div>
    </div>
  );
}
