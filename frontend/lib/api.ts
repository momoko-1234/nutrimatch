import { API_BASE_URL } from "./constants";
import type { AnalyzeRequest, AnalyzeResponse } from "./types";

export async function analyzeNutritionRisk(
  payload: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`Analyze API failed with status ${response.status}`);
  }

  return response.json();
}
