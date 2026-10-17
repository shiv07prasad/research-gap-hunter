import { useEffect, useMemo, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { Maximize2, Minus, Plus } from "lucide-react";

const COLORS = {
  Paper: "#4fd1c5",
  Stub: "#7f9c99",
  Author: "#ff8a65",
  Institution: "#c9875a",
  Venue: "#8c9c9a",
  Method: "#7ef0d8",
  Dataset: "#f17ab8",
  Task: "#f5b14a",
  Limitation: "#b794ff",
};
const GOLD = "#f2c46d";

const LAYERS = [
  { id: "papers", label: "Papers", labels: ["Paper"], color: COLORS.Paper },
  { id: "knowledge", label: "Concepts", labels: ["Method", "Dataset", "Task"], color: COLORS.Method },
  { id: "limitations", label: "Limitations", labels: ["Limitation"], color: COLORS.Limitation },
  { id: "people", label: "People", labels: ["Author", "Institution"], color: COLORS.Author },
];

const KIND = {
  Paper: "Paper", Method: "Method", Dataset: "Dataset", Task: "Concept / task",
  Limitation: "Limitation", Author: "Author", Institution: "Institution", Venue: "Venue",
};

const endId = (x) => (typeof x === "object" ? x.id : x);
const linkKey = (l) => `${endId(l.source)}|${endId(l.target)}|${l.type}`;

export default function GraphView({ data, newNodes, newLinks, highlight, onClearHighlight, onLayout }) {
  const wrapRef = useRef(null);
  const fgRef = useRef(null);
  const [size, setSize] = useState({ width: 800, height: 600 });
  const [on, setOn] = useState({ papers: true, knowledge: true, limitations: true, people: false });
  const [hover, setHover] = useState(null);

  useEffect(() => {
    const el = wrapRef.current;
    const ro = new ResizeObserver(([e]) => setSize({ width: e.contentRect.width, height: e.contentRect.height }));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const visible = useMemo(() => {
    const labels = new Set(LAYERS.filter((l) => on[l.id]).flatMap((l) => l.labels));
    const nodes = data.nodes.filter((n) => labels.has(n.label));
    const ids = new Set(nodes.map((n) => n.id));
    const links = data.links
      .map((l) => ({ ...l, source: endId(l.source), target: endId(l.target) }))
      .filter((l) => ids.has(l.source) && ids.has(l.target));
    return { nodes, links };
  }, [data, on]);

  const counts = useMemo(() => {
    const c = {};
    data.nodes.forEach((n) => (c[n.label] = (c[n.label] ?? 0) + 1));
    return c;
  }, [data]);

  const maxPr = useMemo(
    () => Math.max(1e-9, ...data.nodes.filter((n) => n.label === "Paper").map((n) => n.pagerank ?? 0)),
    [data]
  );
  const hasHighlight = highlight.size > 0;

  const drawNode = (node, ctx, scale) => {
    // a node can be painted before the layout has given it a position; skip it this frame
    if (!Number.isFinite(node.x) || !Number.isFinite(node.y)) return;
    const isPaper = node.label === "Paper";
    const r = isPaper ? 3.5 + 7 * Math.sqrt((node.pagerank ?? 0) / maxPr) : node.label === "Limitation" ? 2.6 : 2.2;
    const isNew = newNodes.has(node.id);
    const lit = highlight.has(node.id);
    const dim = hasHighlight && !lit && !isNew;
    const color = isPaper && node.is_stub ? COLORS.Stub : COLORS[node.label] ?? "#999";
    ctx.globalAlpha = dim ? 0.14 : 1;

    if (isNew) {
      const pulse = 1 + 0.4 * Math.sin(Date.now() / 260);
      const g = ctx.createRadialGradient(node.x, node.y, r * 0.5, node.x, node.y, r * 3 * pulse);
      g.addColorStop(0, "rgba(242,196,109,0.55)");
      g.addColorStop(1, "rgba(242,196,109,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(node.x, node.y, r * 3 * pulse, 0, 2 * Math.PI);
      ctx.fill();
    }

    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    if (isPaper && node.is_stub) {
      ctx.setLineDash([1.6, 1.6]);
      ctx.strokeStyle = COLORS.Stub;
      ctx.lineWidth = 1.2;
      ctx.stroke();
      ctx.setLineDash([]);
    } else {
      ctx.shadowColor = color;
      ctx.shadowBlur = lit || isNew ? 18 : isPaper ? 10 : 6;
      const g = ctx.createRadialGradient(node.x - r / 3, node.y - r / 3, r / 6, node.x, node.y, r);
      g.addColorStop(0, "#ffffff");
      g.addColorStop(0.25, color);
      g.addColorStop(1, shade(color));
      ctx.fillStyle = g;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
    if (lit) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, r + 2.2, 0, 2 * Math.PI);
      ctx.strokeStyle = GOLD;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    const showLabel = isPaper || lit || isNew || scale > 2.2;
    if (showLabel) {
      const text = isPaper ? node.key : truncate(node.name, 34);
      const fontSize = Math.max((isPaper ? 9.5 : 8.5) / scale, isPaper ? 2.6 : 2.2);
      ctx.font = `${isPaper ? 600 : 400} ${fontSize}px Inter, system-ui, sans-serif`;
      ctx.textAlign = "center";
      ctx.textBaseline = "top";
      ctx.fillStyle = lit || isNew ? "#fbe7bd" : isPaper ? "#d7ece9" : "rgba(215,236,233,0.75)";
      ctx.fillText(text, node.x, node.y + r + 2);
    }
    ctx.globalAlpha = 1;
  };

  const linkColor = (l) => {
    if (newLinks.has(linkKey(l))) return "rgba(242,196,109,0.95)";
    const both = highlight.has(endId(l.source)) && highlight.has(endId(l.target));
    if (hasHighlight && !both) return "rgba(126,240,216,0.035)";
    if (both) return "rgba(242,196,109,0.75)";
    if (l.type === "CITES") return "rgba(126,240,216,0.42)";
    if (l.type === "HAS_LIMITATION" || l.type === "RESOLVES") return "rgba(183,148,255,0.35)";
    return "rgba(126,240,216,0.13)";
  };

  const zoom = (f) => {
    const fg = fgRef.current;
    if (fg) fg.zoom(fg.zoom() * f, 300);
  };

  return (
    <div className="graph-wrap" ref={wrapRef}>
      <div className="stage-toolbar">
        <div className="toolbar-group glass">
          {LAYERS.map((l) => (
            <button key={l.id} className={`layer ${on[l.id] ? "on" : ""}`} onClick={() => setOn({ ...on, [l.id]: !on[l.id] })}>
              <span className="dot" style={{ background: l.color, boxShadow: `0 0 8px ${l.color}` }} />
              {l.label}
              <span className="muted mono">{l.labels.reduce((t, x) => t + (counts[x] ?? 0), 0)}</span>
            </button>
          ))}
        </div>
        <div className="toolbar-group glass">
          <button className="tool" onClick={() => zoom(1.3)} aria-label="Zoom in"><Plus size={15} /></button>
          <button className="tool" onClick={() => zoom(1 / 1.3)} aria-label="Zoom out"><Minus size={15} /></button>
          <button className="tool" onClick={() => fgRef.current?.zoomToFit(500, 50)} aria-label="Fit"><Maximize2 size={14} /></button>
        </div>
      </div>

      {hasHighlight && (
        <button className="stage-hint glass" onClick={onClearHighlight}>
          Showing the evidence path · click to show the whole graph
        </button>
      )}

      {hover && (
        <div className="node-card glass">
          <div className="kind">{hover.label === "Paper" && hover.is_stub ? "Paper · cited, not read yet" : KIND[hover.label]}</div>
          <strong>{hover.label === "Paper" ? `${hover.key} — ${hover.name}` : hover.name}</strong>
          {hover.year && <span className="muted">{hover.year}</span>}
        </div>
      )}

      <div className="stage-legend glass">
        <span><i style={{ background: COLORS.Paper }} />Paper</span>
        <span><i className="ring" />Cited, not read</span>
        <span><i style={{ background: COLORS.Method }} />Method</span>
        <span><i style={{ background: COLORS.Dataset }} />Dataset</span>
        <span><i style={{ background: COLORS.Task }} />Concept</span>
        <span><i style={{ background: COLORS.Limitation }} />Limitation</span>
        <span><i style={{ background: GOLD, boxShadow: `0 0 6px ${GOLD}` }} />Just added / evidence</span>
      </div>

      <ForceGraph2D
        ref={fgRef}
        width={size.width}
        height={size.height}
        graphData={visible}
        backgroundColor="rgba(0,0,0,0)"
        nodeId="id"
        nodeCanvasObject={drawNode}
        nodePointerAreaPaint={(node, color, ctx) => {
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(node.x, node.y, 7, 0, 2 * Math.PI);
          ctx.fill();
        }}
        linkColor={linkColor}
        linkWidth={(l) => (newLinks.has(linkKey(l)) ? 2.2 : l.type === "CITES" ? 0.9 : 0.5)}
        linkCurvature={(l) => (l.type === "CITES" ? 0.18 : 0.08)}
        linkDirectionalArrowLength={(l) => (l.type === "CITES" ? 2.6 : 0)}
        linkDirectionalArrowRelPos={0.92}
        linkDirectionalArrowColor={linkColor}
        linkDirectionalParticles={(l) => (newLinks.has(linkKey(l)) ? 3 : 0)}
        linkDirectionalParticleWidth={2.4}
        linkDirectionalParticleColor={() => GOLD}
        d3VelocityDecay={0.3}
        cooldownTicks={140}
        autoPauseRedraw={false}
        onEngineStop={() => onLayout?.(visible.nodes)}
        onNodeHover={setHover}
        onBackgroundClick={() => hasHighlight && onClearHighlight?.()}
      />
    </div>
  );
}

function shade(hex) {
  const n = parseInt(hex.slice(1), 16);
  const f = (v) => Math.round(v * 0.45);
  return `rgb(${f(n >> 16)}, ${f((n >> 8) & 255)}, ${f(n & 255)})`;
}

function truncate(s, n) {
  return s && s.length > n ? `${s.slice(0, n - 1)}…` : s ?? "";
}
