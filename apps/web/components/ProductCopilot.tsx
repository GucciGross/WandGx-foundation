"use client";

import { useRef, useState } from "react";
import { API_URL, postJson } from "@/lib/api";

type Message = { role: "user" | "assistant"; content: string; runId?: string };

export function ProductCopilot() {
  const [input, setInput] = useState("What can this app do?");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "I am the product copilot. Ask a user-facing question." },
  ]);
  const [streaming, setStreaming] = useState(false);
  const activeRunId = useRef<string | undefined>(undefined);

  function stream() {
    const message = input.trim();
    if (!message || streaming) return;
    setInput("");
    setStreaming(true);
    setMessages((prev) => [...prev, { role: "user", content: message }, { role: "assistant", content: "" }]);

    const source = new EventSource(`${API_URL}/agui/stream?message=${encodeURIComponent(message)}`);
    source.addEventListener("RUN_STARTED", (event) => {
      const payload = JSON.parse((event as MessageEvent).data);
      activeRunId.current = payload.run_id;
    });
    source.addEventListener("TEXT_MESSAGE_CONTENT", (event) => {
      const payload = JSON.parse((event as MessageEvent).data);
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        next[next.length - 1] = { ...last, content: `${last.content}${payload.delta}`, runId: activeRunId.current };
        return next;
      });
    });
    source.addEventListener("RUN_FINISHED", () => {
      setStreaming(false);
      source.close();
    });
    source.onerror = () => {
      setStreaming(false);
      source.close();
    };
  }

  async function feedback(rating: "good" | "bad") {
    const last = [...messages].reverse().find((msg) => msg.role === "assistant");
    await postJson("/feedback", {
      run_id: last?.runId,
      agent_id: "product_copilot",
      rating,
      comment: rating === "good" ? "Useful response" : "Needs improvement",
      snapshot: { last_message: last?.content },
    });
  }

  return (
    <div className="console">
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="label">{message.role}</div>
            <div>{message.content || "..."}</div>
          </div>
        ))}
      </div>
      <div className="inputrow">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask the product copilot..."
          onKeyDown={(event) => {
            if (event.key === "Enter") stream();
          }}
        />
        <button className="btn" onClick={stream} disabled={streaming}>
          {streaming ? "Streaming" : "Send"}
        </button>
      </div>
      <div className="actions">
        <button className="btn secondary" onClick={() => void feedback("good")}>Thumbs up</button>
        <button className="btn secondary" onClick={() => void feedback("bad")}>Thumbs down</button>
      </div>
    </div>
  );
}
