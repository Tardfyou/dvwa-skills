# Authorized Web Assessment Mode

Use this reference when the user provides a new authorized web target rather than a DVWA module.

## Intent

The expected behavior is agent-led penetration testing assistance:

1. Observe the live application.
2. Build an application model.
3. Choose tools based on hypotheses.
4. Verify findings with targeted evidence.
5. Write a complete Markdown report with screenshots and reproduction details.

Do not turn the workflow into "run one scanner and paste the output." Helper scripts and scanners are evidence sources only.

## Required Inputs

Before making requests, identify these fields from the prompt or ask only when missing:

- target URL
- authorization statement
- scope, normally same-origin for local labs
- credentials or instruction that no credentials are available
- allowed intensity, default `passive/safe`
- output language
- report output directory

If the target is not localhost, a private lab address, or a clearly named training target, require explicit authorization before requests.

## Default Boundaries

Default allowed actions:

- same-origin browser navigation
- page, route, form, link, script, cookie, storage, and API inventory
- security-header review
- source-code review when source path is provided
- passive ZAP spider and passive alerts
- Burp proxy capture and replay of already observed requests
- targeted harmless probes against lab inputs
- screenshots and operation logs

Default forbidden actions unless the user explicitly authorizes them and the plan includes limits and cleanup:

- ZAP active scan
- password spraying, credential stuffing, or broad brute force
- destructive payloads
- web shell upload or command execution payloads
- reverse shells, external callbacks, persistence, or lateral movement
- production data dumping or sensitive-data exfiltration
- scanning other origins, ports, or networks outside scope

## Agent-Led Workflow

1. **Scope and setup**
   - Record target, scope origin, credentials, authorization, allowed tools, and output directory.
   - Start an operation log and timing.

2. **Live observation**
   - Use Playwright/browser tooling to load the target.
   - Capture first-viewport and full-page screenshots for important pages.
   - Record title, routes, navigation, forms, buttons, visible app features, cookies, local/session storage, response status, and major scripts.

3. **Surface mapping**
   - Crawl same-origin pages conservatively.
   - For SPAs, inspect client routes and network requests instead of relying only on HTML links.
   - Extract API candidates from network traffic, forms, JavaScript, and source code when available.
   - Record authentication and role assumptions.

4. **Passive tooling**
   - Use ZAP spider/passive alerts when available.
   - Treat ZAP alerts as leads. Do not mark them confirmed until reproduced or supported by direct evidence.
   - Use Burp for traffic capture and replay when available.

5. **Hypothesis generation**
   - Group possible tests by vulnerability class, input point, expected sink/control, and risk:
     - authentication/session
     - access control/IDOR
     - injection
     - XSS/DOM sinks
     - CSRF/state-changing actions
     - file upload/download
     - security headers/CSP/clickjacking
     - information disclosure
     - business logic
   - Start with the lowest-risk tests that can prove or disprove the hypothesis.

6. **Targeted validation**
   - Generate small Playwright or Python/requests harnesses only after the observed request model justifies automation.
   - Keep payloads harmless and local to the lab.
   - Save request/response snippets, screenshots, and timing for each finding.
   - Classify findings as `Confirmed`, `Likely`, `Possible`, `Informational`, or `Not Reproduced`.

7. **Report writing**
   - The primary deliverable is a readable Markdown report, not JSON or raw scanner output.
   - Include screenshots, evidence, severity, reproduction steps, affected URLs, impact, remediation, limitations, and next manual verification steps.

## Optional Inventory Helper

`scripts/authorized_web_assessment.py` can collect a low-risk first-pass inventory:

```powershell
py -3.11 .\scripts\authorized_web_assessment.py `
  --url http://127.0.0.1:3000/ `
  --authorized `
  --max-pages 12 `
  --zap-url http://127.0.0.1:8090 `
  --out-dir ..\dvwa-results\authorized-web-assessment-juice-shop-<timestamp>
```

Use it only as a supporting artifact after the agent has a plan. Its report is an inventory and passive-alert summary, not a complete penetration test.

## Report Structure

For authorized web assessment reports, use this structure:

1. Summary
2. Scope, authorization, and constraints
3. Methodology and tools
4. Application map
5. Authentication/session observations
6. Crawled pages, forms, API hints, and screenshots
7. Security headers and configuration observations
8. Findings table
9. Detailed finding sections
   - title
   - status: confirmed/likely/possible/informational/not reproduced
   - severity and rationale
   - affected URL/API
   - evidence and screenshots
   - reproduction steps
   - impact
   - remediation
   - limitations
10. Operation timeline
11. Artifacts
12. Overall limitations and next steps

## Test Prompt

Use this prompt shape in a new Codex window:

```text
Use $dvwa-automated-testing in authorized web assessment mode against my local simulated target.

Target URL: http://127.0.0.1:3000/
Authorization: This is my local OWASP Juice Shop lab running on 127.0.0.1, and I authorize same-origin testing.
Assessment mode: passive/safe first, then targeted harmless verification only when a hypothesis is supported by observed evidence.
Scope: same-origin only. Do not scan other hosts, ports, or external networks.
Credentials: no credentials initially; create or use a lab account only if the application workflow requires it and record the account state.
Source path: D:\WorkSpace\综合实践5\targets\juice-shop
Tools: use Playwright/browser exploration and screenshots, Python/requests for targeted harnesses, ZAP spider/passive alerts if available at http://127.0.0.1:8090, and Burp only if useful. Do not rely on a fixed helper script as the primary workflow.
Output language: zh-CN
Report output directory: D:\WorkSpace\综合实践5\dvwa-results
Report requirements: produce a detailed Markdown penetration testing report with scope, methodology, application map, crawled pages, forms/API hints, screenshots, security headers, ZAP passive alerts, verified findings, evidence, severity/confidence triage, reproduction steps, remediation, operation timeline, artifacts, limitations, and next recommended manual verification steps.
Prohibited actions: no destructive payloads, no credential attacks, no web shells, no reverse shells, no persistence, no external callbacks, no ZAP active scan, and no out-of-scope network access.
```
