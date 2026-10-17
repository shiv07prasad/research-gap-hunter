import { useEffect, useRef, useState } from "react";
import { CircleCheck, FileText, LoaderCircle, Plus, Upload } from "lucide-react";
import { api } from "../api.js";

export default function UploadStep({ onUploaded, onFinished, glow }) {
  const inputRef = useRef(null);
  const [samples, setSamples] = useState([]);
  const [working, setWorking] = useState({}); // file -> true while uploading
  const [events, setEvents] = useState([]);
  const [dragging, setDragging] = useState(false);
  const busy = Object.values(working).some(Boolean);

  const loadSamples = () => api.samples().then(setSamples);
  // retry until the backend is up (it may still be starting when the page loads)
  useEffect(() => {
    let timer;
    const tryLoad = () => loadSamples().catch(() => (timer = setTimeout(tryLoad, 3000)));
    tryLoad();
    return () => clearTimeout(timer);
  }, []);

  // Runs uploads one after another so each one's new nodes animate separately.
  const runAll = async (jobs) => {
    let anySuccess = false;
    for (const { key, label, call } of jobs) {
      setWorking((w) => ({ ...w, [key]: true }));
      setEvents((ev) => [{ key, state: "working", title: label, text: "Reading PDF, extracting entities, linking citations…" }, ...ev.filter((e) => e.key !== key)]);
      try {
        const res = await call();
        anySuccess ||= res.status === "ingested";
        setSamples((list) => list.map((s) => (s.file === key ? { ...s, in_graph: true } : s)));
        setEvents((ev) => ev.map((e) => (e.key === key ? { ...e, state: "done", title: res.paper?.id ?? label, text: describe(res) } : e)));
        await onUploaded(res);
      } catch (err) {
        setEvents((ev) => ev.map((e) => (e.key === key ? { ...e, state: "error", text: err.message } : e)));
      } finally {
        setWorking((w) => ({ ...w, [key]: false }));
      }
    }
    await loadSamples().catch(() => {});
    onFinished(anySuccess);
  };

  const pending = samples.filter((s) => !s.in_graph);
  const addSamples = (list) =>
    runAll(list.map((s) => ({ key: s.file, label: s.file, call: () => api.uploadSample(s.file) })));
  const addFiles = (files) =>
    runAll(
      [...files]
        .filter((f) => f.name.toLowerCase().endsWith(".pdf"))
        .map((f) => ({ key: f.name, label: f.name, call: () => api.upload(f) }))
    );

  return (
    <>
      <p className="muted" style={{ fontSize: 12 }}>
        Three papers were just "published". Add them and watch the graph connect them to existing work.
      </p>

      <div className="sample-list">
        {samples.map((s) => (
          <div className="sample" key={s.file}>
            <span className="sample-icon"><FileText size={16} /></span>
            <span className="sample-text">
              <strong>{s.file}</strong>
              <span title={s.title}>{s.title}</span>
            </span>
            {working[s.file] ? (
              <span className="state busy"><LoaderCircle size={13} className="spin" /> adding</span>
            ) : s.in_graph ? (
              <span className="state ok"><CircleCheck size={13} /> in graph</span>
            ) : (
              <button className="btn sm" disabled={busy} onClick={() => addSamples([s])}>
                <Plus size={13} /> Add
              </button>
            )}
          </div>
        ))}
      </div>

      {pending.length > 0 && (
        <button className={`btn primary block ${glow && !busy ? "glow-target" : ""}`} disabled={busy} onClick={() => addSamples(pending)}>
          {busy ? <LoaderCircle size={15} className="spin" /> : <Upload size={15} />}
          {busy ? "Adding papers…" : `Add ${pending.length === samples.length ? "all " : ""}${pending.length} sample paper${pending.length > 1 ? "s" : ""}`}
        </button>
      )}

      <div
        className={`dropzone ${dragging ? "dragging" : ""}`}
        onClick={() => !busy && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!busy) addFiles(e.dataTransfer.files);
        }}
      >
        <Upload size={14} /> or drop your own PDF here
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          multiple
          hidden
          onChange={(e) => {
            addFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </div>

      {events.length > 0 && (
        <div className="event-log">
          {events.map((e) => (
            <div key={e.key} className={`event ${e.state}`}>
              <strong>{e.title}</strong>
              {e.text}
            </div>
          ))}
        </div>
      )}
    </>
  );
}

function describe(res) {
  if (res.status === "exists") return "Already in the graph.";
  const parts = [];
  if (res.paper.filled_stub) parts.push(`Was cited but unread — ${res.citations_lit_up} citations now connected`);
  else parts.push("New paper added");
  const matched = res.references.filter((r) => r.matched_id).length;
  parts.push(`${matched}/${res.references.length} references linked`);
  const n = ["proposes", "uses", "datasets", "tasks"].reduce((t, k) => t + (res.extracted[k]?.length ?? 0), 0);
  parts.push(`${n} methods/concepts, ${res.extracted.limitations?.length ?? 0} limitations`);
  return parts.join(" · ");
}
