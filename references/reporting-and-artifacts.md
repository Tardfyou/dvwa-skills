# Reporting And Artifacts

Use this file before producing the final answer or a saved report for `$dvwa-automated-testing`.

## Output Language

- Match the user's prompt language by default.
- If the prompt includes `Report language`, `Output language`, `Console language`, `CLI response language`, `zh-CN`, `en-US`, or similar wording, use that language for all user-facing communication.
- This language rule applies to interim chat updates, command explanations, generated harness comments intended for the user, Markdown report headings/body, final summary, and no-solution explanations.
- Raw terminal output, HTTP evidence, source-code snippets, payloads, paths, and tool names should remain exact. Explain or summarize them in the requested language.

## Primary Deliverable

For every solved or attempted challenge, produce a readable Markdown walkthrough report as the primary deliverable. The JSON report is supporting machine-readable metadata and must not replace the Markdown report.

The Markdown report must include:

- detailed solving process
- intermediate operations
- automatic Playwright screenshots or failed screenshot command/error notes
- request/response evidence
- source review
- generated test or harness rationale
- timing
- final reasoning
- no-solution or not-exploitable explanation where applicable
- a concise extraction block for the course experiment report, including experiment conclusion, per-difficulty vulnerability cause, solving steps, tools and operations, core payloads/test inputs, key screenshot links, reproduction summary, impossible/no-solution reason, helper scripts, and start/finish/elapsed time

A report that only contains JSON, a final credential, or a final status is incomplete.

## Output Layout

Recommended output layout for progression runs:

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

For a single explicitly requested difficulty, `<module>-<difficulty>-<timestamp>` is also acceptable.

Do not put run output into the permanent skill directory.

## Difficulty Progression

If the user provides only a challenge/module type and does not specify a difficulty, run the module from the easiest level upward:

```text
low -> medium -> high -> impossible
```

For each level:

- set the DVWA security level
- inspect the page and matching source for that level
- run a baseline invalid probe
- generate level-specific tests or a level-specific harness
- record screenshots/evidence/timing
- classify the result

Continue to the next level only when the current level is solved or sufficiently proven. Stop when observed source, response, state, or tool evidence classifies the current level as `not_vulnerable`, `blocked`, `inconclusive`, or unsafe to continue. The Markdown report must include a progression table with every attempted level and the evidence-backed stop reason.

Difficulty names are not conclusions. `high` is not automatically exploitable, and `impossible` is not automatically defended. Classify every attempted level independently from evidence.

## Markdown Report Structure

Use this structure unless the user asks for a different one:

1. **Summary**
   - target, module, difficulty or difficulty range, result, severity, credential if discovered
   - whether each attempted level was solved, not exploitable, blocked, or inconclusive
2. **Scope And Environment**
   - URL, source path, tools used, proxy/MCP status, report language
3. **Difficulty Progression**
   - ordered table: difficulty, status, key defense/weakness, request count, elapsed time, artifact links, stop reason
   - include one short vulnerability-cause explanation per attempted difficulty
4. **Timeline**
   - ordered operations with start/end timestamps or elapsed seconds
   - include login, security-level change, page inspection, source review, screenshot capture, baseline probe, generated test execution, and conclusion
5. **Source Review**
   - source files read, relevant controls, sinks, token logic, delay/lockout behavior
6. **Request Model**
   - route, method, parameters, hidden fields, cookies, success/failure markers
7. **Hypotheses And Test Design**
   - why each test was generated
   - why specific tools were selected or skipped
   - list core payloads, probes, credential candidates, request mutations, or browser inputs that prove the result
8. **Execution Evidence**
   - attempts, request counts, response markers, key snippets, Burp/ZAP notes
   - include screenshots as Markdown image links when available
9. **Screenshots**
   - embed or link screenshots for key operations
   - for missing screenshots, give a per-stage reason and replacement evidence
10. **Timing Summary**
   - run start time, finish time, total elapsed time, and per-phase timing
11. **Result**
   - vulnerable, not vulnerable, credential valid, blocked, or inconclusive
   - for any defended, blocked, or inconclusive level, explain no-solution or not-exploitable reasons such as token freshness, lockout, prepared statements, current-password checks, strict allowlists, or rate limits
12. **Remediation**
   - practical fixes mapped to the observed weakness
13. **Reproduction Summary**
   - concise numbered steps that a human can repeat in the same authorized local DVWA environment
   - include the security level, page route, required tools, exact payloads or request parameters, expected success/failure markers, and cleanup steps when applicable
14. **Artifacts**
   - report JSON, operation log, screenshots, request files, generated harnesses
   - include helper scripts with path, purpose, invocation, and whether they were generated for this run or are bundled references
