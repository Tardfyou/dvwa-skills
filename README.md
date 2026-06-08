# dvwa-skills

`dvwa-skills` is a Codex skill for authorized Windows web-lab, CTF-style, and simulated-real web assessment workflows, using DVWA as the first reference environment.

It provides:

- web-lab solving workflow instructions in `SKILL.md`
- local knowledge base split by DVWA challenge type
- agent-solving protocol for observing, hypothesizing, testing, and reporting lab tasks
- guidance for generating task-specific Python/requests harnesses
- configurable output language for chat/status responses, command explanations, and reports
- automatic difficulty progression when only the challenge type is specified
- DVWA Brute Force reference helper for low, medium, high, and impossible regression checks
- readable Markdown walkthrough reports plus supporting JSON metadata
- Windows tool setup/uninstall scripts
- optional Burp Suite, ZAP, ffuf, sqlmap, IDA, and Burp MCP integration notes
- authorized web assessment mode for local targets such as OWASP Juice Shop, where Codex explores the app, chooses tools from evidence, verifies findings, and writes a detailed Markdown penetration testing report

## Scope

Use this only against DVWA, another clearly authorized local web lab/CTF target, or an explicitly authorized simulated-real web application.

DVWA is a deliberately vulnerable training target. The workflows, harness guidance, and payload examples in this repository are intended for local security education and controlled testing.

For new web targets, the intended behavior is agent-led assessment. Codex should not rely on a fixed helper script as the primary workflow. Helper scripts are optional evidence collectors or smoke tests after scope, observations, and hypotheses exist.

## Experiment Artifacts And Final Report

This repository includes the current experiment archive:

- `DVWA全自动攻击.md`: consolidated DVWA skill experiment report.
- `experiment-artifacts/dvwa-results/`: copied DVWA and OWASP Juice Shop run outputs, including Markdown reports, screenshots, request evidence, generated harnesses, ZAP output, ffuf/sqlmap output, and operation logs.
- `final-reports/AI在网络安全中的应用研究/AI在网络安全中的应用研究.pdf`: final integrated PDF report.
- `final-reports/AI在网络安全中的应用研究/AI在网络安全中的应用研究.md`: Markdown source for the final integrated report.
- `scripts/build_ai_security_pdf.py`: reproducible builder for the integrated Markdown/HTML/PDF report.

To regenerate the final report from the archived files:

```powershell
cd <path-to>\dvwa-skills
py -3.11 .\scripts\build_ai_security_pdf.py
```

## Quick Start

```powershell
cd <path-to>\dvwa-skills
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 -m playwright install chromium
py -3.11 .\scripts\tool_check.py
```

## Environment Startup Checks

Run these checks before asking Codex to solve a lab.

Check Python dependencies and installed tool paths:

```powershell
cd <path-to>\dvwa-skills
py -3.11 -m playwright install chromium
py -3.11 .\scripts\tool_check.py
```

Check local DVWA web service, MySQL, Burp proxy, and Burp MCP ports:

```powershell
Test-NetConnection 127.0.0.1 -Port 80
Test-NetConnection 127.0.0.1 -Port 3306
Test-NetConnection 127.0.0.1 -Port 8080
Test-NetConnection 127.0.0.1 -Port 9876
```

Expected:

- `80`: Apache/Nginx for DVWA is listening.
- `3306`: MySQL is listening, if phpStudy uses the default MySQL port.
- `8080`: Burp/ZAP proxy is listening, if proxy capture is required.
- `9876`: Burp MCP is listening, if MCP is enabled.

Check which processes own the common lab ports:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 80,3306,8080,9876 |
  Select-Object LocalAddress,LocalPort,OwningProcess,
    @{Name='ProcessName';Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}} |
  Sort-Object LocalPort
```

Check DVWA login route:

```powershell
curl.exe -sS -I http://127.0.0.1/DVWA/
curl.exe -sS -L -o NUL -w "final_url=%{url_effective}`nstatus=%{http_code}`n" http://127.0.0.1/DVWA/
```

Expected: final URL is usually `http://127.0.0.1/DVWA/login.php` and status is `200`.

Check Burp MCP:

```powershell
curl.exe -sS -o NUL -w "status=%{http_code}`n" http://127.0.0.1:9876
java -jar C:\Tools\burp-mcp-server\libs\mcp-proxy-all.jar --sse-url http://127.0.0.1:9876
```

Expected: browser/curl access to `9876` may return `403`; the stdio proxy should print `Successfully connected to SSE server`.

Check skill installation:

```powershell
Get-Item C:\Users\31435\.codex\skills\dvwa-automated-testing | Format-List FullName,LinkType,Target
python C:\Users\31435\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\31435\.codex\skills\dvwa-automated-testing
```

Expected: `LinkType` is empty for a normal directory, and validation prints `Skill is valid!`.

Recommended Codex plugin test prompt:

```text
Use $dvwa-automated-testing to solve my authorized local DVWA Brute Force challenge.

Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, identify routes, forms, parameters, tokens, cookies, success/failure markers, form hypotheses, choose tools, generate a task-specific Python/requests harness or Burp workflow if needed, execute tests, and report evidence.

No difficulty is specified. Start at low, then continue to medium, high, and impossible until a level is defended, blocked, or inconclusive. For each attempted level, repeat page inspection, source review, baseline probing, test generation, execution, evidence collection, automatic Playwright screenshot capture, and timing.

