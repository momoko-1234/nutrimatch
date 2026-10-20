# Security policy

目前維護預設分支的教育原型，未提供正式醫療服務安全保證。
不要在公開 Issue 張貼金鑰、健康資料或可利用的漏洞細節。
若已啟用 GitHub private vulnerability reporting，請到 Security → Report a vulnerability。
否則先以不含漏洞細節的 Issue 請維護者提供私下回報方式。

Ollama 請保留在 loopback，不要公開 11434 埠。
公開部署前補足 HTTPS、驗證、限流、模型併發限制與隱私政策，避免記錄真實問卷。

## 依賴檢查紀錄（2026-10-20）

已將 Next.js 更新至 15.5.28，並讓依賴共用已修補的 PostCSS 8.5.31。
當次 `npm audit --omit=dev` 回報 0 項已知漏洞，這不代表沒有安全風險。
完整 audit 仍回報 9 項開發工具相關漏洞（2 moderate、7 high），涉及 Tailwind 3 / ESLint 工具鏈的 glob／樣式解析依賴。
這些工具只應處理可信任的原始碼，不應讓使用者上傳任意 glob 或樣式作為建置輸入。
修復完整工具鏈可能需要 Tailwind / ESLint 主要版本遷移，列為後續維護工作；不要使用 `npm audit fix --force` 盲目改版。
