# XSS Reflected - GitHub WalkThrough

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

- DVWA route: `vulnerabilities/xss_r/`
- GitHub section selector: `XSS`
- Knowledge-base directory: `xss-reflected`

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

1. Submit a normal name/value and locate the reflection point in the response.
2. Submit a harmless script proof and confirm browser execution.
3. Capture both request and reflected response snippet.
4. Report missing output encoding.

### Medium

1. Identify filtering of obvious `<script>` strings.
2. Test case changes, broken-up tags, alternate tags, or event handlers according to the reflected context.
3. Confirm execution and report the bypassed blacklist condition.

### High

1. Expect regex or tag filtering.
2. Determine the output context first: HTML body, attribute, JavaScript, or URL.
3. Choose a payload that fits that context and avoids blocked tags.
4. Report context and encoding failure.

### Impossible

1. Confirm input is escaped before reflection.
2. Submit representative payloads and show they render as text.
3. Report the encoding function or defensive behavior.

## Local Images

![GitHub WalkThrough xss-reflected 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa64.png

![GitHub WalkThrough xss-reflected 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa81.png

![GitHub WalkThrough xss-reflected 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa65.png
