# 貢獻指南

1. Fork 並建立分支，依 README 啟動前後端。
2. API 變更同步修改 Python schema、TypeScript types、範例與文件。
3. backend 執行 `python -m unittest discover -s tests -v`；frontend 執行 lint、typecheck、build。
4. PR 說明問題、行為與驗證方式，介面變動附虛構資料截圖。

不要提交金鑰、`.env`、真實健康資料、模型權重或依賴目錄。
醫療／營養規則修改請提供可靠來源、適用族群與限制，未驗證內容不可描述成臨床結論。
AI provider 需明確說明資料目的地並保留基本報告降級路徑。
