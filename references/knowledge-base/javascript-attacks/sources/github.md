# JavaScript Attacks - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `JavaScript_Attacks`
- Lines: `3570-3818`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/javascript/`
- GitHub section selector: `JavaScript_Attacks`
- Knowledge-base directory: `javascript-attacks`

## Source Section Outline

- Line 3570: `## JavaScript_Attacks`
- Line 3578: `### Low`
- Line 3725: `### Medium`
- Line 3754: `### High`
- Line 3806: `### Impossible`

## Complete Process Notes

## Detailed Walkthrough Process

### General process

1. Open `vulnerabilities/javascript/` and inspect the page JavaScript before submitting anything.
2. Identify client-side transformations, token construction, hashing, or parameter rewriting.
3. Reproduce the transformation manually in browser devtools or Python.
4. Submit the correctly transformed value and verify the server-side response.
5. For higher levels, read minified/obfuscated code, pretty-print it, and isolate the validation function.
6. Report the transformation path and why client-side-only protection is insufficient.

## Local Images

![GitHub WalkThrough javascript-attacks 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa73.png

![GitHub WalkThrough javascript-attacks 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa74.png
