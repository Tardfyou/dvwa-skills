# Report Schema

The JSON report should keep this shape:

```json
{
  "metadata": {
    "tool": "agent-generated-harness|burp|zap|browser|dvwa_runner.py",
    "mode": "agent-led|helper-walkthrough|helper-fast",
    "output_language": "zh-CN|en-US|user-specified",
    "started_at": "ISO-8601",
    "finished_at": "ISO-8601",
    "elapsed_seconds": 0,
    "target": "DVWA base URL",
    "module": "brute-force",
    "difficulty": "low|medium|high|impossible|progression",
    "difficulty_order": ["low", "medium", "high", "impossible"],
    "primary_markdown_report": "report.md"
  },
  "scope": {
    "authorized_lab": true,
    "local_or_private_target": true,
    "source_path": "optional"
  },
  "source_review": {},
  "difficulty_progression": [
    {
      "difficulty": "low|medium|high|impossible",
      "status": "vulnerable|not_vulnerable|credential_valid|blocked|inconclusive|not_attempted",
      "started_at": "ISO-8601",
      "finished_at": "ISO-8601",
      "elapsed_seconds": 0,
      "request_count": 0,
      "credential": null,
      "key_evidence": [],
      "screenshots": [],
      "stop_reason": "optional"
    }
  ],
  "timings": {
    "setup_seconds": 0,
    "source_review_seconds": 0,
    "test_generation_seconds": 0,
    "execution_seconds": 0,
    "reporting_seconds": 0
  },
  "process": [
    {
      "step": "login|security|module-inspection|baseline-probe|success-classification",
      "timestamp": "ISO-8601",
      "elapsed_seconds": 0,
      "duration_seconds": 0,
      "difficulty": "low|medium|high|impossible|n/a",
      "tool": "browser|source-review|burp|zap|generated-harness|shell",
      "detail": "what was observed or decided",
      "data": {},
      "evidence": []
    }
  ],
  "operation_log": [
    {
      "timestamp": "ISO-8601",
      "elapsed_seconds": 0,
      "difficulty": "low|medium|high|impossible|n/a",
      "tool": "tool name",
      "action": "short action",
      "input_summary": "no secrets",
      "output_summary": "short result",
      "duration_seconds": 0,
      "artifact": "optional path"
    }
  ],
  "baseline_probe": {},
  "tool_artifacts": {
    "raw_request": "optional Burp/ZAP request template",
    "ffuf_example": "optional ffuf command file",
    "generated_harness": "optional generated script path",
    "operation_log": "optional jsonl path"
  },
  "helper_scripts": [
    {
      "path": "optional generated or bundled script path",
      "purpose": "what the script does",
      "invocation": "command used or reproduction command",
      "generated_for_this_run": true
    }
  ],
  "screenshots": {
    "available": false,
    "items": [
      {
        "difficulty": "low|medium|high|impossible|n/a",
        "label": "module page|baseline failure|success proof|defense evidence",
        "path": "optional screenshot path",
        "caption": "what the screenshot proves",
        "timestamp": "ISO-8601"
      }
    ],
    "missing_reason": "why screenshots were not captured"
  },
  "test_generation": {
    "strategy": "generated|wordlist",
    "usernames": 0,
    "passwords": 0,
    "max_attempts": 0,
    "avoid_default_first": true,
    "refresh_token_per_attempt": false,
    "rationale": []
  },
  "attempts": [],
  "finding": {
    "status": "vulnerable|not_vulnerable|credential_valid|blocked|inconclusive",
    "severity": "none|low|medium|high",
    "credential": null,
    "evidence": [],
    "no_solution_reason": "optional explanation for high/impossible or defended levels"
  },
  "course_report_extraction": {
    "experiment_conclusion": "short conclusion suitable for the course report",
    "per_difficulty_causes": [
      {
        "difficulty": "low|medium|high|impossible",
        "cause": "vulnerability cause or defense reason"
      }
    ],
    "solving_steps": [],
    "tools_and_operations": [],
    "core_payloads_or_test_inputs": [],
    "key_screenshots": [],
    "reproduction_summary": [],
    "impossible_or_no_solution_reason": "optional",
    "helper_scripts": [],
    "started_at": "ISO-8601",
    "finished_at": "ISO-8601",
    "elapsed_seconds": 0,
    "manual_verification_focus": []
  },
  "readability": {
    "markdown_report": "optional report path",
    "include_step_by_step_process": true,
    "include_timing_summary": true,
    "include_screenshot_links": true,
    "include_difficulty_progression_table": true,
    "markdown_is_primary_deliverable": true
  },
  "recommendations": []
}
```

Markdown reports should be readable and derived from the JSON report. Follow `references/reporting-and-artifacts.md` for section order, screenshots, timing, and no-solution analysis.
