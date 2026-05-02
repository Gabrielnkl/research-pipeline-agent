import { ResearchForm } from "@/components/ResearchForm";

export default function HomePage() {
  return (
    <main className="home-page">
      <div className="home-hero">
        <div className="hero-eyebrow">
          <span className="eyebrow-dot" />
          Deep Research Pipeline
        </div>
        <h1 className="hero-title">
          Ask anything.<br />
          <em>Get answers that matter.</em>
        </h1>
        <p className="hero-sub">
          Powered by an autonomous agent with human-in-the-loop review.
          Complex questions, rigorous research, verified conclusions.
        </p>
      </div>
      <div className="home-form-card">
        <ResearchForm />
      </div>
    </main>
  );
}
