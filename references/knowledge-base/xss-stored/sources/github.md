# XSS Stored - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `XSS`
- Lines: `2979-3395`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/xss_s/`
- GitHub section selector: `XSS`
- Knowledge-base directory: `xss-stored`

## Source Section Outline

- Line 2979: `## XSS`
- Line 2985: `### XSS(DOM)`
- Line 3002: `#### Low`
- Line 3020: `#### Medium`
- Line 3052: `#### High`
- Line 3080: `#### Impossible`
- Line 3093: `### XSS(Reflected)`
- Line 3097: `#### Low`
- Line 3145: `#### Medium`
- Line 3176: `#### High`
- Line 3198: `#### Impossible`
- Line 3219: `### XSS(Stored)`
- Line 3220: `#### Low`
- Line 3271: `#### Medium`
- Line 3319: `#### High`
- Line 3355: `#### Impossible`

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/xss_s/` and submit a normal guestbook entry.
2. Locate where name/message are stored and rendered after reload.
3. Submit a harmless script proof in the field that accepts enough length.
4. Reload or revisit the page to prove persistence.
5. Clean up test entries if the lab allows it and report storage location.

### Medium

1. Identify field length limits and filters.
2. Use Burp/ZAP to modify client-side length-limited fields when needed.
3. Test alternate tags/event handlers if `<script>` is filtered.
4. Report which field is vulnerable and whether client-side constraints were bypassed.

### High

1. Inspect stricter filters and output context.
2. Use a context-specific payload, often through an event handler or tag variant if allowed by the lab.
3. Prove persistence across reloads and sessions.
4. Report filter limitations and cleanup status.

### Impossible

1. Confirm stored output is escaped and length/format checks are server-side.
2. Submit representative payloads and show safe rendering.
3. Report effective output encoding.

## Local Images

![GitHub WalkThrough xss-stored 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa64.png

![GitHub WalkThrough xss-stored 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa81.png

![GitHub WalkThrough xss-stored 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa65.png
