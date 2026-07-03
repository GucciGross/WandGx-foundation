import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Hermes Agent Starter",
  description: "Hermes control plane + CrewAI runtime starter for agent-first apps",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="shell">
          <nav className="nav">
            <Link className="brand" href="/">
              <span className="logo">H</span>
              <span>Hermes Agent Starter</span>
            </Link>
            <div className="navlinks">
              <Link href="/admin/hermes">Hermes Admin</Link>
              <Link href="/app/support">Product Copilot</Link>
              <a href="http://localhost:8000/docs">API Docs</a>
            </div>
          </nav>
          {children}
        </main>
      </body>
    </html>
  );
}
