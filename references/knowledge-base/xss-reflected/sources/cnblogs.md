# XSS Reflected - CNBlogs

## Source

https://www.cnblogs.com/chadlas/articles/15756337.html

## Local Source Location

- Local original file not available; use the source URL.

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

- Section outline unavailable.

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

No module-specific image was found or downloaded for this source.
