import { Check, Orbit, RotateCcw } from "lucide-react";

export default function TopBar({ steps, stepState, onStep, health, onReset }) {
  const ok = health?.neo4j && health?.openai_key;
  const status = !health ? "Connecting…" : !health.neo4j ? "Neo4j not reachable" : !health.openai_key ? "OpenAI key missing" : "Neo4j Aura connected";

  return (
    <header className="topbar">
      <div className="brand">
        <div className="brand-mark">
          <Orbit size={20} />
        </div>
        <div>
          <h1>Research Gap Hunter</h1>
          <p>Graph + AI novelty radar for research ideas</p>
        </div>
      </div>

      <nav className="stepper" aria-label="Demo steps">
        {steps.map((s, i) => {
          const state = stepState(s.n);
          return (
            <span key={s.n} style={{ display: "contents" }}>
              {i > 0 && <span className="stepper-sep" />}
              <button className={`stepper-item ${state}`} onClick={() => onStep(s.n)}>
                <span className="num">{state === "done" ? <Check size={13} /> : s.n}</span>
                <span className="label">{s.title}</span>
              </button>
            </span>
          );
        })}
      </nav>

      <div className="top-actions">
        <span className={`status-chip ${health && !ok ? "bad" : ""}`}>
          <span className="status-dot" />
          {status}
        </span>
        <button className="btn sm ghost" onClick={onReset} title="Remove live uploads and start the demo again">
          <RotateCcw size={14} /> Reset demo
        </button>
      </div>
    </header>
  );
}
