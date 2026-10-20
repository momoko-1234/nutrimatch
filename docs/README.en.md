# NutriMatch

An open-source nutrition education prototype with explainable rule-based recommendations and optional local Ollama explanations.

- Next.js / React / TypeScript / Tailwind UI and FastAPI backend.
- Four-step questionnaire, top-eight nutrient priorities, food suggestions and supplement coverage.
- Local Ollama explanations with graceful fallback to the rule report.
- CLI single/batch JSON and Markdown reports, tests, and GitHub Actions CI.

![Workflow](images/workflow.svg)

Use Python 3.11+ and Node.js 22 LTS. In `backend`, create and activate a virtual environment,
run `python -m pip install -r requirements.txt`, then `python -m uvicorn app.main:app --reload --port 8000`.
In `frontend`, run `npm ci` and `npm run dev`, then visit `http://localhost:3000`.
API docs: `http://localhost:8000/docs`.

For local AI, install Ollama, run `ollama pull qwen2.5:7b`, and enable the UI checkbox.
No OpenAI integration is implemented. Scores are heuristic recommendation priorities, not disease probabilities.

See the [main README](../README.md), [user guide](user-guide.md), [API](api.md) and [contributing](../CONTRIBUTING.md).
This is not a medical device or clinically validated model. MIT applies to original code and documentation;
third-party trademarks, models and dependencies retain their own rights.
