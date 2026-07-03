import { ProductCopilot } from "@/components/ProductCopilot";

export default function SupportPage() {
  return (
    <section className="card">
      <div className="eyebrow">User-facing runtime</div>
      <h1>Product Copilot</h1>
      <p>
        This is the customer/user surface. It streams AG-UI-style events from the
        backend and can be swapped for CopilotKit components as the product matures.
      </p>
      <ProductCopilot />
    </section>
  );
}
