"use client";

import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string>("");

  const ping = async () => {
    setLoading(true);
    setResult("");

    try {
      const base = process.env.NEXT_PUBLIC_API_BASE_URL;
      if (!base) throw new Error("NEXT_PUBLIC_API_BASE_URL is not set");

      const res = await fetch(`${base}/health`);
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);

      const data = await res.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (err: any) {
      setResult(err?.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: 24, fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: 24, fontWeight: 700 }}>Grillz</h1>
      <p style={{ marginTop: 8 }}>Backend smoke test:</p>

      <button
        onClick={ping}
        disabled={loading}
        style={{
          marginTop: 12,
          padding: "10px 14px",
          borderRadius: 10,
          border: "1px solid #ccc",
          cursor: loading ? "not-allowed" : "pointer",
        }}
      >
        {loading ? "Pinging..." : "Ping backend (/health)"}
      </button>

      <pre
        style={{
          marginTop: 16,
          padding: 12,
          borderRadius: 10,
          background: "#f6f6f6",
          overflowX: "auto",
          color: "black",
        }}
      >
        {result || "—"}
      </pre>
    </main>
  );
}

