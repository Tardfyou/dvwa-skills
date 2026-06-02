# DVWA Brute Force Module

## Inputs

Expected user inputs:

- DVWA base URL, for example `http://127.0.0.1/dvwa/`
- DVWA login username and password
- difficulty: `low`, `medium`, `high`, or `impossible`
- optional source path to the DVWA checkout or web root
- optional username/password wordlists

## Behavioral Strategy

Use observation-first testing:

1. Authenticate to DVWA.
2. Set the requested security level.
3. Load `vulnerabilities/brute/`.
4. Parse hidden fields, especially `user_token`.
5. Generate credential test cases.
6. Send attempts and classify responses.
7. Stop on first valid credential unless the user asks for exhaustive enumeration.

## Difficulty Notes

- `low`: Basic GET parameters are typically enough.
- `medium`: Same request shape as low, but slower response behavior may exist.
- `high`: Refresh the page and parse a fresh `user_token` before each attempt.
- `impossible`: Treat as a defense validation case. Avoid interpreting known-valid credential login as a brute-force flaw; look for lockout, token validation, and failure messaging.

## Source Review Hints

When `--source-path` is supplied, inspect likely files under:

- `vulnerabilities/brute/source/low.php`
- `vulnerabilities/brute/source/medium.php`
- `vulnerabilities/brute/source/high.php`
- `vulnerabilities/brute/source/impossible.php`

Record whether the source contains signs of:

- direct SQL interpolation
- escaping or parameterized queries
- `sleep` or rate limiting
- `user_token`
- lockout or failed-login counters

Use source review to guide tests, not to bypass the testing process.
