# 部署指南

先完成本機測試。後端需保留完整 repository，包含 `data/`。
在根目錄安裝 `python -m pip install -r backend/requirements.txt` 後執行：

```bash
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
```

Python 3.11+，設定 `BACKEND_CORS_ORIGINS=https://your-frontend.example`，多來源以逗號分隔。
`.env` 依啟動目錄解析，正式部署建議平台注入環境變數。

前端根目錄選 `frontend`，使用 `npm ci`、`npm run build`、`npm start` 或支援 Next.js 的平台。
建置前設定 `NEXT_PUBLIC_API_BASE_URL=https://your-api.example`；這是公開值，不能包含金鑰，修改後需重建。

## Ollama

必須與 FastAPI 在相同網路命名空間，預設 loopback 11434。
遠端 localhost 是後端主機，並非訪客電腦。先安裝模型並確保足夠資源。
serverless 通常不適合直接運行 7B 模型；可關閉 AI，仍可使用基本分析。
本版本不提供跨容器 Ollama 設定。

公開服務前需補足同意／隱私政策、HTTPS、驗證、限流、模型併發限制及日誌去識別化。
驗證 `/health`、虛構問卷、AI 開關及模型不可用時的降級；勿將真實問卷存入公開 logs 或 CI artifacts。
