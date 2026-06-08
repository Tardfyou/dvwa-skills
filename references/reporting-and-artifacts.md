# Reporting And Artifacts

Use this file before producing the final answer or a saved report for `$dvwa-automated-testing`.

## Output Language

- Match the user's prompt language by default.
- If the prompt includes `Report language`, `Output language`, `Console language`, `CLI response language`, `zh-CN`, `en-US`, or similar wording, use that language for user-facing communication and generated reports.
- Raw terminal output, HTTP evidence, source-code snippets, payloads, paths, and tool names should remain exact. Explain them in the requested language.

## Primary Deliverable

For every solved, attempted, or assessed target, produce a readable Markdown report as the primary deliverable. JSON files, screenshots, request files, ZAP exports, and generated harnesses are supporting artifacts.

A report that only contains JSON, scanner output, a credential, or a final status is incomplete.

## Output Layout

Recommended layout for DVWA progression runs:

```text
dvwa-results\
  <module>-progression-<timestamp>\
    report.md
    report.json
    operation-log.jsonl
    screenshots\
    requests\
    generated-harnesses\
```

Recommended layout for authorized web assessment runs:

```text
dvwa-results\
  authorized-web-assessment-<target>-<timestamp>\
    report.md
    report.json
    operation-log.jsonl
    screenshots\
    requests\
    generated-harnesses\
    zap\
```

Do not put run output into the permanent skill directory.

## DVWA Difficulty Progression

If the user provides only a DVWA challenge/module type and does not specify a difficulty, run the module from the easiest level upward:

```text
low -> medium -> high -> impossible
```

For each level:

- set the DVWA security level
- inspect the page and matching source for that level
- run a baseline invalid probe
- generate level-specific tests or a level-specific harness
- record screenshots/evidence/timing
- classify the result from evidence

Continue only when the current level is solved or sufficiently proven. Stop when observed source, response, state, or tool evidence classifies the current level as `not_vulnerable`, `blocked`, `inconclusive`, or unsafe to continue.

Difficulty names are not conclusions. `high` is not automatically exploitable, and `impossible` is not automatically defended.

## DVWA Report Structure

Use this structure for DVWA challenge reports unless the user asks otherwise:

1. **Summary**
   - target, module, difficulty or difficulty range, result, severity, credential if discovered
   - whether each attempted level was solved, not exploitable, blocked, or inconclusive
2. **Scope And Environment**
   - URL, source path, tools used, proxy/MCP status, report language
3. **Difficulty Progression**
   - difficulty, status, key defense/weakness, request count, elapsed time, artifact links, stop reason
4. **Timeline**
   - ordered operations with start/end timestamps or elapsed seconds
5. **Source Review**
   - source files read, relevant controls, sinks, token logic, delay/lockout behavior
6. **Request Model**
   - route, method, parameters, hidden fields, cookies, success/failure markers
7. **Hypotheses And Test Design**
   - why each test was generated and why specific tools were selected or skipped
8. **Execution Evidence**
   - attempts, request counts, response markers, key snippets, Burp/ZAP notes
9. **Screenshots**
   - embed or link screenshots for key operations, or explain missing screenshots per stage
10. **Timing Summary**
   - run start time, finish time, total elapsed time, and per-phase timing
11. **Result**
   - vulnerable, not vulnerable, credential valid, blocked, or inconclusive
12. **Remediation**
   - practical fixes mapped to the observed weakness
13. **Reproduction Summary**
   - concise steps that a human can repeat in the same authorized local environment
14. **Artifacts**
   - report JSON, operation log, screenshots, request files, generated harnesses
