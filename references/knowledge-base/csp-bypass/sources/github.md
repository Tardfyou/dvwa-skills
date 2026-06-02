# CSP Bypass - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `CSP_Bypass`
- Lines: `3396-3569`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/csp/`
- GitHub section selector: `CSP_Bypass`
- Knowledge-base directory: `csp-bypass`

## Source Section Outline

- Line 3396: `## CSP_Bypass`
- Line 3404: `### Low`
- Line 3449: `### Medium`
- Line 3478: `### High`
- Line 3538: `### Impossible`

## Complete Process Notes

## Detailed Walkthrough Process

### General process

1. Open `vulnerabilities/csp/` and capture the active `Content-Security-Policy` header or meta tag.
2. List allowed script sources, inline permissions, nonce/hash requirements, and JSONP-capable domains.
3. Test whether normal inline script is blocked.
4. Build a payload only from sources allowed by the policy, such as an allowed JSONP endpoint in the lab guide context.
5. Verify execution in the browser console and report the specific CSP weakness.
6. At impossible/secure levels, show that missing unsafe directives and strict allowlists block execution.

## Local Images

![GitHub WalkThrough csp-bypass 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa66.png

![GitHub WalkThrough csp-bypass 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa67.png

![GitHub WalkThrough csp-bypass 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa68.png

![GitHub WalkThrough csp-bypass 4](./images/github-04.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa69.png

![GitHub WalkThrough csp-bypass 5](./images/github-05.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa70.png

![GitHub WalkThrough csp-bypass 6](./images/github-06.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa71.png
