// app/page.tsx
import { ResearchForm } from "@/components/ResearchForm";

export default function HomePage() {
  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">
        Research Pipeline Agent
      </h1>
      <ResearchForm />
    </main>
  );
}