URL: http://127.0.0.1/dvwa/
Login: admin / password
Module: Brute Force
Source path: D:\phpStudy\PHPTutorial\WWW\DVWA
Optional proxy: http://127.0.0.1:8080
Output language: zh-CN
Console language: zh-CN
Report requirements: produce a readable Markdown walkthrough report as the primary deliverable. The report must include detailed solving process, intermediate operations, operation log, timing summary with start time, finish time, and elapsed time, automatic Playwright screenshots or screenshot-not-captured notes with the failed command/error, request/response evidence, source analysis, generated test plan, tool use, attempts, difficulty progression table, result, remediation, limitations, and no-solution reason when a level is defended.
Course-report extraction requirements: add a compact zh-CN section named `实验总报告可提取信息`, containing `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, and `人工验证关注点`. Keep payloads, paths, parameters, commands, and evidence snippets exact.
```

The expected behavior is not instant output from a fixed script. Codex should inspect the live page and source, explain the request model, generate or use a small task-specific harness only if needed, run tests, progress across difficulties when none is specified, and produce a readable Markdown walkthrough report in the requested language.

## Solving Modes

Single difficulty mode:

```text
Use $dvwa-automated-testing to solve my authorized local DVWA Brute Force challenge.
Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, then form hypotheses and execute a task-specific test path.
URL: http://127.0.0.1/dvwa/
Login: admin / password
Module: Brute Force
Difficulty: high
Source path: D:\phpStudy\PHPTutorial\WWW\DVWA
Output language: zh-CN
Console language: zh-CN
Report requirements: produce a readable Markdown walkthrough report as the primary deliverable. The report must include detailed solving process, intermediate operations, operation log, timing summary with start time, finish time, and elapsed time, automatic Playwright screenshots or screenshot-not-captured notes with the failed command/error, request/response evidence, source analysis, generated test plan, tool use, attempts, result, remediation, limitations, and no-solution reason if the level is defended.
Course-report extraction requirements: add a compact zh-CN section named `实验总报告可提取信息`, containing `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, and `人工验证关注点`. Keep payloads, paths, parameters, commands, and evidence snippets exact.
```

Progression mode:

```text
Use $dvwa-automated-testing to solve my authorized local DVWA Brute Force challenge.
Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, then form hypotheses and execute a task-specific test path.
No difficulty is specified. Start at low, then continue to medium, high, and impossible until a level is defended, blocked, or inconclusive.
URL: http://127.0.0.1/dvwa/
Login: admin / password
Module: Brute Force
Source path: D:\phpStudy\PHPTutorial\WWW\DVWA
Output language: zh-CN
Console language: zh-CN
Report requirements: produce a readable Markdown walkthrough report as the primary deliverable. The report must include detailed solving process, intermediate operations, operation log, timing summary with start time, finish time, and elapsed time, automatic Playwright screenshots or screenshot-not-captured notes with the failed command/error, request/response evidence, source analysis, generated test plan, tool use, attempts, difficulty progression table, result, remediation, limitations, and no-solution reason when a level is defended.
Course-report extraction requirements: add a compact zh-CN section named `实验总报告可提取信息`, containing `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, and `人工验证关注点`. Keep payloads, paths, parameters, commands, and evidence snippets exact.
```

## Recreate The Tool Environment

Install the Windows toolchain:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_setup.ps1
```

Minimal Brute Force-only setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_setup.ps1 -SkipGui -SkipIda -SkipBurpMcp
```

Clean uninstall preview:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1 -WhatIf
```

Clean uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1
```

## Burp MCP

The Burp MCP extension JAR is built at:

```text
C:\Tools\burp-mcp-server\build\libs\burp-mcp-all.jar
```

Manual Burp step:

1. Open Burp Suite Community.
2. Add the JAR as a Java extension.
3. Enable the MCP server in Burp's `MCP` tab.
4. Use `http://127.0.0.1:9876` or the stdio proxy:

```powershell
java -jar C:\Tools\burp-mcp-server\libs\mcp-proxy-all.jar --sse-url http://127.0.0.1:9876
```

## Documentation

- Main skill instructions: `SKILL.md`
- User guide: `references\usage.md`
- Agent solving protocol: `references\agent-solving-protocol.md`
- Temporary harness generation: `references\harness-generation.md`
- Reporting and artifacts: `references\reporting-and-artifacts.md`
- Tool environment install/uninstall: `references\tool-environment-management.md`
- Tool capability matrix: `references\tool-capabilities.md`
- Local install status: `references\local-tool-install-status.md`
- Knowledge base index: `references\knowledge-base\index.md`
- Brute Force helper smoke tests: `references\brute-force-test-run.md`

## Current Capability Status

Primary capability:

- agent solving protocol for web-lab and CTF-style tasks
- tool-selection guidance across browser, Burp/ZAP, Python harnesses, ffuf, sqlmap, IDA, and MCP
- DVWA knowledge base as reference material
- temporary harness generation guidance
- automatic `low -> medium -> high -> impossible` progression when difficulty is omitted
- readable Markdown reports with operation logs, automatic Playwright screenshots or failed screenshot command/error notes, timing, evidence, limitations, and no-solution explanations for defended levels

Reference helper status:

- automatic DVWA login
- security level switching
- Brute Force module navigation
- token-aware high/impossible attempts
- proxy support for Burp/ZAP
- report generation

The bundled Brute Force helper is deliberately not the skill's primary solving path. It exists for local smoke tests, comparison, and regression once the agent-led plan has been exercised.
