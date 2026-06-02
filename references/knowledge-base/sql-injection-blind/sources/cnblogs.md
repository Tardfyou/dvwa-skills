# SQL Injection Blind - CNBlogs

## Source

https://www.cnblogs.com/chadlas/articles/15735045.html

## Local Source Location

- Local original file not available; use the source URL.

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

- Section outline unavailable.

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
