# 本地 Ollama 分析

本地模型提供繁體中文營養解讀；既有規則負責推薦排序及分數。

1. 安裝並啟動 Ollama，用 `ollama list` 確認模型。
2. 本專案預設使用 `qwen2.5:7b`；若未安裝，可自行執行 `ollama pull qwen2.5:7b`。
3. 後端 `.env` 可設定 `OLLAMA_BASE_URL=http://127.0.0.1:11434`、
   `OLLAMA_MODEL=qwen2.5:7b`、`OLLAMA_TIMEOUT_SECONDS=120`。修改後重啟後端。
4. 在 UI 勾選「使用本地 Ollama 分析」，再按 Generate advice。

API：`POST /api/analyze` 的原有 JSON 新增 `"use_ollama": true`。
省略時預設關閉，以保留原有呼叫方式。回應新增 `localAI`：
`status` 為 `disabled`、`success` 或 `unavailable`，並包含 `model`、
`explanation`、`message`。逾時或失敗仍回傳原規則報告。

首次載入模型可能較慢。模型產生文字不代表醫療驗證；原始安全提醒保持顯示。
啟用時問卷與分析結果會送往執行 FastAPI 電腦上的 Ollama，
只允許 loopback HTTP 位址，拒絕 cloud 模型名稱、不跟隨重新導向，也不使用環境代理。
不呼叫 ChatGPT API。遠端部署時 localhost 指後端主機，並非使用者的電腦。

介接依據：[Ollama Chat API](https://docs.ollama.com/api/chat)。
