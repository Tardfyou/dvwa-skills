# File Inclusion - CNBlogs

## Source

https://www.cnblogs.com/chadlas/articles/15719775.html

## Local Source Location

- Local original file not available; use the source URL.

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/fi/`
- GitHub section selector: `File_Inclusion`
- Knowledge-base directory: `file-inclusion`

## Source Section Outline

- Section outline unavailable.

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/fi/` and locate the `page` parameter in navigation links.
2. Load a normal included page and record the baseline URL shape.
3. Replace `page` with a safe local file path that proves read capability, such as a DVWA source file.
4. Try relative traversal sequences to reach files outside the include directory.
5. If remote wrappers are enabled in the lab, test them only with controlled local resources.
6. Report the included file, traversal depth, and whether local/remote inclusion worked.

### Medium

1. Inspect filtering for obvious replacement of `http://`, `https://`, or `../`.
2. Test encoded traversal, doubled traversal strings, or alternative wrappers when a naive replace is present.
3. Confirm the bypass by including a harmless DVWA file.
4. Report the filter weakness and exact transformation observed.

### High

1. Expect allowlist-like behavior around filenames or prefixes.
2. Test whether `file://`, path normalization, or suffix tricks can still include unintended files.
3. Use source review to determine whether the filter checks startswith, contains, or a true allowlist.
4. Report what file classes remain reachable.

### Impossible

1. Confirm only known pages are selectable.
2. Attempt traversal and wrapper payloads and record rejection.
3. Report strict allowlisting as the effective control.

## Local Images

No module-specific image was found or downloaded for this source.
