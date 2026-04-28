// app/research/[id]/review/page.tsx
import { HITLPanel } from "@/components/HITLPanel";

export default function ReviewPage({ params }: { params: { id: string } }) {
  return (
    <main className="max-w-3xl mx-auto p-6">
      <HITLPanel jobId={params.id} />
    </main>
  );
}