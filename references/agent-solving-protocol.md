# Agent Solving Protocol

This is the core protocol for `$dvwa-automated-testing`. The purpose of the skill is to make the agent capable of solving authorized web-lab and CTF-style tasks, including tasks it has not seen before. DVWA is the first reference environment and regression lab. Knowledge-base walkthroughs are references, not answer keys. Scripts are execution helpers, not the primary reasoning path.

## Non-Negotiable Rule

Do not begin by running a one-shot solver script or by trying a known default answer.

Begin by building a task model from the live DVWA page, the selected security level, the available source code, and observed request/response behavior.

## Universal Web Lab Task Loop

Use this loop for every module:

1. **Scope**
   - Confirm the target is DVWA or another authorized web lab/CTF target.
   - Record URL, credentials, module, optional difficulty, source path, output language, and report artifact directory.
   - Keep all requests inside the provided lab scope.
   - If the user did not specify a difficulty, plan `low -> medium -> high -> impossible` progression and stop at the first defended, blocked, or inconclusive level.

2. **Orient**
   - Log in.
   - Set the requested security level, or the current level in the progression.
   - Open the module page.
   - Identify route, forms, methods, parameters, hidden fields, cookies, tokens, redirects, and response markers.

3. **Read Local Source**
   - Locate the matching source file for the selected difficulty.
   - Identify validation, escaping, tokens, rate limits, state changes, database calls, file operations, command execution, or browser-side code.
   - Convert source observations into hypotheses. Do not copy a final payload from a walkthrough without verifying it.

4. **Baseline**
   - Send at least one normal valid-looking request.
   - Send at least one deliberately invalid or harmless probe.
   - Record success and failure markers: text, status, length, timing, cookies, DOM effects, or database/file changes.

5. **Hypothesize**
   - State what vulnerability class might exist.
   - State what control might block it.
   - State the smallest safe test that distinguishes vulnerable from not vulnerable.

6. **Generate Tests**
   - Build a small hypothesis-driven test set first.
   - Only expand to wordlists or scanners after a manual/targeted proof.
   - For tokenized flows, plan token refresh.
   - For state-changing modules, plan cleanup or rollback.

7. **Choose Tools**
   - Use browser/DevTools for DOM, CSP, JavaScript, and visual proof.
   - Use Burp/ZAP for request capture, replay, and mutation.
   - Use Python/requests for repeatable session-aware testing.
   - Use ffuf for fuzzing after request shape is understood.
   - Use sqlmap only for SQL Injection modules after manual proof and authenticated request export.
   - Use IDA only for binary reversing tasks, not DVWA PHP Brute Force.
   - Use MCP only when the tool is connected; missing MCP is not a blocker.

8. **Execute And Observe**
   - Run tests incrementally.
   - Record request count, payload source, response marker, and tool used.
   - Stop early when the proof is sufficient or when defenses such as lockout appear.

9. **Conclude**
   - Classify the result as vulnerable, not vulnerable, credential valid, or inconclusive.
   - Separate authentication success from vulnerability proof.
   - Include evidence and remediation.

10. **Report**
    - Report process, not only final answer.
    - Use the requested output language, or match the user's language if none is specified. This applies to chat/status messages, command explanations, final summary, and Markdown report content.
    - Produce a readable Markdown walkthrough report as the primary deliverable. JSON is supporting metadata.
    - Include observations, hypotheses, test generation rationale, attempts, evidence, tool artifacts, automatic Playwright screenshots or failed screenshot command/error notes, timing, and source review.
    - If difficulty progression was used, include a progression table with level, status, evidence, timing, and stop reason.
    - For defended high/impossible levels, explain why the challenge is not exploitable or why the run is inconclusive.

## Brute Force-Specific Protocol

If no difficulty is specified, solve Brute Force in order: `low`, `medium`, `high`, `impossible`. Repeat the following protocol per level until a level cannot be exploited or is intentionally defended.

1. Set the current difficulty in DVWA.
2. Inspect the form and determine parameter names and request method.
3. Submit a deliberately wrong credential and record the failure marker.
4. Read `vulnerabilities/brute/source/<difficulty>.php`.
5. Determine whether the level uses direct SQL, escaping, delay, token, lockout, or prepared statements.
6. Generate a credential strategy:
   - Start with a few wrong passwords to establish failure behavior.
   - Use user-supplied wordlists when provided.
   - Keep known DVWA defaults late in the sequence during walkthrough/evaluation mode.
7. For high/impossible, fetch a fresh `user_token` before each attempt.
8. Use Burp/ZAP proxy capture when external-tool evidence is requested.
9. Capture screenshots where tooling is available: module page, baseline failure, success proof, and defense evidence.
10. Use `scripts/dvwa_runner.py --mode walkthrough` only after completing the above model, or when the user explicitly asks for a helper smoke test.
11. Use `--mode fast` only for smoke tests and regression checks.

## Tool-Orchestration Mindset

The agent should know what each tool contributes:

- **Browser/DevTools**: DOM sinks, JavaScript transformations, CSP, visual proof, storage/cookies.
- **Burp Suite**: proxy history, request replay, parameter mutation, Intruder-style fuzzing, token-aware manual workflows, MCP integration when available.
- **OWASP ZAP**: proxy, spidering, passive scan, replay, API-driven checks.
- **Python/requests**: session-aware harnesses, token refresh, repeatable tests, report generation.
- **ffuf**: content and parameter fuzzing after the request shape is understood.
- **sqlmap**: SQL injection automation after a manual proof and authenticated request export.
- **IDA**: binary reversing tasks only; not PHP web modules.
- **MCP**: optional control plane for tools already running; never assume it exists.

Tool use must follow hypotheses. Do not run tools because they are available.

## Unseen Module Strategy

When there is no module-specific helper:

1. Load the module's `references/knowledge-base/<module>/guide.md` if it exists.
2. Inspect the live page and source.
3. Write a small local test plan in the response before broad automation.
4. Use Burp/ZAP/browser/Python manually or semi-automatically.
5. If repeatable logic emerges, write a temporary harness. Promote it into `scripts/` only when the user explicitly wants a reusable helper.

## What Not To Do

- Do not treat public walkthroughs as payload libraries to replay blindly.
- Do not run a scanner before understanding the request shape.
- Do not use default credentials as the first brute-force attempt during evaluation.
- Do not call sqlmap for Brute Force.
- Do not call IDA for PHP web modules.
- Do not omit failed probes from the report.
