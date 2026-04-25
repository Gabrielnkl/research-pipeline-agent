import { ResearchForm } from "@/components/ResearchForm";

export default function HomePage() {
  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center px-6 py-16">
      {/* Hero */}
      <div className="text-center mb-12 max-w-xl">
        <div className="inline-flex items-center gap-2 text-xs font-mono text-[var(--text-muted)] border border-[var(--border)] rounded-full px-3 py-1 mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-signal animate-pulse" />
          Powered by multi-agent orchestration
        </div>
        <h1 className="font-display text-4xl sm:text-5xl text-[var(--text)] leading-tight mb-4">
          Deep Research,{" "}
          <span className="italic text-[var(--text-muted)]">
            with human oversight
          </span>
        </h1>
        <p className="text-[var(--text-muted)] text-base leading-relaxed">
          Ask any complex question. Our agent searches, synthesizes, and flags
          uncertain claims for your review before producing the final report.
        </p>
      </div>

      {/* Form */}
      <ResearchForm />

      {/* Feature pills */}
      <div className="mt-12 flex flex-wrap justify-center gap-2">
        {[
          "Orchestrator agent",
          "Web search",
          "Claim verification",
          "Human review",
          "Markdown report",
        ].map((f) => (
          <span
            key={f}
            className="text-xs font-mono text-[var(--text-muted)] border border-[var(--border)] rounded-full px-3 py-1"
          >
            {f}
          </span>
        ))}
      </div>
    </div>
  );
}
