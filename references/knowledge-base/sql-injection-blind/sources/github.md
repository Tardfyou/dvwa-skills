# SQL Injection Blind - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `SQL_Injection(Blind)`
- Lines: `2406-2797`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/sqli_blind/`
- GitHub section selector: `SQL_Injection\(Blind\)`
- Knowledge-base directory: `sql-injection-blind`

## Source Section Outline

- Line 2406: `## SQL_Injection(Blind)`
- Line 2425: `### Low`
- Line 2638: `### Medium`
- Line 2704: `### High`
- Line 2754: `### Impossible`

## Complete Process Notes

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

## Local Images

No module-specific image was found or downloaded for this source.
