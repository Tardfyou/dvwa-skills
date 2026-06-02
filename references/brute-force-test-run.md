# Brute Force Helper Smoke Tests

This file documents the bundled Brute Force helper. Use it to verify the local environment or compare a finished agent-led solution. Do not use it as the first step when evaluating whether Codex can solve a lab.

## User Inputs Needed

- DVWA base URL, for example `http://127.0.0.1/dvwa/`
- DVWA login username
- DVWA login password
- Difficulty: `low`, `medium`, `high`, or `impossible`
- DVWA source path, for example `D:\phpStudy\PHPTutorial\WWW\DVWA`
- Optional Burp/ZAP proxy URL, normally `http://127.0.0.1:8080`
- Optional username/password wordlists

## One-Time Setup

```powershell
cd <path-to>\dvwa-skills
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 .\scripts\tool_check.py
```

## Low Or Medium Smoke Test

```powershell
py -3.11 .\scripts\dvwa_runner.py `
  --url http://127.0.0.1/dvwa/ `
  --username admin `
  --password password `
  --module brute-force `
  --difficulty low `
  --source-path D:\phpStudy\PHPTutorial\WWW\DVWA `
  --mode walkthrough `
  --export-tool-artifacts `
  --output-dir .\dvwa-results
```

Expected helper behavior:

- logs in
- sets the requested security level
- records module inspection and an invalid baseline probe
- tries a small generated credential set
- writes process, evidence, and any discovered credential

## High Smoke Test

```powershell
py -3.11 .\scripts\dvwa_runner.py `
  --url http://127.0.0.1/dvwa/ `
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

Expected helper behavior:

- fetches a fresh `user_token` before attempts
- sends traffic through Burp/ZAP when the proxy is running
- explains token handling in the report

## Impossible Smoke Test

Run the same command with `--difficulty impossible`.

Expected helper behavior:

- treats a known-valid login as `credential_valid`, not automatically as `vulnerable`
- reports lockout, token checks, and failed-login defenses

## Fast Mode

Use fast mode only for repeated environment checks:

```powershell
py -3.11 .\scripts\dvwa_runner.py `
  --url http://127.0.0.1/dvwa/ `
  --username admin `
  --password password `
  --module brute-force `
  --difficulty low `
  --source-path D:\phpStudy\PHPTutorial\WWW\DVWA `
  --mode fast `
  --output-dir .\dvwa-results
```

Fast mode may find known DVWA credentials immediately, so it is not suitable for measuring unseen-task reasoning.

## Custom Wordlists

```powershell
py -3.11 .\scripts\dvwa_runner.py `
  --url http://127.0.0.1/dvwa/ `
  --username admin `
  --password password `
  --module brute-force `
  --difficulty medium `
  --usernames .\wordlists\users.txt `
  --passwords .\wordlists\passwords.txt `
  --max-attempts 500 `
  --mode walkthrough `
  --output-dir .\dvwa-results
```

## Proper Codex Evaluation Prompt

```text
Use $dvwa-automated-testing to solve my authorized local DVWA Brute Force challenge.

Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, identify form fields, tokens, cookies, success/failure markers, form hypotheses, choose tools, generate a task-specific Python/requests harness or Burp workflow if needed, execute tests, and report evidence.

URL: http://127.0.0.1/dvwa/
Login: admin / password
Module: Brute Force
Difficulty: low
Source path: D:\phpStudy\PHPTutorial\WWW\DVWA
Optional proxy: http://127.0.0.1:8080
Output language: zh-CN
Console language: zh-CN
Report requirements: produce a readable Markdown walkthrough report as the primary deliverable. The report must include detailed solving process, intermediate operations, operation log, timing summary with start time, finish time, and elapsed time, automatic Playwright screenshots or screenshot-not-captured notes with the failed command/error, request/response evidence, source analysis, generated test plan, tool use, attempts, result, remediation, limitations, and no-solution reason if the level is defended.
Course-report extraction requirements: add a compact zh-CN section named `实验总报告可提取信息`, containing `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, and `人工验证关注点`. Keep payloads, paths, parameters, commands, and evidence snippets exact.
```

## Helper Output Criteria

- A JSON report and Markdown report appear under `dvwa-results`.
- The Markdown report includes target, module, difficulty, attempts, walkthrough process, baseline probe, evidence, source review, and recommendations.
- For high level, attempts include token-aware requests.
- Optional raw HTTP and ffuf artifacts appear under `dvwa-results\tool-artifacts` when `--export-tool-artifacts` is used.
