import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "./api.js";
import TopBar from "./components/TopBar.jsx";
import StepCard from "./components/StepCard.jsx";
import UploadStep from "./components/UploadStep.jsx";
import IdeaStep from "./components/IdeaStep.jsx";
import AskStep from "./components/AskStep.jsx";
import GraphView from "./components/GraphView.jsx";
import InsightPanel from "./components/InsightPanel.jsx";

export const STEPS = [
  { n: 1, title: "Add new papers", sub: "Grow the knowledge graph from PDFs" },
  { n: 2, title: "Check your research idea", sub: "Is it new? Where is the gap?" },
  { n: 3, title: "Ask the graph", sub: "Approaches, limitations, who fixed them" },
];

export default function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);

  const [activeStep, setActiveStep] = useState(1);
  const [done, setDone] = useState({ 1: false, 2: false, 3: false });

  const [novelty, setNovelty] = useState(null);
  const [answer, setAnswer] = useState(null);
  const [panelView, setPanelView] = useState("overview");
  const [highlight, setHighlight] = useState([]);
  const [newNodes, setNewNodes] = useState(new Set());
  const [newLinks, setNewLinks] = useState(new Set());
  const [toast, setToast] = useState(null);
  const positions = useRef(new Map());
  const toastTimer = useRef(null);

  const refresh = useCallback(async () => {
    const [g, s] = await Promise.all([api.graph(), api.stats()]);
    // keep existing node positions so the layout doesn't jump after an upload
    g.nodes.forEach((n) => {
      const p = positions.current.get(n.id);
      if (p) Object.assign(n, p);
    });
    setGraph(g);
    setStats(s);
  }, []);

  // Keep retrying until the backend and Neo4j answer (e.g. backend restarting, Aura waking up).
  useEffect(() => {
    let timer;
    let stopped = false;
    const load = async () => {
      try {
        const h = await api.health();
        setHealth(h);
        if (!h.neo4j) throw new Error("Neo4j not reachable yet");
        await refresh();
      } catch {
        setHealth((prev) => (prev?.neo4j ? prev : { neo4j: false, openai_key: prev?.openai_key ?? false }));
        if (!stopped) timer = setTimeout(load, 3000);
      }
    };
    load();
    return () => {
      stopped = true;
      clearTimeout(timer);
    };
  }, [refresh]);

  const showToast = (text) => {
    setToast(text);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(null), 5000);
  };

  const completeStep = (n) => {
    setDone((d) => ({ ...d, [n]: true }));
    setActiveStep((cur) => (cur === n && n < 3 ? n + 1 : cur));
  };

  const onUploaded = async (res) => {
    if (res.status !== "ingested") return;
    setNewNodes((prev) => new Set([...prev, ...res.new_nodes, `Paper:${res.paper.id}`]));
    setNewLinks((prev) => new Set([...prev, ...res.new_links.map((l) => `${l.source}|${l.target}|${l.type}`)]));
    showToast(
      res.paper.filled_stub
        ? `${res.paper.id} added — ${res.citations_lit_up} existing citations connected`
        : `${res.paper.id} added — linked to ${res.references.filter((r) => r.matched_id).length} papers it cites`
    );
    await refresh();
  };

  const onUploadsFinished = (anySuccess) => {
    if (anySuccess) completeStep(1);
  };

  const onNovelty = (r) => {
    setNovelty(r);
    setHighlight(r.highlight_nodes ?? []);
    setPanelView("novelty");
    completeStep(2);
  };

  const onAnswer = (r) => {
    setAnswer(r);
    setHighlight(r.highlight_nodes ?? []);
    setPanelView("answers");
    completeStep(3);
  };

  const onReset = async () => {
    if (!window.confirm("Remove all live-uploaded papers and restore the starting graph?")) return;
    await api.resetDemo();
    setNewNodes(new Set());
    setNewLinks(new Set());
    setNovelty(null);
    setAnswer(null);
    setHighlight([]);
    setPanelView("overview");
    setDone({ 1: false, 2: false, 3: false });
    setActiveStep(1);
    await refresh();
  };

  const stepState = (n) => (activeStep === n ? "active" : done[n] ? "done" : "idle");

  return (
    <div className="app">
      <TopBar
        steps={STEPS}
        stepState={stepState}
        onStep={setActiveStep}
        health={health}
        onReset={onReset}
      />

      <main className="layout">
        <aside className="rail">
          <StepCard
            step={STEPS[0]}
            state={stepState(1)}
            complete={done[1]}
            badge={done[1] ? "Next" : "Start here"}
            summary={done[1] ? "Papers added — the graph grew. Add more any time." : "Add the 3 sample papers or drop a PDF."}
            onOpen={() => setActiveStep(1)}
          >
            <UploadStep onUploaded={onUploaded} onFinished={onUploadsFinished} glow={stepState(1) === "active"} />
          </StepCard>

          <StepCard
            step={STEPS[1]}
            state={stepState(2)}
            complete={done[2]}
            badge="Next"
            summary={novelty ? `Verdict: ${novelty.verdict} · closest paper covers ${Math.round(novelty.best_coverage * 100)}%` : "Describe an idea and get a novelty verdict."}
            onOpen={() => setActiveStep(2)}
          >
            <IdeaStep onResult={onNovelty} glow={stepState(2) === "active"} />
          </StepCard>

          <StepCard
            step={STEPS[2]}
            state={stepState(3)}
            complete={done[3]}
            badge="Next"
            summary={answer ? "Answer shown on the right; the path is highlighted." : "Ask about approaches, limitations and fixes."}
            onOpen={() => setActiveStep(3)}
          >
            <AskStep onResult={onAnswer} glow={stepState(3) === "active"} />
          </StepCard>
        </aside>

        <section className="stage">
          <GraphView
            data={graph}
            newNodes={newNodes}
            newLinks={newLinks}
            highlight={new Set(highlight)}
            onClearHighlight={() => setHighlight([])}
            onLayout={(nodes) => nodes.forEach((n) => positions.current.set(n.id, { x: n.x, y: n.y }))}
          />
          {toast && <div className="toast glass">{toast}</div>}
        </section>

        <aside className="insights">
          <InsightPanel
            view={panelView}
            onView={setPanelView}
            stats={stats}
            novelty={novelty}
            answer={answer}
          />
        </aside>
      </main>
    </div>
  );
}
