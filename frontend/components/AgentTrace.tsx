"use client";

export function AgentTrace({ steps }: { steps: any[] }) {
  return (
    <div className="space-y-2">
      {steps.map((step) => (
        <div
          key={step.id}
          className="border rounded p-3 flex justify-between"
        >
          <span>{step.name}</span>
          <span>{step.status === "complete" ? "✓" : "..."}</span>
        </div>
      ))}
    </div>
  );
}