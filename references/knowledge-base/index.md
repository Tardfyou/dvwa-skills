# DVWA Public Guide Knowledge Base

This directory indexes public DVWA walkthrough knowledge by challenge type.

Primary sources:
- CNBlogs DVWA series index: https://www.cnblogs.com/chadlas/p/15707475.html
- GitHub DVWA WalkThrough: https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

Use these files as source-linked background knowledge. Prefer observing the live DVWA page, source code, and responses before applying any specific technique.

Each module directory contains:
- `guide.md`: merged local working guide with detailed testing process and local image references.
- `sources/github.md`: split notes for the matching section in the single GitHub WalkThrough document.
- `sources/cnblogs.md`: split notes for the matching CNBlogs series page when one exists.
- `images/`: locally mirrored screenshots from the public guides when available.

Use `source-map.json` for machine-readable source URLs, local GitHub line ranges, split-note paths, and image counts.

## Modules

- [DVWA Setup And Usage](./setup/guide.md)
- [Brute Force](./brute-force/guide.md)
- [Command Injection](./command-injection/guide.md)
- [CSRF](./csrf/guide.md)
- [File Inclusion](./file-inclusion/guide.md)
- [File Upload](./file-upload/guide.md)
- [Insecure CAPTCHA](./insecure-captcha/guide.md)
- [SQL Injection](./sql-injection/guide.md)
- [SQL Injection Blind](./sql-injection-blind/guide.md)
- [Weak Session IDs](./weak-session-ids/guide.md)
- [XSS DOM](./xss-dom/guide.md)
- [XSS Reflected](./xss-reflected/guide.md)
- [XSS Stored](./xss-stored/guide.md)
- [CSP Bypass](./csp-bypass/guide.md)
- [JavaScript Attacks](./javascript-attacks/guide.md)
