"use client";

const INK     = "#1f2421";
const INK_MID = "rgba(31,36,33,0.55)";
const TEAL    = "#216869";
const GREEN   = "#49a078";
const BORDER  = "rgba(33,104,105,0.18)";
const MONO    = "var(--font-space-mono), 'Courier New', monospace";

type Prediction = {
  market_ticker: string;
  p_yes: number;
  entropy: number | null;
  weight: number | null;
  rationale: string;
};

function ConfidenceCell({ p }: { p: number }) {
  const pct = (p * 100).toFixed(1);
  const spacing = p < 0.4 ? "3px" : p < 0.6 ? "5px" : "8px";
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8, fontFamily: MONO, fontSize: 12, color: INK }}>
      <span style={{
        display: "inline-block", width: 26, height: 12,
        border: `1.5px solid ${GREEN}`,
        background: `repeating-linear-gradient(45deg, ${GREEN} 0px, ${GREEN} 1px, transparent 1px, transparent ${spacing})`,
      }} />
      {pct}%
    </span>
  );
}

function EntropyCell({ entropy }: { entropy: number | null }) {
  if (entropy === null)
    return <span style={{ fontFamily: "Georgia, serif", fontSize: 12, color: INK_MID, fontStyle: "italic" }}>fallback uniform</span>;
  const isLow = entropy < 0.005;
  return (
    <span style={{
      fontFamily: MONO, fontSize: 12, color: GREEN,
      fontWeight: isLow ? 700 : 400,
      textDecoration: isLow ? "underline" : "none",
      textUnderlineOffset: "3px",
    }}>
      {entropy.toFixed(4)}
    </span>
  );
}

export default function PredictionsTable({ predictions }: { predictions: Prediction[] }) {
  return (
    <div style={{ overflowX: "auto", border: `1.5px solid ${BORDER}`, background: "#ffffff", boxShadow: "2px 4px 16px rgba(33,104,105,0.07)" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: `1.5px solid ${BORDER}`, background: "rgba(33,104,105,0.04)" }}>
            {["Event Ticker", "P(yes)", "Entropy Score", "Weight", "Status"].map((h, i) => (
              <th key={h} style={{
                padding: "10px 20px",
                textAlign: i === 0 ? "left" : "center",
                fontFamily: MONO, fontSize: 9, fontWeight: 700,
                letterSpacing: "2px", textTransform: "uppercase",
                color: TEAL,
              }}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {predictions.map((pred, i) => (
            <tr
              key={pred.market_ticker}
              style={{
                borderBottom: `1px solid ${BORDER}`,
                background: i % 2 === 0 ? "#ffffff" : "rgba(33,104,105,0.025)",
                cursor: "default",
              }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLElement).style.background = "rgba(156,197,161,0.18)")}
              onMouseLeave={(e) => ((e.currentTarget as HTMLElement).style.background = i % 2 === 0 ? "#ffffff" : "rgba(33,104,105,0.025)")}
            >
              <td style={{ padding: "12px 20px", fontFamily: MONO, fontSize: 11, color: INK }}>
                {pred.market_ticker}
              </td>
              <td style={{ padding: "12px 20px", textAlign: "center" }}>
                <ConfidenceCell p={pred.p_yes} />
              </td>
              <td style={{ padding: "12px 20px", textAlign: "center" }}>
                <EntropyCell entropy={pred.entropy} />
              </td>
              <td style={{ padding: "12px 20px", textAlign: "center", fontFamily: MONO, fontSize: 12, color: INK_MID }}>
                {pred.weight !== null ? pred.weight.toFixed(3) : "—"}
              </td>
              <td style={{ padding: "12px 20px", textAlign: "center" }}>
                <span className="rubber-stamp">pending</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
