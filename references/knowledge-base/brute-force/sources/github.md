# Brute Force - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\??????5\1earn\1earn\Security\RedTeam\Web???\???\DVWA-WalkThrough.md`
- Section: `Brute_Force`
- Lines: `72-461`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/brute/`
- GitHub section selector: `Brute_Force`
- Knowledge-base directory: `brute-force`

## Source Section Outline

- Line 72: `## Brute_Force`
- Line 76: `### Low`
- Line 136: `### Medium`
- Line 185: `### High`
- Line 346: `### Impossible`

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/brute/` after setting security to low.
2. Observe that the form submits `username`, `password`, and `Login` through a GET request.
3. Send a known-wrong credential and record the failure marker. DVWA commonly returns an incorrect username/password message.
4. Send generated username/password pairs. Start with lab-relevant usernames such as `admin`, then common passwords such as `password`, unless the user provides wordlists.
5. Classify success by the protected-area welcome marker rather than by HTTP status alone.
6. Report the found pair, request count, parameter names, and the absence of throttling/token requirements.

### Medium

1. Repeat the low-level request mapping, but watch response time and source behavior.
2. Expect basic escaping and a delay such as `sleep`, meaning large wordlists are slower.
3. Keep attempts conservative and record timing behavior in the report.
4. Continue using response-marker classification; do not depend on visible redirects only.

### High

1. Load the module page before each credential attempt.
2. Parse the fresh hidden `user_token` from the form.
3. Submit `username`, `password`, `Login`, and that fresh token in the same session.
4. If a request fails unexpectedly, reload the form and retry with a new token before concluding the credential failed.
5. Report token handling as a bypass requirement and include a note that token freshness prevents naive replay but not necessarily automated testing.

### Impossible

1. Confirm the page uses stronger controls such as token checks, prepared queries, failed-login counters, lockout, or stricter validation.
2. Test only enough attempts to prove defensive behavior; do not turn this into a large brute-force run.
3. If a known-valid credential logs in, classify it as `credential_valid`, not as a brute-force vulnerability.
4. Report lockout/throttling/token behavior and why automated brute force is not practically exploitable at this level.

### Tool process

1. Use a generated Python/requests harness or Burp workflow after inspection; `scripts/dvwa_runner.py` is only a reference/regression helper.
2. Add `--proxy http://127.0.0.1:8080` to capture traffic in Burp or ZAP.
3. Add `--export-tool-artifacts` to write raw request and ffuf examples.
4. Use Burp Repeater to inspect one attempt, and Intruder only with a fresh-token strategy or macro for high/impossible.

## Local Images

![GitHub WalkThrough brute-force 1](./images/github-01.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa5.png

![GitHub WalkThrough brute-force 2](./images/github-02.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa6.png

![GitHub WalkThrough brute-force 3](./images/github-03.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa7.png

![GitHub WalkThrough brute-force 4](./images/github-04.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa8.png

![GitHub WalkThrough brute-force 5](./images/github-05.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa9.png

![GitHub WalkThrough brute-force 6](./images/github-06.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa10.png

![GitHub WalkThrough brute-force 7](./images/github-07.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa11.png

![GitHub WalkThrough brute-force 8](./images/github-08.png)

Original: D:\WorkSpace\??????5\1earn\assets\img\Security\RedTeam\Web???\???\dvwa\dvwa12.png

