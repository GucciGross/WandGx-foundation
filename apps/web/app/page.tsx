import Link from "next/link";
import { SystemStatus } from "@/components/SystemStatus";

export default function HomePage() {
  return (
    <div className="hero">
      <section className="card">
        <div className="eyebrow">Agent-first SaaS foundation</div>
        <h1>Clone once. Build agent apps forever.</h1>
        <p>
          Hermes is the builder and guardian. CrewAI is the runtime workforce.
          AG-UI streams connect agents to the product UI, while A2A makes Hermes discoverable.
        </p>
        <div className="actions">
          <Link className="btn" href="/admin/hermes">Start with Hermes</Link>
          <Link className="btn secondary" href="/app/support">Try product copilot</Link>
        </div>
        <div className="grid">
          <div className="stat"><strong>2</strong><span>agent surfaces</span></div>
          <div className="stat"><strong>1</strong><span>CrewAI template</span></div>
          <div className="stat"><strong>∞</strong><span>generated crews</span></div>
        </div>
      </section>
      <SystemStatus />
    </div>
  );
}
