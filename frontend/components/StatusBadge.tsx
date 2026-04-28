export function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    running: "bg-blue-500",
    awaiting_review: "bg-yellow-500",
    complete: "bg-green-500",
    failed: "bg-red-500",
  };

  return (
    <span className={`text-white px-3 py-1 rounded ${colors[status]}`}>
      {status}
    </span>
  );
}