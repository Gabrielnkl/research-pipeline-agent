"use client";

export function AgentTrace({ steps }: { steps: any[] }) {
  return (
    <div className="agent-trace">
      <p className="trace-heading">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.2"/>
          <path d="M6 3v3.5l2.5 1.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
        </svg>
        Agent Steps
      </p>
      <div className="steps-list">
        {steps.map((step, i) => {
          const done = step.status === "complete";
          const active = step.status === "running";
          return (
            <div key={step.id} className={`step-row ${done ? "done" : ""} ${active ? "active" : ""}`}>
              <div className="step-line-col">
                <div className="step-dot">
                  {done ? (
                    <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
                      <path d="M1.5 4l2 2 3-3" stroke="#0f0f0f" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  ) : active ? (
                    <div className="dot-pulse" />
                  ) : (
                    <div className="dot-idle" />
                  )}
                </div>
                {i < steps.length - 1 && <div className={`step-connector ${done ? "done" : ""}`} />}
              </div>
              <div className="step-content">
                <span className="step-name">{step.name}</span>
                {step.detail && <span className="step-detail">{step.detail}</span>}
              </div>
              <div className="step-status">
                {done && <span className="step-tag done">done</span>}
                {active && <span className="step-tag active">running</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
