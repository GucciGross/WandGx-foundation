import { HermesConsole } from "@/components/HermesConsole";

export default function HermesAdminPage() {
  return (
    <section className="card">
      <div className="eyebrow">Control plane</div>
      <h1>Hermes Admin</h1>
      <p>
        Tell Hermes what app or crew to build. This console talks to the FastAPI
        control plane and returns manifests/actions before code is written.
      </p>
      <HermesConsole />
    </section>
  );
}
