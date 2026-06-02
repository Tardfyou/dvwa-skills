# Tool Capabilities

Use this file when a DVWA, web-lab, or CTF task asks Codex to combine security tools like a penetration-testing workflow.

## Capability Matrix

| Tool | Best Lab Modules | Codex Action | User Setup |
| --- | --- | --- | --- |
| Python/requests harness | All request-level modules | Generate a small task-specific script after inspecting page/source | Install `requests`; provide URL/credentials |
| Playwright browser automation | All modules needing screenshots or DOM proof | Capture authenticated login/security/module/proof screenshots and browser-visible evidence | Install `playwright` and Chromium |
| Bundled Brute Force helper | Brute Force regression | Use `scripts/dvwa_runner.py` as a reference helper or smoke test | Install `requests`; provide URL/credentials |
| Burp Suite Proxy | All web modules | Send browser, generated harness, or helper traffic through `127.0.0.1:8080` | Start Burp and proxy listener |
| Burp Repeater | All request-level modules | Provide raw request artifacts and replay instructions | Manually send selected request if no MCP |
| Burp Intruder | Brute Force low/medium; fuzzing | Provide payload positions and wordlists | Manual Intruder run unless MCP supports it |
| Burp MCP | Request orchestration | Inspect history/replay if MCP is installed | Install PortSwigger MCP server extension |
| OWASP ZAP API | Spider/passive scan/replay | Use API endpoint if enabled; otherwise proxy traffic | Start ZAP and enable API key/port |
| ffuf | Content/parameter fuzzing; Brute Force low demo only | Generate command artifacts | Install Go/ffuf |
| sqlmap | SQL Injection modules only | Generate scoped sqlmap command or request file | Install sqlmap |
| Browser DevTools | DOM XSS/CSP/JS attacks | Use Playwright first for browser evidence; ask user for console/DOM observations only if no browser tool is available | Open F12 manually if automation is unavailable |
| IDA | Binary reversing only | Do not use for DVWA Brute Force | Install only for binary challenges |

## Brute Force Agent Contract

When the user asks to solve DVWA Brute Force, Codex should:

1. Load `references/agent-solving-protocol.md`.
2. Load `references/knowledge-base/brute-force/guide.md` as background.
3. Inspect the live module page and matching source file.
4. Establish failure markers with an invalid credential request.
5. Derive the needed request fields, token handling, and rate/lockout constraints.
6. If difficulty is omitted, plan `low -> medium -> high -> impossible` progression; otherwise use the requested difficulty.
7. Generate a small Python/requests harness or Burp workflow for the current difficulty or progression loop.
8. Run the generated test plan incrementally.
9. Use `scripts/dvwa_runner.py --mode walkthrough` only for comparison or regression after the agent-led test path exists.
10. Produce a readable Markdown report with difficulty progression, automatic Playwright screenshots or failed screenshot command/error notes, operation log, timing, generated test logic, credential result, vulnerability status, request count, evidence, and stop reason.

## MCP Behavior

## Playwright Screenshot Behavior

Prefer Python Playwright through `scripts/dvwa_screenshot.py` or a generated Python proof script. Python Playwright is installed through `scripts\requirements.txt` plus `py -3.11 -m playwright install chromium`.

If a module-specific proof screenshot script is written in Node, install Node Playwright in that run directory before executing the script:

```powershell
npm.cmd install playwright@1.60.0 --no-audit --no-fund
node .\generated-harnesses\<proof-screenshot-script>.js .\screenshots
```

This avoids module-resolution failures where a temporary `npx -p playwright node <script>` invocation cannot provide `require('playwright')` to an external generated script.

Only use MCP tools that are actually connected in the Codex runtime. Do not assume Burp/ZAP/IDA MCP is present because the skill mentions it.

If an MCP tool is unavailable:

- Continue with browser/manual proxy steps, generated Python harnesses, and file artifacts.
- Give manual Burp/ZAP/IDA steps only when that tool is relevant.
- For Brute Force, missing MCP is not a blocker.

## Manual Controls Codex Should Ask The User For

Ask the user to do only these setup actions when needed:

- Start DVWA and confirm the URL opens.
- Provide DVWA login username/password.
- Provide the DVWA source path.
- Start Burp or ZAP if proxy capture is required.
- Install optional tools that are not present.
- For high/impossible Intruder workflows, configure Burp macro/token refresh manually if no Burp MCP or API control is available.
