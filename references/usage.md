# DVWA Skill Usage

This is the user-facing operating guide for `$dvwa-automated-testing`.

## What This Skill Does

Use this skill when you want Codex to solve a local or explicitly authorized DVWA/web-lab/CTF target by reasoning through the task.

The intended behavior is:

1. Confirm scope, authorization, credentials, tools, language, and report output path.
2. Inspect the live target first with browser/HTTP observations.
3. Review source code when a source path is provided.
4. Build an application/request model.
5. Form hypotheses and choose the smallest useful tool path.
6. Generate task-specific Playwright or Python/requests harnesses only when observations justify automation.
7. Use Burp/ZAP/ffuf/sqlmap only when they fit the current hypothesis and scope.
8. Execute tests incrementally and record evidence.
9. Produce a readable Markdown report with screenshots, operation timeline, timing, evidence, findings, remediation, and limitations.

DVWA is the first training lab for this skill. The broader goal is to guide Codex toward agent-led authorized web assessment. Bundled helpers are supporting tools, not fixed workflows.

## Prompt: Authorized Web Assessment

Use this when the target is a new authorized lab or simulated-real application, not a DVWA difficulty module.

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

Expected behavior:

- Codex first explores the application in the browser and builds an app model.
- Tools are selected from observations and hypotheses; scanner/helper output is supporting evidence only.
- The final deliverable is a complete Markdown penetration testing report with screenshots and reproduction details.
- Read `references\authorized-web-assessment.md` for this mode.

## Prompt: DVWA Single Difficulty

```text
Use $dvwa-automated-testing to solve my authorized local DVWA <MODULE> challenge.

Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, identify routes, forms, parameters, tokens, cookies, success/failure markers, form hypotheses, choose tools, generate a task-specific Python/requests harness or Burp workflow if needed, execute tests, and report evidence. Do not infer exploitability from difficulty names: `high` is not automatically solvable, and `impossible` is not automatically unsolvable.

URL: http://127.0.0.1/dvwa/
Login: admin / password
Module: <MODULE>
Difficulty: high
Source path: D:\phpStudy\PHPTutorial\WWW\DVWA
Optional proxy: http://127.0.0.1:8080
Output language: zh-CN
Console language: zh-CN
Report requirements: produce a readable Markdown walkthrough report as the primary deliverable. The report must include detailed solving process, intermediate operations, operation log, timing summary with start time, finish time, and elapsed time, automatic Playwright screenshots or screenshot-not-captured notes with the failed command/error, request/response evidence, source analysis, generated test plan, tool use, attempts, result, remediation, limitations, and no-solution reason if the level is defended.
Course-report extraction requirements: add a compact zh-CN section named `实验总报告可提取信息`, containing `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, and `人工验证关注点`. Keep payloads, paths, parameters, commands, and evidence snippets exact.
```

## Prompt: DVWA Difficulty Progression

```text
Use $dvwa-automated-testing to solve my authorized local DVWA <MODULE> challenge.

Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, identify routes, forms, parameters, tokens, cookies, success/failure markers, form hypotheses, choose tools, generate a task-specific Python/requests harness or Burp workflow if needed, execute tests, and report evidence. Do not infer exploitability from difficulty names: `high` is not automatically solvable, and `impossible` is not automatically unsolvable.

No difficulty is specified. Start at low, then continue to medium, high, and impossible until a level is defended, blocked, or inconclusive. For each attempted level, repeat page inspection, source review, baseline probing, test generation, execution, evidence collection, automatic Playwright screenshot capture, and timing.

URL: http://127.0.0.1/dvwa/
Login: admin / password
Module: <MODULE>
Source path: D:\phpStudy\PHPTutorial\WWW\DVWA
Optional proxy: http://127.0.0.1:8080
Output language: zh-CN
Console language: zh-CN
Report requirements: produce a readable Markdown walkthrough report as the primary deliverable. The report must include detailed solving process, intermediate operations, operation log, timing summary with start time, finish time, and elapsed time, automatic Playwright screenshots or screenshot-not-captured notes with the failed command/error, request/response evidence, source analysis, generated test plan, tool use, attempts, difficulty progression table, result, remediation, limitations, and no-solution reason when a level is defended.
Course-report extraction requirements: add a compact zh-CN section named `实验总报告可提取信息`, containing `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, and `人工验证关注点`. Keep payloads, paths, parameters, commands, and evidence snippets exact.
```

## Setup And Checks On Windows

From the skill root:

```powershell
cd <path-to>\dvwa-skills
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_setup.ps1
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 -m playwright install chromium
py -3.11 .\scripts\tool_check.py
```

Use `py -3.11` for bundled helpers and generated Python harnesses on Windows. Do not use generic `py -3`, because it may resolve to a different interpreter.

To check and optionally start the local lab tools:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_and_start_lab_tools.ps1
```

Use `-NoStart` for check-only mode:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_and_start_lab_tools.ps1 -NoStart
```

Common local ports:

- `80`: DVWA/phpStudy web server
- `3306`: MySQL, if phpStudy uses the default port
- `8080`: Burp proxy
- `8090`: ZAP daemon/API
- `9876`: Burp MCP, if enabled inside Burp

## OWASP Juice Shop Local Target

The current simulated-real target can be started from:

```text
D:\WorkSpace\综合实践5\targets\juice-shop
```

If dependencies are already installed and the app is built:

```powershell
Start-Process -FilePath node.exe -ArgumentList "build/app" -WorkingDirectory "D:\WorkSpace\综合实践5\targets\juice-shop" -WindowStyle Hidden
```

Expected URL:

```text
http://127.0.0.1:3000/
```

If rebuilding is needed and Docker is unavailable:

```powershell
cd D:\WorkSpace\综合实践5\targets\juice-shop
npm.cmd install
npm.cmd run build:frontend
npm.cmd run build:server
node build/app
```

## Optional Helper Smoke Tests

Bundled helpers are only for environment checks, inventory, or regression. They are not the primary way to evaluate the skill's reasoning.

DVWA Brute Force regression helper:

```powershell
py -3.11 .\scripts\dvwa_runner.py `
  --url http://127.0.0.1/DVWA/ `
  --username admin `
  --password password `
  --module brute-force `
  --difficulty low `
  --source-path D:\phpStudy\PHPTutorial\WWW\DVWA `
  --mode walkthrough `
  --export-tool-artifacts `
  --output-dir ..\dvwa-results
```

Authorized web inventory helper:

```powershell
py -3.11 .\scripts\authorized_web_assessment.py `
  --url http://127.0.0.1:3000/ `
  --authorized `
  --max-pages 12 `
  --zap-url http://127.0.0.1:8090 `
  --out-dir ..\dvwa-results\authorized-web-assessment-juice-shop-<timestamp>
```

The inventory helper output can support a later report, but it is not a complete penetration test by itself.

## Tool Rules

- Playwright: browser exploration, screenshots, SPA/network observation, proof capture.
- Python/requests: small targeted harnesses after the request model is known.
- Burp: proxy capture, history, replay, manual comparison.
- ZAP: spider and passive alerts by default; active scan only with explicit authorization and limits.
- ffuf: scoped content/parameter fuzzing after a safe request model exists.
- sqlmap: SQL injection only after manual proof and scoped authenticated request export.
- IDA: binary reversing only, not normal DVWA Web modules.
- MCP: optional orchestration. Missing MCP is not a blocker.

Runtime reports are written to `dvwa-results`. Keep that directory out of the skill package.
