import { useState } from "react";
import { ArrowRight, LoaderCircle, MessageSquareText, Send } from "lucide-react";
import { api } from "../api.js";

const SUGGESTIONS = [
  "Which approaches to reducing hallucination have been explored, what are their limitations, and which papers address them?",
  "Which methods have been evaluated on MedQA?",
  "Who has co-authored with Daniel Osei?",
];

export default function AskStep({ onResult, glow }) {
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const run = async (q) => {
    if (!q.trim()) return;
    setQuestion(q);
    setBusy(true);
    setError("");
    try {
      onResult({ question: q, ...(await api.ask(q)) });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="chips">
        {SUGGESTIONS.map((s, i) => (
          <button
            key={s}
            className={`chip ${glow && i === 0 && !busy ? "glow-target" : ""}`}
            onClick={() => run(s)}
            disabled={busy}
          >
            {i === 0 ? <ArrowRight size={13} /> : <MessageSquareText size={13} />}
            {s}
          </button>
        ))}
      </div>
      <form
        className="ask-row"
        onSubmit={(e) => {
          e.preventDefault();
          run(question);
        }}
      >
        <input
          className="ask-input"
          placeholder="Or ask your own question…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button className="btn primary icon" disabled={busy || !question.trim()} aria-label="Ask">
          {busy ? <LoaderCircle size={16} className="spin" /> : <Send size={16} />}
        </button>
      </form>
      {busy && <p className="progress-text"><LoaderCircle size={13} className="spin" /> The agent is querying the graph…</p>}
      {error && <p style={{ color: "var(--red)", fontSize: 12 }}>{error}</p>}
    </>
  );
}
