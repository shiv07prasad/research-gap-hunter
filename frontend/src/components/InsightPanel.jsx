import {
  BookOpen,
  Check,
  CircleDot,
  FileText,
  GitBranch,
  Layers,
  Lightbulb,
  MessageSquareText,
  Minus,
  Network,
  Sparkles,
  Target,
  TriangleAlert,
  Users,
  X,
} from "lucide-react";

const VERDICT = {
  exists: { label: "Already exists", cls: "exists" },
  partial: { label: "Partially exists", cls: "partial" },
  novel: { label: "Looks novel", cls: "novel" },
};

export default function InsightPanel({ view, onView, stats, novelty, answer }) {
  const tabs = [
    { id: "overview", label: "Overview", icon: Network, enabled: true },
    { id: "novelty", label: "Novelty", icon: Sparkles, enabled: !!novelty },
    { id: "answers", label: "Answers", icon: MessageSquareText, enabled: !!answer },
  ];
  return (
    <div className="panel">
      <div className="panel-tabs">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`panel-tab ${view === t.id ? "on" : ""}`}
            disabled={!t.enabled}
            onClick={() => onView(t.id)}
          >
            <t.icon size={14} /> {t.label}
          </button>
        ))}
      </div>
      <div className="panel-body">
        {view === "novelty" && novelty ? (
          <NoveltyView r={novelty} />
        ) : view === "answers" && answer ? (
          <AnswerView a={answer} />
        ) : (
          <Overview stats={stats} />
        )}
      </div>
    </div>
  );
}

/* ---------- overview ---------- */

function Overview({ stats }) {
  const c = stats?.counts ?? {};
  const papers = (c.Paper ?? 0) - (stats?.stubs ?? 0);
  const concepts = (c.Method ?? 0) + (c.Dataset ?? 0) + (c.Task ?? 0);
  const top = stats?.top_papers ?? [];
  const maxPr = Math.max(1e-9, ...top.map((p) => p.pagerank));

  return (
    <>
      <div className="eyebrow"><Network size={14} /> Knowledge graph · Neo4j</div>
      <h2 className="panel-title">
        Research on <strong>LLM hallucination</strong>, knowledge graphs and small models
      </h2>

      <div className="tiles">
        <Tile icon={FileText} num={papers} label="Papers read" />
        <Tile icon={CircleDot} num={stats?.stubs ?? 0} label="Cited but not yet read" cls="warn" />
        <Tile icon={Layers} num={concepts} label="Methods, datasets, concepts" />
        <Tile icon={TriangleAlert} num={c.Limitation ?? 0} label="Limitations found" cls="violet" />
      </div>

      <div className="section">
        <div className="section-title"><GitBranch size={14} /> Most influential papers (PageRank)</div>
        {top.map((p) => (
          <div className="rank-row" key={p.id} title={p.title}>
            <span className="mono">{p.id}{p.is_stub ? "*" : ""}</span>
            <span className="rank-bar"><i style={{ width: `${(p.pagerank / maxPr) * 100}%` }} /></span>
            <span className="mono muted">{p.cited_by} cites</span>
          </div>
        ))}
        {top.some((p) => p.is_stub) && <p className="muted" style={{ fontSize: 11 }}>* cited by others but its text is not in the graph yet</p>}
      </div>

      <div className="section">
        <div className="section-title"><Lightbulb size={14} /> How to use this demo</div>
        <ol className="howto">
          <li>Add the sample papers — watch new nodes and citations light up in gold.</li>
          <li>Check a research idea — get a verdict, a coverage matrix and the exact gap.</li>
          <li>Ask the graph — approaches, their limitations and which papers fixed them.</li>
        </ol>
      </div>
    </>
  );
}

function Tile({ icon: Icon, num, label, cls = "" }) {
  return (
    <div className={`tile ${cls}`}>
      <div className="tile-top"><Icon size={16} /><span className="num mono">{num}</span></div>
      <div className="label">{label}</div>
    </div>
  );
}

/* ---------- novelty ---------- */

const CELL = { yes: Check, partial: Minus, no: X };

