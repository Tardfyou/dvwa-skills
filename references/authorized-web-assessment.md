# Authorized Web Assessment Mode

Use this reference when the user provides a new authorized web target rather than a DVWA module.

## Intent

The expected behavior is agent-led penetration testing assistance:

1. Observe the live application.
2. Build an application model.
3. Use the available tools comprehensively.
4. Verify vulnerabilities with direct evidence.
5. Write a complete Markdown report with screenshots, reproduction details, impact, and remediation.

Do not turn the workflow into "run one scanner and paste the output." Scanners and helpers are evidence sources, not the full assessment.

## Required Inputs

Before making requests, identify these fields from the prompt or ask only when missing:

- target URL
- authorization statement
- authorized target scope
- credentials or instruction that no credentials are available
- assessment intensity, normally `active-comprehensive` for local labs when the user wants complete vulnerability discovery and validation
- output language
- report output directory

If the target is not localhost, a private lab address, or a clearly named training target, require explicit authorization before requests.

## Active-Comprehensive Mode

When `Assessment intensity: active-comprehensive` is provided, use every available supported tool and technique needed to discover and verify vulnerabilities in the authorized target. Do not exclude a vulnerability class because it is active, exploit-oriented, or scanner-driven.

Include these categories by default when the target exposes relevant functionality and the tools support it:

- login and authentication bypass
- default credential and weak credential checks when appropriate for the lab
- SQL, NoSQL, LDAP, template, path, file inclusion, and command injection validation
- authenticated fuzzing
- ZAP spider, passive alerts, and active scan
- Burp proxy capture, replay, and manual comparison
- ffuf content and parameter fuzzing
- sqlmap after a scoped request model exists
- CSRF and state-changing workflow validation
- IDOR and access-control checks across lab-created users
- file upload and execution proof
- directory traversal, download, and information disclosure checks
- XSS, DOM XSS, CSP bypass, and client-side logic abuse
- API abuse, business logic checks, and security misconfiguration validation
- controlled data extraction needed to prove impact in the lab

The remaining boundary is authorization scope. Keep the work tied to the user-authorized target, and record state changes and cleanup steps in the report.

## Agent-Led Workflow

1. **Scope and setup**
   - Record target, authorization, target boundary, credentials, assessment intensity, tools, and output directory.
   - Start an operation log and timing.

2. **Live observation**
   - Use Playwright/browser tooling to load the target.
   - Capture first-viewport and full-page screenshots for important pages.
   - Record title, routes, navigation, forms, buttons, visible app features, cookies, local/session storage, response status, and major scripts.

3. **Surface mapping**
   - Crawl the authorized target.
   - For SPAs, inspect client routes and network requests instead of relying only on HTML links.
   - Extract API candidates from network traffic, forms, JavaScript, and source code when available.
   - Record authentication and role assumptions.

4. **Tooling**
   - Run ZAP spider and passive alerts when available.
   - In active-comprehensive mode, run ZAP active scan against the authorized target and record scan policy, start/end time, alert count, and affected URLs.
   - Use Burp for traffic capture and replay when available.
   - Use ffuf and sqlmap when the target surface and request model justify them.
   - Treat scanner alerts as leads until reproduced or supported by direct evidence; then classify them as confirmed findings.

5. **Hypothesis generation**
   - Group tests by vulnerability class, input point, expected sink/control, and expected impact:
     - authentication/session
     - access control/IDOR
     - injection
     - XSS/DOM sinks
     - CSRF/state-changing actions
     - file upload/download
     - security headers/CSP/clickjacking
     - information disclosure
     - API/business logic
   - In active-comprehensive mode, continue from inventory to direct validation instead of stopping at passive leads.

6. **Targeted validation**
   - Generate Playwright or Python/requests harnesses when repeated browser or request-level validation is useful.
   - Save request/response snippets, screenshots, command output, ZAP/Burp evidence, and timing for each finding.
   - Classify findings as `Confirmed`, `Likely`, `Possible`, `Informational`, or `Not Reproduced`.
   - Record any created accounts, uploaded files, changed records, or cleanup steps.

7. **Report writing**
   - The primary deliverable is a readable Markdown report, not JSON or raw scanner output.
   - Include screenshots, evidence, severity, reproduction steps, affected URLs, impact, remediation, state changes/cleanup, limitations, and next verification steps.

## Optional Inventory Helper

`scripts/authorized_web_assessment.py` can collect a first-pass inventory and ZAP alerts:

```powershell
py -3.11 .\scripts\authorized_web_assessment.py `
  --url http://127.0.0.1:3000/ `
  --authorized `
  --max-pages 12 `
  --zap-url http://127.0.0.1:8090 `
  --zap-active `
  --out-dir ..\dvwa-results\authorized-web-assessment-juice-shop-<timestamp>
```

Use it only as a supporting artifact after the agent has a plan. Its report is an inventory and alert summary, not a complete penetration test. In active-comprehensive mode, continue with active validation and tool-specific evidence after this helper.

## Report Structure

For authorized web assessment reports, use this structure:

1. Summary
2. Scope, authorization, and assessment intensity
3. Methodology and tools
4. Application map
5. Authentication/session observations
6. Crawled pages, forms, API hints, and screenshots
7. Active test coverage
8. Security headers and configuration observations
9. Findings table
10. Detailed finding sections
    - title
    - status: confirmed/likely/possible/informational/not reproduced
    - severity and rationale
    - affected URL/API
    - evidence and screenshots
    - reproduction steps
    - impact
    - remediation
    - state changes/cleanup
    - limitations
11. Operation timeline
12. Artifacts
13. Overall limitations and next steps

## Test Prompt

Use this prompt shape in a new Codex window:

```text
Use $dvwa-automated-testing in authorized web assessment mode against my local simulated target.

Target URL: http://127.0.0.1:3000/
Authorization: This is my local OWASP Juice Shop lab running on 127.0.0.1, and I authorize full active testing against this target.
Assessment intensity: active-comprehensive. Use every available supported tool and technique needed to discover and verify vulnerabilities inside the authorized target, including login bypass, injection, access control testing, upload testing, CSRF, XSS, fuzzing, sqlmap when justified, and ZAP active scan.
Scope: authorized local lab target at http://127.0.0.1:3000/.
Credentials: no credentials initially; create or use lab accounts if the application workflow requires them and record the account state.
Source path: D:\WorkSpace\综合实践5\targets\juice-shop
Tools: use Playwright/browser exploration and screenshots, Python/requests for targeted harnesses, ZAP spider/passive/active scan if available at http://127.0.0.1:8090, Burp if useful, ffuf/sqlmap when an input point and request model justify them. Do not rely on a fixed helper script as the primary workflow.
Output language: zh-CN
Report output directory: D:\WorkSpace\综合实践5\dvwa-results
Report requirements: produce a detailed Markdown penetration testing report with scope, methodology, application map, crawled pages, forms/API hints, screenshots, security headers, ZAP alerts including active scan results, verified findings, evidence, severity/confidence triage, reproduction steps, remediation, operation timeline, artifacts, state changes/cleanup, limitations, and next recommended manual verification steps.
Scope boundary: keep all activity inside this authorized local lab target.
```