15. **Experiment Report Extraction**
   - provide a compact Chinese block when `Output language: zh-CN` is requested
   - fields: `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, `人工验证关注点`
16. **Limitations**
   - missing tools, missing MCP/browser control, unavailable screenshots, stopped attempts, assumptions

## Authorized Web Assessment Report Structure

For non-DVWA authorized web assessment mode, do not use the DVWA difficulty progression structure. Use this structure:

1. **Summary**
   - target, authorization, scope, dates, overall risk, finding counts by severity/status
2. **Scope And Authorization**
   - included origins, credentials, authorized assessment intensity, and target boundary
3. **Methodology And Tools**
   - browser exploration, source review if available, ZAP spider/passive/active scan, Burp/proxy, ffuf/sqlmap when used, generated harnesses, screenshots
4. **Application Map**
   - pages, routes, forms, API hints, authentication/session observations, storage/cookies, screenshots
5. **Security Header And Configuration Review**
   - observed headers, missing controls, transport assumptions, CSP/clickjacking notes
6. **Findings Table**
   - id, title, status, severity, confidence, affected URL/API, evidence artifact
7. **Active Test Coverage**
   - authentication bypass, injection, XSS, CSRF, IDOR/access control, upload/download, traversal, API abuse, fuzzing, scanner coverage, and tool-specific gaps
8. **Detailed Findings**
   - title, status, severity rationale, affected component, evidence, screenshots, reproduction steps, impact, remediation, limitations
9. **Operation Timeline**
   - start/finish time, major operations, tools, commands, outputs, artifacts
10. **Artifacts**
   - Markdown report, JSON/inventory files, screenshots, request files, generated harnesses, proxy/ZAP exports
11. **State Changes, Cleanup, Limitations, And Next Steps**
   - untested authenticated areas, scanner-only leads, missing tools, recommended manual verification

Scanner or helper output alone is not enough for a confirmed finding. Mark ZAP alerts as `Likely` or `Possible` until reproduced by browser evidence, targeted requests, source review, or a generated harness; for comprehensive authorized assessments, continue from scanner leads to direct validation where the available tools support it.

## Screenshot Rules

Capture screenshots when browser or screenshot tooling is available. Useful screenshots:

- login or authenticated landing confirmation
- target home page and important workflows
- source file or source view showing relevant logic, when available
- baseline response or normal flow
- successful proof response or defensive failure
- Burp/ZAP HTTP history or Repeater evidence when used

Prefer Python Playwright through bundled helpers or generated Python proof scripts. Run them with `py -3.11`.

If a generated proof screenshot script uses Node and `require('playwright')`, install Node Playwright in the run directory first:

```powershell
npm.cmd install playwright@1.60.0 --no-audit --no-fund
node .\generated-harnesses\<proof-screenshot-script>.js .\screenshots
```

Store screenshots under the run output directory and link them from `report.md` with relative Markdown image links:

```markdown
![Evidence screenshot](screenshots/evidence.png)
```

If screenshot tooling is unavailable, do not block the task. Add a `Screenshots` section with one note per missing stage and replacement evidence.

## Operation Log

Maintain an operation log during the run. Each entry should include:

- timestamp
- elapsed seconds since run start
- difficulty level when applicable
- actor/tool
- action
- input summary without secrets
- output summary
- evidence path or screenshot path when available
- duration seconds when measurable

Example:

```json
{"ts":"2026-06-02T09:00:00+08:00","elapsed_s":12.4,"difficulty":"low","tool":"source-review","action":"read low.php","output":"Direct SQL query without token or lockout","duration_s":0.8}
```

## Timing Requirements

At minimum, report:

- total elapsed time
- start time and finish time
- time spent on setup/login/navigation
- time spent on source review when applicable
- time spent on test generation
- time spent executing attempts
- request count when measurable
- per-difficulty elapsed time during DVWA progression runs

If exact timing is unavailable, label it as approximate rather than inventing precision.

## Final Report Preflight

Before saving or handing off `report.md`, check the generated Markdown directly:

- no placeholder content such as `待补充`, `TODO`, empty screenshot lists, or empty extraction fields
- no mojibake in actual file content
- no stale "screenshot not captured" limitation if screenshots were later captured
- no full JSON blobs pasted where concise evidence snippets would be enough
- no generated repair script listed as a normal helper unless it repaired a clearly logged artifact problem

If a repair script was needed, record why it was needed, rerun the preflight after repair, and prefer fixing the report generator or prompt for the next run.