function NoveltyView({ r }) {
  const v = VERDICT[r.verdict] ?? VERDICT.novel;
  const labels = r.components.map((c) => c.label);
  const gaps = r.graph_gaps;
  const openWeak = r.weaknesses.filter((w) => w.resolved_by.length === 0);
  const pct = Math.round((r.best_coverage ?? 0) * 100);

  return (
    <>
      <div className="eyebrow"><Sparkles size={14} /> Novelty check</div>
      <h2 className="panel-title" style={{ fontSize: 16 }}>{r.idea}</h2>

      <div className={`hero ${v.cls}`}>
        <div className="hero-top">
          <span>Closest existing work</span>
          <span className={`verdict-pill ${v.cls}`}>{v.label}</span>
        </div>
        <div className="hero-number">
          <span className="big mono">{pct}%</span>
          <span className="caption">of your idea is covered by the closest paper</span>
          <span className="bars" aria-hidden>
            {r.matrix.map((m) => <i key={m.paper_id} style={{ height: `${Math.max(8, m.coverage * 100)}%` }} />)}
          </span>
        </div>
      </div>

      <div className="tiles">
        <Tile icon={FileText} num={r.matrix.length} label="Closest papers compared" />
        <Tile icon={Target} num={gaps.never_combined.length} label="Combinations nobody tried" cls="warn" />
        <Tile icon={TriangleAlert} num={openWeak.length} label="Open weaknesses nearby" cls="violet" />
        <Tile icon={CircleDot} num={r.unread_stubs.length} label="Cited but unread papers" />
      </div>

      {(r.gap || gaps.never_combined.length > 0) && (
        <div className="gap-card">
          <div className="section-title" style={{ color: "var(--gold)", marginBottom: 6 }}><Target size={14} /> The gap</div>
          {r.gap && r.gap !== "none" && <p>{r.gap}</p>}
          {gaps.never_combined.length > 0 && (
            <ul className="gap-pairs">
              {gaps.never_combined.map((g) => (
                <li key={`${g.a}-${g.b}`}>No paper combines <b>{g.a}</b> + <b>{g.b}</b></li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="section">
        <div className="section-title"><Layers size={14} /> Coverage matrix</div>
        <div className="matrix-wrap">
          <table className="matrix">
            <thead>
              <tr>
                <th>Paper</th>
                {labels.map((l) => <th key={l}>{l}</th>)}
              </tr>
            </thead>
            <tbody>
              {r.matrix.map((row) => (
                <tr key={row.paper_id} title={`${row.title} — ${row.reasons.join(" · ")}`}>
                  <td>
                    <span className="pid">{row.paper_id}</span>{" "}
                    <span className="cov">{Math.round(row.coverage * 100)}%</span>
                  </td>
                  {labels.map((l) => {
                    const val = row.cells?.[l] ?? "no";
                    const Icon = CELL[val] ?? X;
                    return <td key={l}><span className={`cell ${val}`}><Icon size={12} /></span></td>;
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {r.summary && <p className="muted" style={{ fontSize: 12 }}>{r.summary}</p>}

      {r.weaknesses.length > 0 && (
        <div className="section">
          <div className="section-title"><TriangleAlert size={14} /> Weaknesses of the closest work</div>
          <ul className="list">
            {r.weaknesses.map((w) => (
              <li key={`${w.paper_id}-${w.limitation}`}>
                <b>{w.paper_id}</b> <span className="lim">{w.limitation}</span>{" "}
                {w.resolved_by.length ? <span className="fixed">→ fixed by {w.resolved_by.join(", ")}</span> : <span className="open">→ still open</span>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {r.unread_stubs.length > 0 && (
        <div className="section">
          <div className="section-title"><CircleDot size={14} /> Cited but not yet in the graph</div>
          <ul className="list">
            {r.unread_stubs.map((s) => (
              <li key={s.id}>
                {s.title}
                <span className="meta">cited by {s.cited_by} papers — add it in step 1 to analyse it</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {r.reading_path.length > 0 && (
        <div className="section">
          <div className="section-title"><BookOpen size={14} /> Reading path</div>
          <ul className="list">
            {r.reading_path.map((p, i) => (
              <li key={p.id}>
                {i + 1}. {p.title}
                <span className="meta">{p.year ?? "year unknown"}{p.is_stub ? " · not loaded yet" : ""}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {r.people.length > 0 && (
        <div className="section">
          <div className="section-title"><Users size={14} /> People to talk to</div>
          <p style={{ fontSize: 12, color: "var(--text-2)" }}>{r.people.join(" · ")}</p>
        </div>
      )}
    </>
  );
}

/* ---------- answers ---------- */

function AnswerView({ a }) {
  const paths = a.paths ?? [];
  return (
    <>
      <div className="eyebrow"><MessageSquareText size={14} /> Graph agent</div>
      <h2 className="panel-title" style={{ fontSize: 16 }}>{a.question}</h2>

      {paths.length > 0 && (
        <div className="section">
          <div className="section-title"><GitBranch size={14} /> Approach → limitation → fixed by</div>
          {paths.map((p) => (
            <div className="chain" key={p.paper_id}>
              <div className="chain-head">
                <span className="pid">{p.paper_id}</span>
                {p.approaches.map((x) => x.name).join(", ") || p.title}
                <span className="muted"> · {p.year}</span>
              </div>
              <ul>
                {p.limitations.map((l) => (
                  <li key={l.key}>
                    <span className="lim">{l.name}</span>
                    {l.resolved_by.length ? (
                      <span className="fixed">→ fixed by {l.resolved_by.map((f) => f.id).join(", ")}</span>
                    ) : (
                      <span className="open">→ still open</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      <details className="raw" open={paths.length === 0}>
        <summary>Agent's written answer</summary>
        <p>{a.answer}</p>
      </details>
      {a.trace?.length > 0 && (
        <details className="raw">
          <summary>{a.trace.length} graph queries the agent ran</summary>
          <pre>{a.trace.map((t) => `${t.tool}: ${t.args.query ?? t.args.topic ?? t.args.text}`).join("\n\n")}</pre>
        </details>
      )}
    </>
  );
}
