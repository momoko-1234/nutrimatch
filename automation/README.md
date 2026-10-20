# CLI 自動化模板

先啟動 API，再從 repository 根目錄執行 README 的 CLI 指令。
`--input` 可為單一問卷物件或問卷陣列，依序執行；全部成功才寫入報告，錯誤回 exit code 1。
`--format json` 保留完整 API 回應，`--format markdown` 產生閱讀版。
`--ollama` 控制所有輸入的 AI 開關，未指定則全部使用規則分析。
AI 不可用是可降級狀態，仍寫入報告、回 exit code 0，並在終端顯示次數。

預設 API `http://localhost:8000`。可用 `--api-url` 自訂可信任目的地，問卷會傳到該目的地。
不要把真實健康報告存入 Git、公開 CI artifacts 或公開日誌。
CLI 只處理本地檔案與 HTTP 呼叫，沒有憑證管理、排程器或通知功能。
可由 Windows 工作排程器、cron 或你的既有工作流呼叫。
