# Web Lab And CTF Methodology

Use this file for non-DVWA or unseen web-lab tasks. The goal is to guide the agent through a repeatable solving process rather than memorized payloads.

## Phase 1: Recon Inside Scope

- Identify base URL, routes, authentication, roles, cookies, and technologies.
- Map visible pages and forms.
- Check robots, static assets, JavaScript files, API endpoints, and source files if provided.
- Use passive observation before active fuzzing.

## Phase 2: Request Modeling

For each interesting action, record:

- method and URL
- parameters and body encoding
- headers and cookies
- CSRF/token fields
- redirects
- success/failure text
- status codes and response lengths
- client-side transformations

## Phase 3: Source-Aware Hypotheses

When source is available:

- Find the route handler.
- Trace input from request to sink.
- Identify sanitization, validation, escaping, auth checks, rate limits, and state changes.
- Build the smallest test that confirms or refutes the suspected weakness.

When source is unavailable:

- Use differential probes.
- Compare valid, invalid, boundary, encoded, and malformed inputs.
- Use timing and length differences carefully.

## Phase 4: Vulnerability-Class Playbooks

### Brute Force

- Establish failure marker first.
- Check lockout, delay, token, and captcha.
- Keep known defaults late during evaluation.
- Use token refresh for protected forms.

### Command Injection

- Establish baseline command behavior.
- Test harmless separators and OS-specific proof commands.
- Avoid destructive commands and external callbacks unless the lab explicitly requires them.

### SQL Injection

- Prove manually with boolean/error/timing behavior.
- Use sqlmap only after a scoped authenticated request is captured.
- Keep query count conservative.

### XSS

- Identify context: HTML text, attribute, URL, script, DOM sink.
- Use harmless proof payloads.
- Confirm in browser or DOM, not only raw response.

### File Upload

- Separate extension, MIME type, content validation, storage path, and execution behavior.
- Use benign proof files first.

### File Inclusion

- Identify include parameter and allowed base path.
- Test traversal/wrapper behavior with harmless local files.

### CSRF

- Identify state-changing action.
- Check tokens, SameSite, Origin/Referer, and current-password requirements.

### Weak Session

- Collect samples.
- Analyze sequence, timestamp, hash, randomness, and predictability.

## Phase 5: Tool Selection

- Browser/DevTools for client-side and visual proof.
- Burp/ZAP for traffic, replay, mutation, and evidence.
- Python harness for repeatable authenticated flows.
- ffuf for scoped fuzzing after request shape is known.
- sqlmap for SQLi after manual proof.
- IDA only for binaries.

## Phase 6: Reporting

Always report:

- scope
- observations
- source review
- hypothesis
- tests generated
- tools used
- evidence
- conclusion
- remediation
- limitations and next steps
