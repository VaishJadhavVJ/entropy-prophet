export const dynamic = "force-dynamic";

import { getPredictions } from "@/lib/predictions";
import HowItWorks from "@/components/HowItWorks";
import PredictionsTable from "@/components/PredictionsTable";
import EntropyBarChart from "@/components/EntropyBarChart";

const INK    = "#1f2421";
const INK_MID = "rgba(31,36,33,0.55)";
const TEAL   = "#216869";
const BORDER = "rgba(33,104,105,0.2)";
const MONO   = "var(--font-space-mono), 'Courier New', monospace";
const SERIF  = "var(--font-playfair), Georgia, serif";

export default async function Page() {
  const predictions = await getPredictions();
  const chartData = predictions.map(({ market_ticker, p_yes, entropy }) => ({
    ticker: market_ticker,
    p_yes,
    entropy,
  }));

  return (
    <div style={{ background: "#dce1de", color: INK, minHeight: "100vh" }}>

      {/* ─── Hero — graph paper on sage background ─── */}
      <header
        className="hero-graph"
        style={{ borderBottom: `1px solid ${BORDER}`, padding: "72px 24px 64px", textAlign: "center" }}
      >
        <div style={{ maxWidth: 680, margin: "0 auto" }}>
          <p style={{ fontFamily: MONO, fontSize: 11, letterSpacing: "0.2em", color: INK_MID, textTransform: "uppercase", marginBottom: 20 }}>
            Research instrument · GLM-5.1 · Entropy-Calibrated
          </p>

          <h1 style={{ fontFamily: SERIF, fontSize: "clamp(48px, 8vw, 80px)", fontWeight: 700, color: TEAL, letterSpacing: "-0.5px", lineHeight: 1.1, margin: 0 }}>
            Entropy Prophet
          </h1>

          <div style={{ width: 48, height: 2, background: TEAL, opacity: 0.4, margin: "20px auto" }} />

          <p style={{ fontFamily: "Georgia, serif", fontSize: 18, color: INK, lineHeight: 1.6, margin: 0 }}>
            Entropy-based calibration for LLM prediction market forecasting
          </p>

          <p style={{ fontFamily: MONO, fontSize: 12, color: INK_MID, lineHeight: 1.7, marginTop: 12 }}>
            LLM confidence ≠ market returns. Entropy detects when confidence is fake.
          </p>
        </div>
      </header>

      {/* ─── Main content ─── */}
      <main style={{ maxWidth: 960, margin: "0 auto", padding: "64px 24px", display: "flex", flexDirection: "column", gap: 72 }}>

        <HowItWorks />

        {/* Live Predictions */}
        <section>
          <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
            <div>
              <h2 style={{ fontFamily: SERIF, fontSize: 28, color: TEAL, margin: 0 }}>
                Live Predictions
              </h2>
              <p style={{ fontFamily: "Georgia, serif", fontSize: 13, color: INK_MID, margin: "4px 0 0" }}>
                {predictions.length} events &middot; last run{" "}
                <span style={{ fontFamily: MONO, fontSize: 12 }}>2026-06-01</span>
              </p>
            </div>
            <span className="rubber-stamp">{predictions.length} pending</span>
          </div>
          <PredictionsTable predictions={predictions} />
        </section>

        {/* Chart */}
        <section>
          <h2 style={{ fontFamily: SERIF, fontSize: 28, color: TEAL, margin: "0 0 6px" }}>
            P(yes) by Event
          </h2>
          <p style={{ fontFamily: "Georgia, serif", fontSize: 13, color: INK_MID, margin: "0 0 24px" }}>
            Pencil-filled bars show calibrated model confidence. Hover for entropy detail.
          </p>

          <div style={{ background: "#ffffff", border: `1.5px solid ${BORDER}`, boxShadow: "2px 4px 16px rgba(33,104,105,0.08)", padding: "24px 16px 8px" }}>
            <EntropyBarChart data={chartData} />
          </div>

          {/* Legend */}
          <div style={{ display: "flex", gap: 20, marginTop: 12, fontFamily: MONO, fontSize: 11, color: INK_MID }}>
            {[
              { label: "<40% confidence", spacing: "3px" },
              { label: "40–60%", spacing: "5px" },
              { label: ">60% confidence", spacing: "8px" },
            ].map(({ label, spacing }) => (
              <span key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{
                  display: "inline-block", width: 14, height: 11,
                  border: `1.5px solid #49a078`,
                  background: `repeating-linear-gradient(45deg, #49a078 0px, #49a078 1px, transparent 1px, transparent ${spacing})`,
                }} />
                {label}
              </span>
            ))}
          </div>
        </section>

      </main>

      {/* ─── Footer ─── */}
      <footer style={{ borderTop: `1px solid ${BORDER}`, padding: "28px 24px", textAlign: "center", fontFamily: "Georgia, serif", fontSize: 13, color: INK_MID }}>
        Built by{" "}
        <span style={{ color: TEAL, fontWeight: 600 }}>Vaish</span>
        {" · "}
        <span style={{ fontFamily: MONO, fontSize: 12 }}>entropy-prophet</span>
        {" · "}
        <span style={{ fontFamily: MONO, fontSize: 12, color: TEAL }}>GLM-5.1</span>
      </footer>
    </div>
  );
}
