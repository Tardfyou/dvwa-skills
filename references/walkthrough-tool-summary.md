# Public Walkthrough Tool Summary

This file summarizes tool usage observed in the local knowledge base built from:

- GitHub single-document walkthrough: `<local 1earn repo>\1earn\Security\RedTeam\Web-security\DVWA-WalkThrough.md`
- CNBlogs DVWA series pages under `references/knowledge-base/*/sources/cnblogs.md`

## Tools Actually Used In The Walkthroughs

### Browser And DevTools

Used across setup, CSP bypass, JavaScript attacks, XSS, and general observation.

Agent capability:

- Open the DVWA module page.
- Observe forms, parameters, cookies, response text, and DOM behavior.
- Use DevTools/F12 manually when browser-side JavaScript, CSP, DOM sinks, or console functions matter.

Manual user requirement:

- If Codex does not have browser-control tooling in the current session, the user must open the page/browser console and paste back observations or screenshots.

### Burp Suite

Used explicitly for Brute Force, Weak Session IDs, SQL Injection request capture/replay, and request tampering in modules such as File Upload, CAPTCHA, XSS Stored, and SQL Injection Blind.

Walkthrough usage patterns:

- Proxy HTTP traffic.
- Send requests to Repeater.
- Send requests to Intruder.
- Mark password payload positions for Brute Force.
- Load a dictionary and compare response length/content.
- Replay captured SQL injection requests with cookies and security level.

Agent capability:

- Run browser traffic or generated harnesses through `http://127.0.0.1:8080` so test traffic appears in Burp.
- Export raw HTTP request templates from generated harnesses or optional helpers.
- Tell the user exactly which request to send to Repeater/Intruder when manual Burp operation is needed.
- If a Burp MCP server is installed and connected, use it for history inspection, request replay, and tool orchestration where available.

Manual user requirement:

- Start Burp Suite.
- Keep the proxy listener on `127.0.0.1:8080`.
- For Intruder-based Brute Force, select the password parameter as the payload position, load the password list, start the attack, then sort/filter by response length or success marker.

### Python Automation

Used explicitly in Brute Force high level for token-aware attempts.

Walkthrough usage patterns:

- Maintain a session.
- Fetch the module page.
- Parse `user_token`.
- Submit username/password/token attempts.
- Optionally proxy Python requests through Burp.

Agent capability:

- Use agent-generated Python/requests harnesses as the primary Brute Force execution path; `scripts/dvwa_runner.py` is a reference/regression helper.
- Generate reports and tool artifacts from the observed request logic.

Manual user requirement:

- Install dependencies with `py -3.11 -m pip install -r scripts\requirements.txt`.
- Provide DVWA URL, DVWA credentials, difficulty, and source path.

### sqlmap

Used in SQL Injection and SQL Injection Blind sections, not Brute Force.

Walkthrough usage patterns:

- Run sqlmap with a URL plus authenticated cookies.
- Run sqlmap from an exported request file.
- Use `--second-url` when the high-level DVWA SQL injection flow submits on one page and renders on another.

Agent capability:

- For SQLi modules only, export authenticated request files and produce conservative sqlmap commands scoped to the DVWA route.
- Explain the manual proof path before using sqlmap.

Manual user requirement:

- Install sqlmap locally.
- Confirm the target is the DVWA lab URL and provide the current `PHPSESSID`/security cookies if not using an exported request.

### Kali/Linux Tooling

The GitHub walkthrough lists Kali as part of the lab environment, but the current skill target is Windows. Treat Kali as optional background context, not a required dependency.

## Tools Not Actually Used In The Walkthroughs

### IDA

IDA does not appear in the DVWA web walkthroughs and is not needed for Brute Force, SQLi, XSS, CSRF, upload, or PHP source review.

Agent capability:

- Mark IDA as optional for future binary reverse-engineering tasks only.
- Do not invoke IDA for DVWA Brute Force.
- If the user later provides a compiled binary challenge, use IDA Free/Home/Pro or an IDA MCP bridge if installed.

Manual user requirement:

- Install IDA only for binary reversing exercises; it is not a Brute Force prerequisite.

### MCP Tools

The public walkthroughs do not use MCP. MCP is an optional orchestration layer for Codex, not part of the original DVWA solution.

Useful optional MCP integrations:

- Burp MCP server: request history, replay, and Burp tool coordination.
- ZAP API/MCP wrapper: spider/passive scan/request replay in an authorized DVWA scope.
- IDA MCP bridge: binary-analysis tasks only, not DVWA Brute Force.

## Brute Force Tool Priority

For DVWA Brute Force, use this order:

1. agent-led analysis plus generated harnesses for all difficulties; `scripts/dvwa_runner.py` only for comparison/regression.
2. Burp proxy capture for observability.
3. Burp Repeater for single-request verification.
4. Burp Intruder only for low/medium or with a token-refresh macro on high/impossible.
5. ffuf only as an exported artifact demonstration for low/medium; it is not the preferred Brute Force solver because high/impossible need per-request token handling.
6. Do not use sqlmap or IDA for Brute Force.


