"use client";

import { useState } from "react";
import { postJson } from "@/lib/api";

type ChatMessage = { role: "user" | "assistant"; content: string; artifact?: unknown };
type HermesAction = {
  type: string;
  title: string;
  description: string;
  payload: Record<string, unknown>;
  requires_approval: boolean;
};
type HermesChatResponse = {
  message: string;
  mode: "dormant" | "observe" | "guardian";
  actions: HermesAction[];
  artifacts: Record<string, unknown>;
};

export function HermesConsole() {
  const [input, setInput] = useState("Build a quote app for painting contractors");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "I am Hermes. Ask me to plan an app or create a CrewAI crew. I return manifests and approval-gated actions first.",
    },
  ]);

  async function send() {
    const message = input.trim();
    if (!message || busy) return;
    setBusy(true);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    try {
      const response = await postJson<HermesChatResponse>("/admin/hermes/chat", {
        message,
        context: {},
      });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.message,
          artifact: { actions: response.actions, artifacts: response.artifacts },
        },
      ]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "assistant", content: String(error) }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="console">
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="label">{message.role}</div>
            <div>{message.content}</div>
            {message.artifact ? <pre>{JSON.stringify(message.artifact, null, 2)}</pre> : null}
          </div>
        ))}
      </div>
      <div className="inputrow">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Create a lead intake crew..."
          onKeyDown={(event) => {
            if ((event.metaKey || event.ctrlKey) && event.key === "Enter") void send();
          }}
        />
        <button className="btn" onClick={() => void send()} disabled={busy}>
          {busy ? "Thinking" : "Send"}
        </button>
      </div>
    </div>
  );
}
