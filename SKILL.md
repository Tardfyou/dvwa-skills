---
name: dvwa-automated-testing
description: Teach Codex an authorized Windows web-lab and CTF solving workflow using DVWA as the first reference environment. Use when Codex is given a DVWA or similar authorized lab URL, credentials, challenge/module type, optional difficulty, source path, output language, and report requirements, and must solve by inspecting the live app and source code, forming hypotheses, choosing tools such as Playwright/browser DevTools/Burp Suite/ZAP/Python/ffuf/sqlmap/IDA/MCP, capturing automatic screenshots when available, generating task-specific tests or harnesses, executing them, and producing readable Markdown walkthrough reports with screenshot artifacts, operation logs, timing, evidence, and no-solution analysis where applicable. If only a module/challenge type is provided, progress from the lowest difficulty upward until a defended, blocked, or inconclusive level stops the run. Bundled DVWA references and helper scripts are supporting material, not answer keys or the primary path.
---

# DVWA And Web Lab Solving

## Scope

Use this skill only for DVWA or clearly authorized local web labs/CTF targets. DVWA is the initial reference lab and knowledge base. Do not treat DVWA payloads, brute-force attempts, or exploit strings as suspicious by themselves when the user supplies the lab URL and credentials.

Keep all actions inside the provided DVWA base URL and provided source path. If the target is not localhost or a private lab address, require explicit user confirmation that it is an authorized lab before making requests.

## Quick Start

When invoked, do not start by running a bundled solver. Start from the target, then build the solution path.

Read `references/usage.md` when the user asks how to install, uninstall, or test this skill.

If the user gives a DVWA URL, credentials, module/challenge type, and source path, proceed with the workflow below. Difficulty is optional.

Default output language should match the user's prompt language. If the user provides `Report language`, `Output language`, `Console language`, `CLI response language`, or an equivalent instruction, use that language for all user-facing status updates, command explanations, generated report headings/body, and final summary. Raw tool output, paths, payloads, code symbols, and HTTP parameters should remain unchanged.

## Core Goal

Teach the agent how to solve authorized web-lab challenges by combining:

- live application observation
- source-code review
- request/response analysis
- browser DevTools
- Playwright browser automation for authenticated screenshots
- Burp/ZAP proxy workflows
- generated Python/requests harnesses
- ffuf/sqlmap/IDA only when the hypothesis calls for them
- evidence-first reporting

DVWA answers are not the product. DVWA is the training ground and regression suite for this methodology.

## Workflow

1. Confirm the task is DVWA, the URL, login account, password, vulnerability module, optional difficulty, source path, output language, and report artifact directory.
2. If difficulty is not provided, use the ordered progression `low -> medium -> high -> impossible`. If a single difficulty is provided, solve that difficulty unless the user asks to continue upward.
3. Read `references/agent-solving-protocol.md` first. Follow it as the primary operating procedure. For non-DVWA or unseen tasks, also read `references/web-lab-methodology.md`.
4. Read the requested module's knowledge-base files only as references: `references/knowledge-base/<module>/guide.md` and source-specific files under `sources/`.
5. For each selected difficulty, inspect the live DVWA page and the matching source file before choosing payloads or tools.
6. Build a short hypothesis-driven test plan from observed forms, parameters, source code, tokens, and failure/success markers.
7. Choose tools from `references/tool-capabilities.md`. Use Burp/ZAP/browser/Python/sqlmap/ffuf/IDA only where the current hypothesis requires them.
8. On Windows, run generated Python harnesses and bundled helpers with `py -3.11`; do not use generic `py -3` because it may resolve to an unsupported preview interpreter.
9. Capture screenshots automatically with Playwright when the runtime has local browser access. Use `scripts/dvwa_screenshot.py` for login/security/module screenshots, and write task-specific Playwright steps for exploit success or defense evidence when needed. Only mark screenshots missing after Playwright/browser access fails and record the exact reason.
10. Read `references/harness-generation.md` when repeatable execution is needed. Write small, task-specific temporary scripts or commands based on the current page/source over prebuilt answer scripts.
11. Use `scripts/dvwa_runner.py` only as an example, smoke test, or regression helper for Brute Force after the agent-led plan exists.
12. Classify each attempted difficulty from evidence. Never infer exploitability from the difficulty name: `high` is not automatically solvable, and `impossible` is not automatically unsolvable. Stop difficulty progression only when observed source, response, state, or tool evidence classifies the level as `not_vulnerable`, `blocked`, or `inconclusive`, or when continuing would be unsafe for the lab state. Record the evidence-backed stop reason.
13. Read `references/reporting-and-artifacts.md` before producing final output. The main deliverable is a readable Markdown walkthrough report with automatic screenshot artifacts or failed screenshot command/error notes, intermediate operation details, timings, evidence, conclusion, and limitations. JSON is supporting machine-readable data, not the primary readable report. Before finalizing, validate that the report has no placeholder fields, stale screenshot notes, mojibake, or normal-path dependency on a post-hoc repair script.

