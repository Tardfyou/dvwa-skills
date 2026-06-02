# CSRF - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `CSRF`
- Lines: `693-1011`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/csrf/`
- GitHub section selector: `CSRF`
- Knowledge-base directory: `csrf`

## Source Section Outline

- Line 693: `## CSRF`
- Line 697: `### Low`
- Line 761: `### Medium`
- Line 828: `### High`
- Line 955: `### Impossible`

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/csrf/` and observe the password-change form.
2. Submit a controlled new password and capture the request parameters.
3. Rebuild the request as a link or simple HTML form from another local page.
4. While authenticated to DVWA in the same browser, trigger that crafted request.
5. Attempt login with the new password to prove state change.
6. Restore the original password and report that the action lacks anti-CSRF protection.

### Medium

1. Identify any referer/origin check in source or response behavior.
2. Replay the request with and without Referer to see whether DVWA enforces a host substring check.
3. If bypassable, use a same-host or referer-shaped local proof page depending on the lab setup.
4. Record the exact header condition required.

### High

1. Inspect the form for `user_token`.
2. Confirm a direct replay without the current token fails.
3. Build the proof around first obtaining or reusing a valid token in the authenticated session.
4. Report whether token extraction is possible from same-origin pages and whether CSRF remains practical.

### Impossible

1. Confirm password change requires the current password and a valid token.
2. Attempt stale/missing token and wrong-current-password cases.
3. Report that the attack path is blocked by server-side validation.

## Local Images

![GitHub WalkThrough csrf 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa13.png

![GitHub WalkThrough csrf 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa14.png

![GitHub WalkThrough csrf 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa82.png
