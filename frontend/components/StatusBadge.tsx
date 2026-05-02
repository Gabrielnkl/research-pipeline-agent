export function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { label: string; dot: string; bg: string; text: string; pulse?: boolean }> = {
    running:         { label: "Running",      dot: "#60a5fa", bg: "rgba(96,165,250,0.1)",  text: "#93c5fd", pulse: true },
    awaiting_review: { label: "Needs Review", dot: "#fbbf24", bg: "rgba(251,191,36,0.1)",  text: "#fcd34d" },
    complete:        { label: "Complete",     dot: "#34d399", bg: "rgba(52,211,153,0.1)",  text: "#6ee7b7" },
    failed:          { label: "Failed",       dot: "#f87171", bg: "rgba(248,113,113,0.1)", text: "#fca5a5" },
  };

  const c = config[status] ?? { label: status, dot: "#888", bg: "rgba(136,136,136,0.1)", text: "#aaa" };

  return (
    <span className="status-badge" style={{ background: c.bg }}>
      <span className={`status-dot ${c.pulse ? "pulse" : ""}`} style={{ background: c.dot }} />
      <span className="status-text" style={{ color: c.text }}>{c.label}</span>
    </span>
  );
}
