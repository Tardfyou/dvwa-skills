# SQL Injection Blind

## Sources

- GitHub WalkThrough: https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md
- CNBlogs guide: https://www.cnblogs.com/chadlas/articles/15735045.html

## DVWA Route

`vulnerabilities/sqli_blind/`

## Agent Notes

- Prefer boolean and timing probes with small request counts; record response/timing deltas.
- Automated tools should use authenticated requests and conservative rate settings.
- Impossible should demonstrate parameterization or strict handling that removes inference.

## Detailed Walkthrough Process

### Low

1. Submit a normal ID and note the true/exists message.
2. Submit boolean true and false probes and record message differences.
3. Use conditional expressions to infer database properties one bit/character at a time.
4. For time-based checks, use small delays and compare against baseline timing.
5. Report the exact true/false oracle and request count.

### Medium

1. Capture the POST/select request and modify the parameter in Burp/ZAP.
2. Use numeric boolean expressions when quotes are not needed.
3. Repeat inference with conservative request counts.
4. Record whether escaping changes syntax requirements.

### High

1. Track any separate page/session flow and token usage.
2. Confirm the blind oracle still exists before extraction.
3. Use automated inference only after manual true/false proof.
4. Report flow and token handling.

### Impossible

1. Confirm parameterization removes the oracle.
2. Test representative boolean and timing probes.
3. Report absence of distinguishable true/false/timing behavior.


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
