// app/research/[id]/page.tsx
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

  if (!job) return <p>Loading...</p>;

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-6">
      <StatusBadge status={job.status} />

      <AgentTrace steps={job.steps} />

      {job.status === "complete" && job.report && (
        <ReportViewer report={job.report} />
      )}
    </main>
  );
}