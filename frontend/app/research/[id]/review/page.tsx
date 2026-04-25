import { notFound, redirect } from "next/navigation";
import { getResearchStatus } from "@/lib/api";
import { HITLPanel } from "@/components/HITLPanel";
import { StatusBadge } from "@/components/StatusBadge";

interface Props {
  params: { id: string };
}

export default async function ReviewPage({ params }: Props) {
  let job;
  try {
    job = await getResearchStatus(params.id);
  } catch {
    notFound();
  }

  // If not awaiting review, redirect back to the job page
  if (job.status !== "awaiting_review") {
    redirect(`/research/${params.id}`);
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-1">
          <a
            href={`/research/${params.id}`}
            className="text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
          >
            ← Job Status
          </a>
          <span className="text-[var(--text-subtle)]">/</span>
          <span className="text-xs font-mono text-[var(--text-muted)]">review</span>
        </div>

        <div className="mt-4 rounded-xl border border-amber-400/30 bg-amber-400/5 px-5 py-4">
          <div className="flex items-start justify-between gap-4 mb-2">
            <div>
              <h1 className="text-lg font-medium text-amber-400 font-mono mb-1">
                Human Review Required
              </h1>
              <p className="text-sm text-[var(--text-muted)]">
                The agent has paused and is waiting for your review before
                continuing.
              </p>
            </div>
            <StatusBadge status={job.status} />
          </div>
          <div className="border-t border-amber-400/15 pt-3 mt-3">
            <p className="text-xs font-mono text-[var(--text-muted)]">Question</p>
            <p className="text-sm text-[var(--text)] mt-0.5 font-display italic">
              "{job.question}"
            </p>
          </div>
        </div>
      </div>

      {/* HITL Panel */}
      <HITLPanel
        jobId={params.id}
        flaggedClaims={job.flaggedClaims ?? []}
        summaries={job.summaries ?? []}
      />
    </div>
  );
}
