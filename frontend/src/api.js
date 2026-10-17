async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, options);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {
      /* not JSON */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json();
}

const postJson = (path, body) =>
  request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

export const api = {
  health: () => request("/health"),
  stats: () => request("/stats"),
  graph: () => request("/graph"),
  novelty: (idea) => postJson("/novelty", { idea }),
  ask: (question) => postJson("/ask", { question }),
  resetDemo: () => request("/reset-demo", { method: "POST" }),
  samples: () => request("/samples"),
  uploadSample: (file) => request(`/upload-sample/${encodeURIComponent(file)}`, { method: "POST" }),
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/upload", { method: "POST", body: form });
  },
};
