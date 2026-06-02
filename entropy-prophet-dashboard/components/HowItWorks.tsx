const INK = "#1a2744";
const INK_MID = "rgba(26,39,68,0.5)";
const BORDER = "rgba(26,39,68,0.12)";
const MONO = "var(--font-space-mono), 'Courier New', monospace";
const SERIF = "var(--font-playfair), Georgia, serif";

const SIGNALS = [
  {
    icon: "⚡",
    title: "Internal Entropy",
    description:
      "Sample the LLM multiple times with temperature > 0. Measure the Shannon entropy of its output distribution. High entropy = the model is uncertain, regardless of what it says.",
    status: "active" as const,
  },
  {
    icon: "🔀",
    title: "Cross-source Disagreement",
    description:
      "Compare predictions across multiple LLMs or data sources. When they disagree strongly, confidence in any single answer should be discounted automatically.",
    status: "soon" as const,
  },
  {
    icon: "📈",
    title: "Price Insurgency",
    description:
      "Track when prediction market prices move sharply after your forecast. Calibrate future weights based on how often your entropy signal predicted the surprise.",
    status: "soon" as const,
  },
];

function StatusTag({ status }: { status: "active" | "soon" }) {
  const isActive = status === "active";
  return (
    <span style={{
      display: "inline-block",
      fontFamily: MONO,
      fontSize: 9,
      fontWeight: 700,
      letterSpacing: "2px",
      textTransform: "uppercase" as const,
      padding: "2px 7px",
      border: `1.5px solid ${isActive ? INK : BORDER}`,
      color: isActive ? INK : INK_MID,
      background: isActive ? "rgba(26,39,68,0.05)" : "transparent",
    }}>
      {isActive ? "● active" : "coming soon"}
    </span>
  );
}

/* Hand-drawn SVG pipeline: LLM Samples → Entropy H(X) → Calibrated P */
function PipelineDiagram() {
  const ink = INK;
  const ghost = "rgba(26,39,68,0.15)";
  return (
    <svg
      viewBox="0 0 720 88"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ width: "100%", maxWidth: 680, display: "block", margin: "0 auto 40px" }}
      aria-hidden="true"
    >
      {/* Box 1 */}
      <rect x="8" y="22" width="150" height="44" rx="1" stroke={ink} strokeWidth="1.5" fill="white" />
      <rect x="11" y="25" width="150" height="44" rx="1" stroke={ghost} strokeWidth="1" fill="none" />
      <text x="83" y="42" textAnchor="middle" fontFamily={MONO} fontSize="10" fill={ink} fontWeight="700" letterSpacing="1">LLM SAMPLES</text>
      <text x="83" y="57" textAnchor="middle" fontFamily={MONO} fontSize="9" fill={ink} opacity="0.45">temp &gt; 0, n=10</text>

      {/* Arrow 1 — slight bezier wobble for hand-drawn feel */}
      <path d="M160 44 C180 43 192 45 212 44" stroke={ink} strokeWidth="1.5" strokeLinecap="round" />
      <path d="M207 38.5 L215 44 L207 49.5" stroke={ink} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />

      {/* Box 2 */}
      <rect x="218" y="22" width="160" height="44" rx="1" stroke={ink} strokeWidth="1.5" fill="white" />
      <rect x="221" y="25" width="160" height="44" rx="1" stroke={ghost} strokeWidth="1" fill="none" />
      <text x="298" y="42" textAnchor="middle" fontFamily={MONO} fontSize="10" fill={ink} fontWeight="700" letterSpacing="1">ENTROPY H(X)</text>
      <text x="298" y="57" textAnchor="middle" fontFamily={MONO} fontSize="9" fill={ink} opacity="0.45">Shannon entropy</text>

      {/* Arrow 2 */}
      <path d="M380 44 C400 43 412 45 432 44" stroke={ink} strokeWidth="1.5" strokeLinecap="round" />
      <path d="M427 38.5 L435 44 L427 49.5" stroke={ink} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />

      {/* Box 3 */}
      <rect x="438" y="22" width="170" height="44" rx="1" stroke={ink} strokeWidth="1.5" fill="white" />
      <rect x="441" y="25" width="170" height="44" rx="1" stroke={ghost} strokeWidth="1" fill="none" />
      <text x="523" y="42" textAnchor="middle" fontFamily={MONO} fontSize="10" fill={ink} fontWeight="700" letterSpacing="1">CALIBRATED P</text>
      <text x="523" y="57" textAnchor="middle" fontFamily={MONO} fontSize="9" fill={ink} opacity="0.45">entropy-weighted</text>

      {/* Faint baseline */}
      <line x1="8" y1="80" x2="608" y2="80" stroke={ink} strokeWidth="0.6" strokeDasharray="2 5" opacity="0.15" />
    </svg>
  );
}

export default function HowItWorks() {
  return (
    <section>
      <h2 style={{ fontFamily: SERIF, fontSize: 28, color: INK, margin: "0 0 6px" }}>
        How it works
      </h2>
      <p style={{ fontFamily: "Georgia, serif", fontSize: 13, color: INK_MID, margin: "0 0 32px" }}>
        Three signals that reveal when a model&apos;s confidence is calibrated vs. fabricated.
      </p>

      <PipelineDiagram />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 24 }}>
        {SIGNALS.map((card) => (
          <div
            key={card.title}
            className="paper-card"
            style={{ padding: "24px", display: "flex", flexDirection: "column", gap: 12 }}
          >
            <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
              <span style={{ fontSize: 22 }}>{card.icon}</span>
              <StatusTag status={card.status} />
            </div>
            <h3 style={{ fontFamily: SERIF, fontSize: 16, color: INK, margin: 0 }}>
              {card.title}
            </h3>
            <p style={{ fontFamily: "Georgia, serif", fontSize: 13, color: INK_MID, lineHeight: 1.65, margin: 0 }}>
              {card.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