15. **Experiment Report Extraction**
   - provide a compact Chinese block when `Output language: zh-CN` is requested
   - fields: `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, `人工验证关注点`
16. **Limitations**
   - missing tools, missing MCP/browser control, unavailable screenshots, stopped attempts, assumptions

## Final Report Preflight

Before saving or handing off `report.md`, check the generated Markdown directly:

- no placeholder content such as `待补充`, `TODO`, empty screenshot lists, or empty extraction fields
- no mojibake in actual file content; distinguish this from PowerShell console display issues by reading UTF-8 text when needed
- no stale "screenshot not captured" limitation if screenshots were later captured
- no full JSON blobs pasted where concise evidence snippets would be enough
- no generated `fix_report.py` listed as a normal helper unless it repaired a clearly logged artifact problem

If a repair script was needed, record why it was needed, rerun the preflight after repair, and prefer fixing the report generator or prompt for the next run.

## Screenshot Rules

Capture screenshots when browser or screenshot tooling is available. Useful screenshots:

- DVWA login or authenticated landing confirmation
- requested security-level page after setting difficulty
- target module page before testing
- source file or source view showing relevant logic
- failed baseline response
- successful proof response or defensive lockout/token failure
- Burp/ZAP HTTP history or Repeater evidence when used

Prefer automatic screenshots through Playwright before falling back to screenshot-not-captured notes. The bundled helper can capture authenticated login/security/module pages:

```powershell
py -3.11 .\scripts\dvwa_screenshot.py `
  --url http://127.0.0.1/dvwa/ `
  --username admin `
  --password password `
  --difficulty low `
  --module-path vulnerabilities/brute/ `
  --output-dir ..\dvwa-results\<run-dir>\screenshots\low
```

For proof screenshots after an exploit attempt, write task-specific Playwright steps in the generated harness or a small temporary script. Screenshot notes are acceptable only after Playwright/browser execution fails; include the command attempted and the error summary.

Prefer the bundled Python helper and Python Playwright environment for screenshots. If a generated proof screenshot script uses Node and `require('playwright')`, do not assume `npx -p playwright node <script>` will let an external script resolve the temporary package. Either install Playwright locally in the run directory first:

```powershell
npm.cmd install playwright@1.60.0 --no-audit --no-fund
node .\generated-harnesses\<proof-screenshot-script>.js .\screenshots
```

or rewrite the proof screenshot flow as a Python Playwright script. Record this command sequence in the operation log when used.

Store screenshots under the run output directory and link them from `report.md` with relative Markdown image links:

```markdown
![Low baseline failure](screenshots/low-baseline-failure.png)
```

If screenshot tooling is unavailable, do not block the task. Add a `Screenshots` section with one note per missing stage:

```text
Screenshot not captured: <reason>. Evidence was recorded through <response snippet/source review/Burp history/manual observation>.
```

Never include full-page dumps or sensitive cookies in screenshots or copied evidence unless the user explicitly asks and it is needed for the local lab.

## Windows Encoding Notes

When PHP, Windows command output, or terminal rendering shows localized text with replacement characters, avoid using that text as the sole marker. Prefer stable ASCII markers from the response or source, such as `Password Changed.`, `Welcome to the password protected area`, `ERROR: You have entered an invalid IP.`, `TTL=`, `whoami`, exact parameter names, or file paths.

Run Python harnesses with `py -3.11` and set `PYTHONIOENCODING=utf-8` when capturing text output through PowerShell.

## Operation Log

Maintain an operation log during the run. Each entry should include:

- timestamp
- elapsed seconds since run start
- difficulty level when applicable
- actor/tool, such as browser, Burp, generated harness, PowerShell, source review
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
- time spent on setup/login/security level
- time spent on source review
- time spent on test generation
- time spent executing attempts
- request count and average attempt time when measurable
- per-difficulty elapsed time during progression runs

If exact timing is unavailable, label it as approximate rather than inventing precision.

## No-Solution Or Not-Exploitable Reports

Some lab levels are intentionally protected, and some high or impossible levels may still have a valid bypass. A good report should stay evidence-driven either way. When no exploit succeeds:

- state the attempted proof path
- name the defense that prevented exploitation
- cite source lines or behavior evidence
- distinguish "credential valid" from "brute-force vulnerability"
- list what would be required to continue, such as larger wordlists, valid user interaction, or tool access
- avoid claiming failure as success

For DVWA Brute Force, successful login using a known valid credential at any difficulty is not proof of a brute-force vulnerability by itself. Treat it as credential validation unless repeated-attempt behavior, missing controls, or a defense bypass proves the vulnerability.
