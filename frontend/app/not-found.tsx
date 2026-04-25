export default function NotFound() {
  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex flex-col items-center justify-center px-6">
      <p className="font-mono text-5xl text-[var(--text-subtle)] mb-4">404</p>
      <h2 className="font-display text-2xl text-[var(--text)] mb-2">
        Research job not found
      </h2>
      <p className="text-[var(--text-muted)] text-sm mb-8">
        This job ID doesn't exist or may have expired.
      </p>
      <a
        href="/"
        className="text-sm font-mono text-signal border border-signal/40 px-5 py-2.5 rounded hover:bg-signal/10 transition-colors"
      >
        Start new research →
      </a>
    </div>
  );
}
