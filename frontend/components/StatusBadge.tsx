"use client";

import { JobStatus } from "@/lib/api";
import clsx from "clsx";

interface Props {
  status: JobStatus;
  pulse?: boolean;
}

const CONFIG: Record<
  JobStatus,
  { label: string; dot: string; bg: string; text: string }
> = {
  queued: {
    label: "Queued",
    dot: "bg-ink-400",
    bg: "bg-ink-800",
    text: "text-ink-300",
  },
  running: {
    label: "Running",
    dot: "bg-signal animate-pulse",
    bg: "bg-signal/10",
    text: "text-signal",
  },
  awaiting_review: {
    label: "Awaiting Review",
    dot: "bg-amber-400 animate-pulse",
    bg: "bg-amber-400/10",
    text: "text-amber-400",
  },
  complete: {
    label: "Complete",
    dot: "bg-success",
    bg: "bg-success/10",
    text: "text-success",
  },
  failed: {
    label: "Failed",
    dot: "bg-danger",
    bg: "bg-danger/10",
    text: "text-danger",
  },
};

export function StatusBadge({ status }: Props) {
  const cfg = CONFIG[status] ?? CONFIG["queued"]; // ← fallback
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium",
        cfg.bg,
        cfg.text
      )}
    >
      <span className={clsx("w-1.5 h-1.5 rounded-full", cfg.dot)} />
      {cfg.label}
    </span>
  );
}
