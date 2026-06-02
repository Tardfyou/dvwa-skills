# Insecure CAPTCHA - CNBlogs

## Source

https://www.cnblogs.com/chadlas/articles/15722429.html

## Local Source Location

- Local original file not available; use the source URL.

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/captcha/`
- GitHub section selector: `Insecure_Captcha`
- Knowledge-base directory: `insecure-captcha`

## Source Section Outline

- Section outline unavailable.

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/captcha/` and map the password-change workflow.
2. Submit the first step and observe hidden fields or step markers in the second request.
3. Replay or forge the final password-change request without solving captcha when the server trusts client-side state.
4. Log out/in or attempt the changed password to prove success.
5. Restore credentials and report that captcha is not bound to the final server-side action.

### Medium

1. Inspect which hidden field or step value indicates captcha validation.
2. Modify that value through Burp/ZAP and submit the final request.
3. Verify whether the server trusts the client-supplied validation result.
4. Report the trusted-client-state flaw.

### High

1. Identify any bypass/debug parameter or alternate branch in source.
2. Test whether special parameter values skip captcha validation.
3. Keep the proof limited to password change in the lab account.
4. Report the hidden bypass condition.

### Impossible

1. Confirm captcha validation is checked server-side at the final action.
2. Attempt missing, stale, or forged validation state.
3. Report that the state is bound correctly.

## Local Images

No module-specific image was found or downloaded for this source.
