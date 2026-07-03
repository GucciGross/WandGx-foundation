"use client";

// Optional drop-in once your CopilotKit runtime is configured.
// The current CopilotKit docs show CopilotChat as a prebuilt chat component.
// Keep this as an example so the starter's default UI stays dependency-resilient.

import { CopilotChat } from "@copilotkit/react-core/v2";

export function CopilotKitWidgetExample() {
  return (
    <CopilotChat
      labels={{
        modalHeaderTitle: "Product assistant",
        welcomeMessageText: "What should we work on?",
      }}
    />
  );
}
