from __future__ import annotations

from typing import Any

from report_model import (
    ALLOWED_REPORT_STATUSES,
    find_prohibited_output_key_paths,
    find_prohibited_semantic_paths,
)


def review_report_output(output: dict[str, Any]) -> dict[str, Any]:
    report = output.get("evidence_report", output)
    issues: list[dict[str, str]] = []

    report_status = report.get("status", output.get("status", ""))
    if report_status not in ALLOWED_REPORT_STATUSES:
        issues.append({"code": "invalid_report_status", "detail": f"Invalid report status: {report_status}"})

    risk_disclosure = output.get("risk_disclosure") or report.get("risk_and_limitations", {}).get("risk_disclosure", "")
    if not risk_disclosure:
        issues.append({"code": "missing_risk_disclosure", "detail": "Report output must contain risk_disclosure."})

    if report.get("human_review_required") is not True and output.get("human_review_required") is not True:
        issues.append({"code": "missing_human_review_required", "detail": "Report must require human review."})

    prohibited_key_paths = find_prohibited_output_key_paths(
        {
            "evidence_report": report,
            "report_generation_trace": output.get("report_generation_trace", []),
            "final_output": output.get("final_output", {}),
        }
    )
    for path in prohibited_key_paths:
        issues.append({"code": "prohibited_output_key", "detail": path})

    semantic_paths = find_prohibited_semantic_paths(
        {
            "evidence_report": report,
            "final_output": output.get("final_output", {}),
        }
    )
    for path in semantic_paths:
        issues.append({"code": "prohibited_semantic_text", "detail": path})

    return {
        "status": "failed" if issues else "passed",
        "issues": issues,
        "required_human_actions": [
            "review evidence sources",
            "confirm risk disclosure",
            "confirm no trading action is present",
            "approve before watchlist, simulation, skill activation, or publication handoff",
        ],
    }
