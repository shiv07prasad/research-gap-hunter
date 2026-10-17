import { useEffect, useState } from "react";
import { LoaderCircle, Sparkles } from "lucide-react";
import { api } from "../api.js";

const EXAMPLE =
  "Use knowledge graphs to reduce hallucinations of small language models in medical question answering, evaluated on MedQA.";

const PHASES = [
  "Breaking the idea into components…",
  "Finding similar papers (vector search)…",
  "Walking citations and shared methods…",
  "Comparing papers component by component…",
];

export default function IdeaStep({ onResult, glow }) {
  const [idea, setIdea] = useState(EXAMPLE);
  const [busy, setBusy] = useState(false);
  const [phase, setPhase] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!busy) return;
    setPhase(0);
    const t = setInterval(() => setPhase((p) => Math.min(p + 1, PHASES.length - 1)), 900);
    return () => clearInterval(t);
  }, [busy]);

  const run = async () => {
    setBusy(true);
    setError("");
    try {
      onResult(await api.novelty(idea));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <textarea className="textarea" rows={4} value={idea} onChange={(e) => setIdea(e.target.value)} />
      <button className={`btn primary block ${glow && !busy ? "glow-target" : ""}`} disabled={busy || !idea.trim()} onClick={run}>
        {busy ? <LoaderCircle size={15} className="spin" /> : <Sparkles size={15} />}
        {busy ? "Searching the graph…" : "Check novelty"}
      </button>
      {busy && <p className="progress-text">{PHASES[phase]}</p>}
      {error && <p style={{ color: "var(--red)", fontSize: 12 }}>{error}</p>}
      <p className="muted" style={{ fontSize: 11 }}>
        Tip: run this before and after adding the papers in step 1 — the answer changes as the graph grows.
      </p>
    </>
  );
}
