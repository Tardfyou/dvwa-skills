# File Inclusion - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `File_Inclusion`
- Lines: `1012-1214`

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

- Line 1012: `## File_Inclusion`
- Line 1019: `### Low`
- Line 1103: `### Medium`
- Line 1153: `### High`
- Line 1192: `### Impossible`

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

![GitHub WalkThrough file-inclusion 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa15.png

![GitHub WalkThrough file-inclusion 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa16.png

![GitHub WalkThrough file-inclusion 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa17.png

![GitHub WalkThrough file-inclusion 4](./images/github-04.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa18.png

![GitHub WalkThrough file-inclusion 5](./images/github-05.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa19.png

![GitHub WalkThrough file-inclusion 6](./images/github-06.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa20.png

![GitHub WalkThrough file-inclusion 7](./images/github-07.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa21.png

![GitHub WalkThrough file-inclusion 8](./images/github-08.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa22.png

![GitHub WalkThrough file-inclusion 9](./images/github-09.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa23.png