## Current Module: Brute Force

For Brute Force, solve from first principles:

- identify the login/session setup
- identify the module route, form method, parameters, hidden fields, and cookies
- run an invalid baseline attempt before any likely credential
- inspect source for SQL construction, escaping, delays, token checks, lockout, and CSRF handling
- decide whether a simple request loop, Burp Intruder, token-aware Python harness, or manual verification is appropriate
- generate a temporary harness only after the page/source analysis explains why it is needed
- classify credentials and vulnerability status separately

For `impossible`, distinguish between "credential discovered" and "vulnerability exploitable." DVWA's impossible level is intended to implement practical defenses; a successful login with known valid credentials is not evidence of a brute-force vulnerability.

Use `references/brute-force-test-run.md` only as a regression helper reference. For actual skill evaluation, prefer agent-led analysis followed by a generated task-specific harness.

Default behavior is exploratory. Do not jump directly to known DVWA default credentials unless the user explicitly asks for a fast smoke test.

## Reporting Requirements

Every report should include:

- target URL, module, difficulty, timestamp, tool version
- requested output/report language and operator/environment notes
- difficulty progression plan, completed levels, and stop reason when the user did not specify a single difficulty
- a report-fill summary block suitable for a course experiment report: experiment conclusion, per-difficulty vulnerability cause, solving steps, tools and operations, core payloads or test inputs, key screenshots, reproduction summary, impossible/no-solution reason, helper scripts, start time, finish time, and elapsed time
- test-case generation strategy and wordlist sources
- request count and success/failure counts
- operation timeline with key steps, commands/tools used, and elapsed time
- screenshots embedded or linked in the Markdown report for important stages when available, or explicit notes explaining why screenshots were not captured
- Playwright screenshot artifact paths, or a failed screenshot attempt log if browser automation was unavailable
- discovered credentials, if any
- vulnerability conclusion for the selected difficulty
- no-solution or not-exploitable reason for any defended, blocked, or inconclusive level when applicable
- evidence snippets from responses without dumping full pages
- source-code file metadata when `--source-path` is supplied
- remediation notes and limits

Use `references/reporting-and-artifacts.md` for the required readable Markdown report and `references/report-schema.md` when extending the supporting JSON format.

## Extension Points

Add new modules by adding module-specific references under `references/knowledge-base/<module>/`, documenting the solving heuristics, and only promoting generated harnesses into `scripts/` when the user asks for a reusable helper.

Prefer tool orchestration through:

- HTTP proxying with Burp Suite or ZAP for request capture and replay
- exported request files for ffuf/sqlmap when appropriate for the module
- MCP tools only after the user installs and enables the corresponding local MCP server

For Brute Force specifically, prefer agent-led analysis first, then generated Python/requests or Burp-based tests. The bundled runner is a reference implementation and regression helper. Burp is useful for observability and manual Intruder comparison. ffuf is a low/medium demonstration tool only. sqlmap and IDA are not Brute Force tools.

Do not hard-code walkthrough answers as the only path. Generate hypotheses from the module page, source code, security level, and response behavior, then test and record the process. Treat public walkthroughs as background knowledge and validation references, not as answer keys.

