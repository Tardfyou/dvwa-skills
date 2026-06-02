# Temporary Harness Generation

Use this when the agent needs repeatable execution. A harness is a short task-specific script generated from the current DVWA page and source code. It should not be a copied answer script.

## When To Generate A Harness

Generate a temporary Python/requests harness when:

- the module requires repeated authenticated requests
- tokens or cookies must be preserved
- response markers need consistent classification
- Burp/ZAP replay is too manual
- the current module does not have a bundled helper

Do not generate a harness before inspecting the live page and source.

## Python Runtime

On Windows, execute generated Python harnesses and bundled helpers with `py -3.11`.
Do not use generic `py -3`; it can resolve to a preview interpreter and break stable dependencies such as `requests` or Playwright.

Recommended invocation:

```powershell
$env:PYTHONIOENCODING='utf-8'
py -3.11 .\generated-harnesses\<module>_<timestamp>.py
```

If Windows command output is localized or contains replacement characters, classify responses with stable ASCII markers when available, such as `TTL=`, `whoami`, DVWA English status strings, HTML element IDs, or exact source-derived error text. Do not rely on localized `ping` prose as the only proof marker.

## Required Inputs From Analysis

Before writing code, identify:

- base URL
- login route
- module route
- form method
- parameter names
- hidden fields and tokens
- cookies that matter
- security-level setup path
- baseline success marker
- baseline failure marker
- rate limit, delay, lockout, or token refresh behavior

## Harness Structure

Use this shape:

1. Create a `requests.Session`.
2. GET `login.php`.
3. Parse hidden login fields such as `user_token`.
4. POST login credentials.
5. GET `security.php`.
6. Parse token if present.
7. POST selected difficulty.
8. GET the module page.
9. Parse module fields.
10. Send a deliberately invalid baseline request.
11. Generate a small test set from the current hypothesis.
12. Execute tests incrementally.
13. Classify responses using observed markers.
14. Record operation log entries and timing for setup, source review, test generation, and execution.
15. Capture screenshots through Python Playwright where possible, or record the exact failed screenshot command and error.
16. Write a readable Markdown walkthrough report plus supporting JSON metadata following `references/reporting-and-artifacts.md`.
17. Run a final report preflight: no `待补充`, no mojibake, no missing extraction fields, no stale screenshot-not-captured note when screenshots were later captured, and no reliance on a generated repair script as the normal path.

For difficulty progression runs, wrap steps 7-14 in a per-difficulty loop using `low`, `medium`, `high`, then `impossible`. Stop when the current level is classified as `not_vulnerable`, `blocked`, or `inconclusive`, and record the stop reason.

## Brute Force Harness Requirements

For Brute Force:

- Do not try `admin:password` first during walkthrough/evaluation.
- Probe a wrong credential first.
- Parse `user_token` for high/impossible before each attempt.
- Stop when a credential is found or when lockout/defense behavior appears.
- Record every attempted pair and marker.
- If using Burp, support a proxy argument.
- Track request count, elapsed time, and average attempt time when measurable.
- Capture screenshot artifacts automatically with Playwright where possible, and store screenshot paths or failed screenshot command/error notes in the report artifacts.
- When no difficulty is specified, produce a progression table and per-difficulty evidence in the Markdown report.

## Where To Put Temporary Harnesses

Prefer a run-specific output directory, for example:

```text
dvwa-results\generated-harnesses\
```

Name scripts by module, difficulty, and timestamp. Keep generated scripts out of the skill's permanent `scripts\` directory unless the user asks to promote them into the skill.

## Promotion Rule

Only promote a generated harness into `scripts\` when:

- it works against multiple runs
- it is parameterized
- it does not hard-code answer payloads
- it records process and evidence
- the user explicitly wants it added to the reusable skill
