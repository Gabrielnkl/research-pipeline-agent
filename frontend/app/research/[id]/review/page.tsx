import { HITLPanel } from "@/components/HITLPanel";

export default function ReviewPage({ params }: { params: { id: string } }) {
  return (
    <main className="review-page">
      <a href={`/research/${params.id}`} className="back-link">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M9 2L4 7l5 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
        Back to trace
      </a>
      <HITLPanel jobId={params.id} />
    </main>
  );
}
