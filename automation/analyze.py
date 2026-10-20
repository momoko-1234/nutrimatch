"""Reusable single/batch API report template. Python standard library only."""

import argparse
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, ProxyHandler, build_opener


def to_markdown(report):
    lines = ["# NutriMatch 營養教育報告", "", report["profileDescription"], "",
             "分數是規則推薦優先度，不是疾病機率。", ""]
    for item in report["nutrientRecommendations"]:
        lines.extend([f"## {item['nutrient']} · {item['score']}", "", item["whyNeeded"],
                      "", "食物：" + "、".join(item["foodSources"]),
                      "", "時間：" + item["intakeTiming"], "", item.get("caution") or "", ""])
    lines.extend(["## 原始安全提醒", "", *report["safetyNotes"], ""])
    for item in report["currentSupplementReview"]:
        lines.extend([item["productName"], item["comment"], item.get("caution") or "", ""])
    ai = report.get("localAI", {})
    lines.extend(["## 本地 AI", "", f"狀態：{ai.get('status', 'disabled')}",
                  ai.get("explanation") or ai.get("message") or "未啟用", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--ollama", action="store_true", help="Enable local model explanations")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        batch = data if isinstance(data, list) else [data]
        if not batch or any(not isinstance(item, dict) for item in batch):
            raise ValueError("Input must be a questionnaire object or a non-empty array of objects")
        reports = []
        opener = build_opener(ProxyHandler({}))
        for item in batch:
            item = {**item, "use_ollama": args.ollama}
            request = Request(args.api_url.rstrip("/") + "/api/analyze",
                data=json.dumps(item).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="POST")
            with opener.open(request, timeout=150) as response:
                reports.append(json.load(response))
        output = ("\n\n---\n\n".join(to_markdown(report) for report in reports)
                  if args.format == "markdown" else
                  json.dumps(reports if isinstance(data, list) else reports[0], ensure_ascii=False, indent=2))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
        unavailable = sum(report.get("localAI", {}).get("status") == "unavailable" for report in reports)
        print(f"Saved {len(reports)} report(s) to {args.output}; AI unavailable: {unavailable}")
        return 0
    except (OSError, ValueError, HTTPError, URLError, TimeoutError) as error:
        print(f"Analysis failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
