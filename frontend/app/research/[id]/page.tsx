import { notFound } from "next/navigation";
import { getResearchStatus } from "@/lib/api";
import { AgentTrace } from "@/components/AgentTrace";
import { ReportViewer } from "@/components/ReportViewer";
import { StatusBadge } from "@/components/StatusBadge";

interface Props {
  params: { id: string };
}

export default async function ResearchPage({ params }: Props) {
  let job;
  try {
    job = await getResearchStatus(params.id);
  } catch {
    notFound();
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      {/* Page header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-1">
          <a
            href="/"
            className="text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
          >
            ← Home
          </a>
          <span className="text-[var(--text-subtle)]">/</span>
          <span className="text-xs font-mono text-[var(--text-muted)]">
            {params.id}
          </span>
        </div>
        <div className="flex items-start justify-between gap-4 mt-4">
          <h1 className="font-display text-2xl text-[var(--text)] leading-snug flex-1">
            {job.question}
          </h1>
          <div className="flex-shrink-0 mt-1">
            <StatusBadge status={job.status} />
          </div>
        </div>
        <p className="text-xs font-mono text-[var(--text-muted)] mt-2">
          Started {new Date(job.createdAt).toLocaleString()}
        </p>
      </div>

      {/* Agent trace — always shown (handles polling internally) */}
      <section className="mb-8">
        <h2 className="text-xs font-mono text-[var(--text-muted)] uppercase tracking-widest mb-4">
          Agent Pipeline
        </h2>
        <AgentTrace jobId={params.id} initialJob={job} />
      </section>

      {/* Report — shown when complete */}
      {job.status === "complete" && job.report && (
        <section>
          <ReportViewer report={job.report} question={job.question} />
        </section>
      )}
    </div>
  );
}
