# XSS DOM - GitHub WalkThrough

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

- DVWA route: `vulnerabilities/xss_d/`
- GitHub section selector: `XSS`
- Knowledge-base directory: `xss-dom`

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

1. Open `vulnerabilities/xss_d/` and identify where URL parameters or fragments are written into the DOM.
2. Change the controlled value and observe the rendered DOM, not only server response.
3. Use a harmless script proof such as `alert(document.domain)` in the local lab.
4. Record the source-to-sink path and browser evidence.

### Medium

1. Inspect client-side filtering or server-side blacklist behavior.
2. Test case changes, tag variations, or event-handler contexts depending on the sink.
3. Confirm execution in the browser and document the bypass condition.

### High

1. Expect stricter tag filtering or allowlisting.
2. Inspect JavaScript source to identify allowed values and sink construction.
3. Use context-appropriate payloads rather than random strings.
4. Report the exact DOM sink and encoding failure.

### Impossible

1. Confirm controlled data is encoded or restricted before DOM insertion.
2. Test representative payloads and record safe rendering.
3. Report the applied control.

## Local Images

![GitHub WalkThrough xss-dom 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa64.png

![GitHub WalkThrough xss-dom 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa81.png

![GitHub WalkThrough xss-dom 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa65.png
