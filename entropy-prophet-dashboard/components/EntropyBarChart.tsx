"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";

const INK   = "#1f2421";
const TEAL  = "#216869";
const GREEN = "#49a078";
const MONO  = "var(--font-space-mono), 'Courier New', monospace";

type ChartEntry = {
  ticker: string;
  p_yes: number;
  entropy: number | null;
};

function shortTicker(ticker: string): string {
  return ticker.replace(/^KX/, "").slice(0, 14);
}

const PencilBar = (props: {
  x?: number; y?: number; width?: number; height?: number; index?: number;
}) => {
  const { x = 0, y = 0, width = 0, height = 0, index = 0 } = props;
  if (height <= 0) return null;
  const id = `ph-${index}`;
  return (
    <g>
      <defs>
        <pattern id={id} patternUnits="userSpaceOnUse" width="5" height="5" patternTransform="rotate(45 0 0)">
          <rect width="5" height="5" fill="rgba(220,225,222,0.5)" />
          <line x1="0" y1="0" x2="0" y2="5" stroke={GREEN} strokeWidth="1.3" strokeOpacity="0.65" />
        </pattern>
      </defs>
      <rect x={x} y={y} width={width} height={height} fill={`url(#${id})`} />
      <rect x={x} y={y} width={width} height={height} fill="none" stroke={TEAL} strokeWidth="1.4" />
    </g>
  );
};

const CustomTooltip = ({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: ChartEntry }>;
}) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{
      background: "#ffffff",
      border: `1.5px solid rgba(33,104,105,0.3)`,
      padding: "10px 14px",
      boxShadow: "2px 4px 0 rgba(33,104,105,0.1), 4px 8px 16px rgba(33,104,105,0.07)",
      fontFamily: MONO, color: INK, fontSize: 11, lineHeight: 1.8,
    }}>
      <div style={{ fontWeight: 700, color: TEAL, marginBottom: 2 }}>{d.ticker}</div>
      <div>P(yes): {(d.p_yes * 100).toFixed(1)}%</div>
      {d.entropy !== null
        ? <div style={{ color: GREEN }}>H: {d.entropy.toFixed(4)}</div>
        : <div style={{ fontStyle: "italic", opacity: 0.5 }}>fallback uniform</div>
      }
    </div>
  );
};

export default function EntropyBarChart({ data }: { data: ChartEntry[] }) {
  return (
    <div style={{
      backgroundColor: "#dce1de",
      backgroundImage: `
        linear-gradient(rgba(33,104,105,0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(33,104,105,0.1) 1px, transparent 1px),
        linear-gradient(rgba(33,104,105,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(33,104,105,0.04) 1px, transparent 1px)
      `,
      backgroundSize: "80px 80px, 80px 80px, 16px 16px, 16px 16px",
    }}>
      <ResponsiveContainer width="100%" height={340}>
        <BarChart data={data} margin={{ top: 12, right: 16, left: 0, bottom: 68 }}>
          <CartesianGrid strokeDasharray="" stroke="rgba(33,104,105,0.1)" strokeWidth={0.5} vertical={false} />
          <XAxis
            dataKey="ticker"
            tickFormatter={shortTicker}
            tick={{ fill: INK, fontSize: 10, fontFamily: "'Courier New', monospace", opacity: 0.6 }}
            angle={-42} textAnchor="end" interval={0}
            axisLine={{ stroke: TEAL, strokeWidth: 1.5 }}
            tickLine={{ stroke: TEAL, strokeWidth: 1, opacity: 0.4 }}
          />
          <YAxis
            domain={[0, 1]}
            tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            tick={{ fill: INK, fontSize: 11, fontFamily: "'Courier New', monospace", opacity: 0.6 }}
            width={44}
            axisLine={{ stroke: TEAL, strokeWidth: 1.5 }}
            tickLine={{ stroke: TEAL, strokeWidth: 1, opacity: 0.4 }}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(73,160,120,0.07)" }} />
          <Bar dataKey="p_yes" shape={<PencilBar />} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
