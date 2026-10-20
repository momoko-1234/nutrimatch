# API reference

預設 `http://localhost:8000`；完整欄位、enum 與範圍見 `/docs`、`/openapi.json` 或 `backend/app/schemas.py`。

## GET /health

`200`：`{"status":"ok","service":"NutriMatch API"}`。不代表 Ollama 可用。

## POST /api/analyze

`Content-Type: application/json`。完整虛構輸入見 [examples/profile.json](../examples/profile.json)。

```json
{
  "profile": {
    "age": 34, "sex": "female", "height_cm": 165, "weight_kg": 58,
    "routine": "late_sleep", "diet_habits": ["eating_out"],
    "exercise_frequency_per_week": 2, "water_liters_per_day": 1.2
  },
  "special_groups": [], "symptom_tags": ["high_stress"],
  "chronic_conditions": [], "health_goals": ["sleep", "energy"],
  "current_supplements": [{"product_id": "dhc-b-complex"}],
  "use_ollama": false
}
```

`profile` 必填，其餘陣列預設空、AI 預設關閉。非法值回 `422`，未知產品 ID 目前忽略。

成功回 `200`：

| 欄位 | 內容 |
|---|---|
| profileDescription | 規則摘要 |
| nutrientRecommendations | 前 8 項：nutrient、whyNeeded、foodSources、recommendedSupplements、intakeTiming、caution、score |
| coveredNutrients | 已覆蓋營養素 |
| currentSupplementReview | productId、productName、comment、caution |
| safetyNotes | 原始提醒陣列 |
| matchedProducts | 產品目錄項目 |
| localAI | status、model、explanation、message |

AI status：`disabled`、`success`、`unavailable`。AI 失敗仍回 200 基本報告，必須檢查此欄位。

```bash
curl http://localhost:8000/api/analyze -H "Content-Type: application/json" --data-binary @examples/profile.json
```

從專案根目錄執行。跨平台也可使用 CLI。此版本沒有帳號驗證，不適合直接暴露成公共服務。
