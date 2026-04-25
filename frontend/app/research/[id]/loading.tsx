export default function Loading() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-10 animate-pulse">
      <div className="h-4 w-32 bg-[var(--bg-card)] rounded mb-6" />
      <div className="h-8 w-3/4 bg-[var(--bg-card)] rounded mb-2" />
      <div className="h-4 w-1/3 bg-[var(--bg-card)] rounded mb-8" />
      <div className="space-y-3">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-14 bg-[var(--bg-card)] rounded-lg" />
        ))}
      </div>
    </div>
  );
}
