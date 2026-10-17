import { Check, ChevronRight } from "lucide-react";

/**
 * One step of the guided flow. The active step is expanded and glows, with a
 * "Start here" / "Next" badge, so a first-time visitor knows what to do.
 */
export default function StepCard({ step, state, complete, badge, summary, onOpen, children }) {
  const active = state === "active";
  // an open step that is already complete stops pulsing, so the eye moves on
  const calm = active && complete;
  return (
    <section className={`step ${state} ${calm ? "calm" : ""}`}>
      <button className="step-head" onClick={onOpen} aria-expanded={active}>
        <span className="step-num">{state === "done" && !active ? <Check size={15} /> : step.n}</span>
        <span>
          <span className="step-title" style={{ display: "block" }}>{step.title}</span>
          <span className="step-sub">{step.sub}</span>
        </span>
        {active ? (
          <span className={`badge-now ${calm ? "calm" : ""}`}>{calm ? <><Check size={11} /> Done</> : badge}</span>
        ) : (
          <ChevronRight size={16} style={{ marginLeft: "auto", color: "var(--muted)" }} />
        )}
      </button>
      {active ? <div className="step-body">{children}</div> : <div className="step-summary">{summary}</div>}
    </section>
  );
}
