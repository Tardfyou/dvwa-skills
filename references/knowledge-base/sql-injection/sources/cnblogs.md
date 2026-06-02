# SQL Injection - CNBlogs

## Source

https://www.cnblogs.com/chadlas/articles/15724905.html

## Local Source Location

- Local original file not available; use the source URL.

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/sqli/`
- GitHub section selector: `SQL_Injection`
- Knowledge-base directory: `sql-injection`

## Source Section Outline

- Section outline unavailable.

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/sqli/` and submit a normal ID value to learn baseline output.
2. Submit a single quote or quote-breaking probe and record error behavior.
3. Test boolean conditions, for example true/false variants, to prove query control.
4. Determine column count with ordered probes or union-null increments.
5. Use a union select to display controlled values in visible columns.
6. Enumerate DB version, database name, tables, columns, and target rows only inside DVWA.
7. Report every inference step, not only the final extracted data.

### Medium

1. Note that input may come from a select/dropdown and be submitted by POST.
2. Use Burp/ZAP to modify the parameter beyond visible UI values.
3. Check whether numeric context removes quote requirements.
4. Repeat boolean and union mapping with the correct syntax for numeric parameters.
5. Report UI constraints versus server-side validation.

### High

1. Observe whether the injection point is moved into a separate form/window or uses session variables.
2. Capture the exact request flow before testing payloads.
3. Apply the same mapping sequence: baseline, error/boolean, column count, union display, extraction.
4. Report flow requirements and any token/session considerations.

### Impossible

1. Confirm prepared statements or parameterized queries in source.
2. Send quote, boolean, union, and timing probes.
3. Report that injection is not exploitable when probes are treated as data.

### Tool process

Export an authenticated request and run sqlmap conservatively only against the DVWA route. Preserve cookies and security level. Include the sqlmap command and key findings in the report, but still explain the manual proof path.

## Local Images

No module-specific image was found or downloaded for this source.
