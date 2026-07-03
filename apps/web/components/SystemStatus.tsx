import { API_URL } from "@/lib/api";

async function getHealth() {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function SystemStatus() {
  const health = await getHealth();
  return (
    <aside className="card">
      <div className="eyebrow">Runtime status</div>
      <h2>Stack readiness</h2>
      <p>Docker Compose boots the web app, FastAPI, worker, Postgres, and Redis.</p>
      <div className="messages">
        <div className="message assistant">
          <div className="label">API</div>
          <pre>{JSON.stringify(health ?? { status: "offline", hint: "Start docker compose" }, null, 2)}</pre>
        </div>
        <div className="message">
          <div className="label">Services</div>
          <p className="badge">Hermes control plane</p>{" "}
          <p className="badge">CrewAI-ready worker</p>{" "}
          <p className="badge">AG-UI stream</p>{" "}
          <p className="badge">A2A card</p>
        </div>
      </div>
    </aside>
  );
}
