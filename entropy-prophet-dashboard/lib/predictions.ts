import { promises as fs } from "fs";
import path from "path";

export type RawPrediction = {
  market_ticker: string;
  p_yes: number;
  rationale: string;
};

export type Prediction = {
  market_ticker: string;
  p_yes: number;
  entropy: number | null;
  weight: number | null;
  rationale: string;
};

function parseRationale(rationale: string): Pick<Prediction, "entropy" | "weight"> {
  const entropyMatch = rationale.match(/entropy=([0-9.]+)/);
  const weightMatch = rationale.match(/weight=([0-9.]+)/);
  return {
    entropy: entropyMatch ? parseFloat(entropyMatch[1]) : null,
    weight: weightMatch ? parseFloat(weightMatch[1]) : null,
  };
}

export async function getPredictions(): Promise<Prediction[]> {
  const filePath = path.join(process.cwd(), "public", "predictions_econ.json");
  const raw = await fs.readFile(filePath, "utf-8");
  const json = JSON.parse(raw) as { predictions: RawPrediction[] };
  return json.predictions.map((p) => ({ ...p, ...parseRationale(p.rationale) }));
}
