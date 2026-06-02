# Command Injection

## Sources

- GitHub WalkThrough: https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md
- CNBlogs guide: https://www.cnblogs.com/chadlas/articles/15706124.html

## DVWA Route

`vulnerabilities/exec/`

## Agent Notes

- Start with harmless OS-discovery payloads against the IP field in the DVWA lab only.
- Low generally accepts command separators; medium/high demonstrate blacklist bypass behavior.
- On Windows labs, validate with commands like `whoami` or `ipconfig`; avoid destructive commands.
- Impossible should validate strict IP parsing and CSRF/token defenses.

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


## Suggested Test Process

1. Log in to DVWA with the user-provided account.
2. Set the requested security level through `security.php`.
3. Open the module route and inspect visible forms, hidden fields, cookies, and response text.
4. Generate a small hypothesis-driven test set before using external tools.
5. Execute tests through an agent-generated harness, browser, Burp/ZAP proxy, or module-specific CLI tool.
6. Record request evidence, response indicators, and source-code observations in the report.

## Media From Public Guides

No module-specific images were found in the configured public sources.

## Source-Specific Files

- [GitHub WalkThrough split notes](./sources/github.md)
- [CNBlogs page notes](./sources/cnblogs.md)
