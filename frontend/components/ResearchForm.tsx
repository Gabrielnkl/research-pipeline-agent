"use client";

import { useState } from "react";
import { startResearch } from "@/lib/api";
import { useRouter } from "next/navigation";

const EXAMPLES = [
  "What are the main causes of inflation in 2024?",
  "How is AI impacting the job market in 2025?",
  "What are the economic effects of high interest rates?",
  "How do supply chain disruptions affect global trade?"
];

export function ResearchForm() {
  const [question, setQuestion] = useState("");
  const [focused, setFocused] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim()) return;
    try {
      const res = await startResearch(question);
      router.push(`/research/${res.id}`);
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="research-form">
      <div className={`textarea-wrapper ${focused ? "focused" : ""}`}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Ask a research question..."
          rows={4}
          className="research-textarea"
        />
        <div className="textarea-corner" />
      </div>

      <div className="examples-section">
        <p className="examples-label">
          <span className="examples-label-line" />
          Try an example
          <span className="examples-label-line" />
        </p>
        <div className="examples-grid">
          {EXAMPLES.map((example, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setQuestion(example)}
              className="example-chip"
            >
              <span className="example-chip-icon">↗</span>
              {example}
            </button>
          ))}
        </div>
      </div>

      <div className="submit-row">
        <span className="char-count">{question.length} chars</span>
        <button type="submit" disabled={!question.trim()} className="submit-btn">
          <span>Begin Research</span>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
    </form>
  );
}
