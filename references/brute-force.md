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

These are starting hypotheses, not conclusions. Inspect the live page and source for the actual run before classifying a level.

- `low`: Basic GET parameters are often enough, but still confirm request method, markers, and source behavior.
- `medium`: Similar request shape to low may appear, but response timing and filtering must be measured.
- `high`: Token handling often appears; refresh the page and parse a fresh `user_token` only after confirming the level requires it.
- `impossible`: Test whether practical defenses are present and effective. Avoid interpreting known-valid credential login as a brute-force flaw; look for lockout, token validation, prepared statements, and failure messaging. If evidence shows a bypass, report it as vulnerable rather than forcing an unsolvable conclusion.

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
