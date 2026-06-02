# DVWA Skill Usage

This is the user-facing operating guide for `$dvwa-automated-testing`.

## What This Skill Does

Use this skill when you want Codex to solve a local or explicitly authorized DVWA/web-lab/CTF target by reasoning through the task.

The intended behavior is:

1. Log in to the lab with user-provided credentials.
2. Set the requested security level.
3. Navigate to the requested module.
4. Inspect the live page, request/response behavior, cookies, hidden fields, and source code when available.
5. Read the local knowledge base as background, not as an answer key.
6. Form hypotheses and choose the smallest useful tool path.
7. Generate task-specific Python/requests harnesses or Burp/ZAP workflows only when the observations justify automation.
8. Execute tests incrementally and record evidence.
9. Produce a readable Markdown walkthrough report with operation timeline, intermediate operations, automatic Playwright screenshots or failed screenshot command/error notes, timing, evidence, result, and limitations.

DVWA is the first training lab for this skill. The broader goal is to teach Codex how to work like a lab-solving agent across authorized web challenges.

## Codex Plugin Prompt

Use one of these prompt shapes in Codex.

### Single Difficulty

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

### Difficulty Progression

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

Minimum required prompt fields:

- lab URL
- lab login username/password
- module name
- source path when available

Difficulty is optional. If supplied, Codex should solve that single difficulty unless the user asks to continue upward. If omitted, Codex should start at `low` and continue upward until it reaches a defended, blocked, or inconclusive level.

Optional but recommended prompt fields:

- output language, for example `zh-CN` or `en-US`
- output directory for report artifacts
- whether screenshots are required or optional
- whether Burp/ZAP/MCP evidence should be included
- whether to solve only one difficulty or continue upward

## First-Time Setup On Windows

From the skill root:

```powershell
cd <path-to>\dvwa-skills
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_setup.ps1
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 -m playwright install chromium
py -3.11 .\scripts\tool_check.py
```

Always use `py -3.11` for this skill's helpers and generated Python harnesses on Windows. Do not use generic `py -3`, because it may resolve to an unsupported preview Python and break imports such as `requests`.

For only the minimum Brute Force environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_setup.ps1 -SkipGui -SkipIda -SkipBurpMcp
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 -m playwright install chromium
```

Read `references\tool-environment-management.md` for full install/uninstall behavior.

## Local Experiment Steps

Use this sequence for phpStudy-based Windows labs.

1. Start phpStudy.
2. Start Apache/Nginx and MySQL.
3. Open `http://127.0.0.1/DVWA/`.
4. If DVWA is not initialized, open `http://127.0.0.1/DVWA/setup.php` and create/reset the database.
5. Log in with the lab account, commonly `admin` / `password`.
6. Confirm the source path, for example `D:\phpStudy\PHPTutorial\WWW\DVWA`.
7. Run `py -3.11 .\scripts\tool_check.py` from the skill root.
8. Invoke Codex with the prompt above.

## Check Whether The Environment Is Running

Run these commands before a test session.

### Skill And Tool Dependencies

```powershell
cd <path-to>\dvwa-skills
py -3.11 .\scripts\tool_check.py
```

Expected: Python dependencies are present and optional tools are either detected or clearly reported as missing.

### Automatic Screenshot Check

Install Python dependencies and the Playwright Chromium browser:

```powershell
cd <path-to>\dvwa-skills
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 -m playwright install chromium
py -3.11 .\scripts\tool_check.py
```

Expected: `playwright` and `Playwright Chromium` are shown as installed. A challenge run should use Playwright for login/security/module screenshots before falling back to screenshot-not-captured notes.

### DVWA, MySQL, Burp, And MCP Ports

```powershell
Test-NetConnection 127.0.0.1 -Port 80
Test-NetConnection 127.0.0.1 -Port 3306
Test-NetConnection 127.0.0.1 -Port 8080
Test-NetConnection 127.0.0.1 -Port 9876
```

Expected:

- `80`: DVWA web server is running.
- `3306`: MySQL is running, if phpStudy uses the default MySQL port.
- `8080`: Burp or ZAP proxy is running, if proxy evidence is requested.
- `9876`: Burp MCP is running, if MCP is enabled in Burp.

If phpStudy uses a different MySQL port, check that configured port instead of `3306`.

### Listening Process Check

```powershell
Get-NetTCPConnection -State Listen -LocalPort 80,3306,8080,9876 |
  Select-Object LocalAddress,LocalPort,OwningProcess,
    @{Name='ProcessName';Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}} |
  Sort-Object LocalPort
```

Typical process names:

- `httpd`, `nginx`, or phpStudy web process for port `80`
- `mysqld` for port `3306`
- `BurpSuiteCommunity`, `java`, or `zap` for proxy/MCP ports

### DVWA HTTP Check

```powershell
curl.exe -sS -I http://127.0.0.1/DVWA/
curl.exe -sS -L -o NUL -w "final_url=%{url_effective}`nstatus=%{http_code}`n" http://127.0.0.1/DVWA/
```

Expected: final URL is normally `http://127.0.0.1/DVWA/login.php` and status is `200`.

### Burp MCP Check

```powershell
curl.exe -sS -o NUL -w "status=%{http_code}`n" http://127.0.0.1:9876
java -jar C:\Tools\burp-mcp-server\libs\mcp-proxy-all.jar --sse-url http://127.0.0.1:9876
```

Expected:

- `curl` or browser access to `http://127.0.0.1:9876` may return `403`; that is normal because it is not a normal web page.
- The stdio proxy should print `Successfully connected to SSE server`.

