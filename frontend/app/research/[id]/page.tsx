"use client";

import { useEffect, useState } from "react";
import { getResearchStatus } from "@/lib/api";
import { AgentTrace } from "@/components/AgentTrace";
import { StatusBadge } from "@/components/StatusBadge";
import { ReportViewer } from "@/components/ReportViewer";
import { useRouter } from "next/navigation";

export default function ResearchPage({ params }: { params: { id: string } }) {
  const [job, setJob] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await getResearchStatus(params.id);
        setJob(data);
        if (data.status === "awaiting_review") {
          router.push(`/research/${params.id}/review`);
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [params.id]);

  if (!job) return (
    <div className="research-loading">
      <div className="loading-orb" />
      <span>Connecting to agent...</span>
    </div>
  );

  return (
    <main className="research-page">
      <div className="research-header">
        <a href="/" className="back-link">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M9 2L4 7l5 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          New query
        </a>
        <StatusBadge status={job.status} />
      </div>

      {job.question && (
        <div className="research-question">
          <p className="question-label">Research Query</p>
          <p className="question-text">&ldquo;{job.question}&rdquo;</p>
        </div>
      )}

      <AgentTrace steps={job.steps} />

      {job.status === "complete" && job.report && (
        <div className="report-section">
          <div className="report-heading">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
              <path d="M6.5 1L12 4v5l-5.5 3L1 9V4L6.5 1z" stroke="var(--signal)" strokeWidth="1.2"/>
            </svg>
            <span>Research Report</span>
          </div>
          <ReportViewer report={job.report} />
        </div>
      )}
    </main>
  );
}
