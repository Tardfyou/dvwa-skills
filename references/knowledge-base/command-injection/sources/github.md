# Command Injection - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `Command_Injection`
- Lines: `462-692`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/exec/`
- GitHub section selector: `Command_Injection`
- Knowledge-base directory: `command-injection`

## Source Section Outline

- Line 462: `## Command_Injection`
- Line 466: `### Low`
- Line 520: `### Medium`
- Line 578: `### High`
- Line 631: `### Impossible`

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/exec/` and identify the IP/input parameter submitted by the ping form.
2. Submit a normal value such as `127.0.0.1` and record the baseline command output.
3. Test command separators one at a time: `&`, `&&`, `|`, `||`, `;` depending on the lab OS.
4. On Windows, use harmless proof commands such as `whoami`, `hostname`, or `ipconfig`; on Linux, use `id`, `whoami`, or `uname -a`.
5. Confirm injection only when both the original ping behavior and injected command output appear.
6. Report the exact separator family that worked, OS assumptions, and response evidence.

### Medium

1. Inspect source or behavior for blacklist filtering.
2. Test whether obvious separators are removed while alternate separators or spacing still work.
3. Try separators with URL encoding, missing spaces, or alternate chaining forms when the page blocks only specific substrings.
4. Keep every command non-destructive and local to the lab.
5. Report the blacklist gap rather than only the final payload.

### High

1. Expect a stricter but still imperfect filter.
2. Compare blocked and accepted payloads to infer whether spaces around separators matter.
3. Use the smallest proof command possible after the separator bypass is found.
4. Record which characters were filtered and which variant survived.

### Impossible

1. Confirm the server validates the input as an IP address or uses a safe command execution pattern.
2. Try malformed IPs and separator payloads to prove they are rejected.
3. Report that command execution could not be reached and identify the defensive control.

### Tool process

Use Burp/ZAP to replay the form request and compare responses. Use OS command output as proof only in the DVWA host context. Do not use destructive commands, persistence commands, or external callbacks for this lab module.

## Local Images

No module-specific image was found or downloaded for this source.