### Skill Installation Check

```powershell
Get-Item C:\Users\31435\.codex\skills\dvwa-automated-testing | Format-List FullName,LinkType,Target
python C:\Users\31435\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\31435\.codex\skills\dvwa-automated-testing
```

Expected:

- `LinkType` should be empty if the skill is installed as a normal directory.
- The validator prints `Skill is valid!`.

Useful Brute Force source files:

```text
D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\brute\source\low.php
D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\brute\source\medium.php
D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\brute\source\high.php
D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\brute\source\impossible.php
```

## Burp And MCP

Burp is optional for DVWA Brute Force, but useful for visibility and manual replay.

1. Start Burp Suite Community.
2. Keep Proxy listener on `127.0.0.1:8080`.
3. If using MCP, load `C:\Tools\burp-mcp-server\build\libs\burp-mcp-all.jar` as a Java extension.
4. Enable Burp's `MCP` tab on `http://127.0.0.1:9876`.
5. A browser request to `http://127.0.0.1:9876` may return `403`; that only means the endpoint is not a normal browser page.
6. Verify the stdio proxy when needed:

```powershell
java -jar C:\Tools\burp-mcp-server\libs\mcp-proxy-all.jar --sse-url http://127.0.0.1:9876
```

Expected log line:

```text
Successfully connected to SSE server at http://127.0.0.1:9876
```

MCP is not required. If MCP tools are unavailable, Codex should continue with browser/Burp manual steps, generated Python harnesses, and file artifacts.

## Difficulty Progression Expectation

When the prompt specifies only the challenge type, Codex should:

- start with `low`
- solve or prove the current level before moving upward
- repeat source review, request modeling, baseline probe, test generation, automatic screenshot capture, evidence, and timing for each level
- continue through `medium`, `high`, and `impossible` while the previous level is solved or sufficiently proven
- stop at the first level classified from evidence as `not_vulnerable`, `blocked`, or `inconclusive`, or when continuing would be unsafe for lab state
- explain the stop reason in the Markdown report

## Brute Force Test Expectation

For a proper skill evaluation, Codex should not immediately run `scripts\dvwa_runner.py` or try the known DVWA credential first. A good run should show:

- live module route inspection
- source review of each attempted difficulty file
- request fields and success/failure markers
- one invalid baseline attempt per attempted difficulty
- a small generated credential strategy
- a temporary harness or Burp workflow derived from the observations
- evidence-based classification of credential discovery and vulnerability status
- a readable Markdown report in the requested output language
- a difficulty progression table when difficulty was omitted
- timing summary for setup, source review, test generation, and execution
- screenshot links when available, or an explicit reason when screenshots were not captured

## Report Output Expectations

Read `references\reporting-and-artifacts.md` before final output.

The final Markdown report should include:

- summary and result
- scope and environment
- difficulty progression table when applicable
- operation timeline
- source review
- request model
- hypotheses and test design
- execution evidence
- automatic Playwright screenshots or failed screenshot command/error notes
- timing summary
- no-solution or not-exploitable reason for any defended, blocked, or inconclusive level
- remediation and limitations
- course-report extraction block with experiment conclusion, per-difficulty vulnerability causes, solving steps, tools and operations, core payloads/test inputs, key screenshots, reproduction summary, impossible/no-solution reason, helper scripts, and start/finish/elapsed time

## Optional Helper Smoke Test

Use the bundled helper only to verify that DVWA, Python, requests, and optional proxying work. It is not the main way to evaluate the skill's reasoning.

Low level helper example:

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
  --output-dir .\dvwa-results
```

High level helper with Burp capture:

```powershell
py -3.11 .\scripts\dvwa_runner.py `
  --url http://127.0.0.1/DVWA/ `
  --username admin `
  --password password `
  --module brute-force `
  --difficulty high `
  --source-path D:\phpStudy\PHPTutorial\WWW\DVWA `
  --mode walkthrough `
  --proxy http://127.0.0.1:8080 `
  --export-tool-artifacts `
  --output-dir .\dvwa-results
```

Runtime reports are written to `dvwa-results`. Keep that directory out of the skill package.

## Knowledge Base Layout

Start at:

```text
references\knowledge-base\index.md
```

Each module has:

- `guide.md`: merged operating guide
- `sources\github.md`: notes split from the single GitHub WalkThrough
- `sources\cnblogs.md`: notes for the CNBlogs subpage when available
- `images\`: local mirrored images

Use `references\knowledge-base\source-map.json` to map modules to source URLs, local line ranges, and image counts.

## Tool Rules

- Brute Force: analyze page/source first, then generate a task-specific Python/requests or Burp workflow.
- `scripts\dvwa_runner.py`: optional reference helper for smoke tests and regression only.
- Burp/ZAP: proxy, history, replay, and manual comparison.
- ffuf: fuzzing and low/medium demonstration artifacts; not preferred for token-heavy Brute Force.
- sqlmap: SQL Injection modules only after manual proof and authenticated request export.
- IDA: binary reversing only, not DVWA Brute Force.
- MCP: optional orchestration layer. Missing MCP is not a blocker.

## Uninstall Tools Cleanly

Preview:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1 -WhatIf
```

Remove optional DVWA security tools:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1
```

Also remove shared prerequisites like Git, Go, Python, and JDK:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1 -RemovePrerequisites
```

Use `-RemovePrerequisites` carefully because those tools may be used by other projects.
