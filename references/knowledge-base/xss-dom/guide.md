# XSS DOM

## Sources

- GitHub WalkThrough: https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md
- CNBlogs guide: https://www.cnblogs.com/chadlas/articles/15755444.html

## DVWA Route

`vulnerabilities/xss_d/`

## Agent Notes

- Treat DOM XSS as client-side sink discovery; inspect URL fragments and query parameters.
- Use harmless payloads such as `alert(document.domain)` only in the local lab browser.
- Record source-to-sink path, affected browser context, and filtering behavior.

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/xss_d/` and identify where URL parameters or fragments are written into the DOM.
2. Change the controlled value and observe the rendered DOM, not only server response.
3. Use a harmless script proof such as `alert(document.domain)` in the local lab.
4. Record the source-to-sink path and browser evidence.

### Medium

1. Inspect client-side filtering or server-side blacklist behavior.
2. Test case changes, tag variations, or event-handler contexts depending on the sink.
3. Confirm execution in the browser and document the bypass condition.

### High

1. Expect stricter tag filtering or allowlisting.
2. Inspect JavaScript source to identify allowed values and sink construction.
3. Use context-appropriate payloads rather than random strings.
4. Report the exact DOM sink and encoding failure.

### Impossible

1. Confirm controlled data is encoded or restricted before DOM insertion.
2. Test representative payloads and record safe rendering.
3. Report the applied control.


## Suggested Test Process

1. Log in to DVWA with the user-provided account.
2. Set the requested security level through `security.php`.
3. Open the module route and inspect visible forms, hidden fields, cookies, and response text.
4. Generate a small hypothesis-driven test set before using external tools.
5. Execute tests through an agent-generated harness, browser, Burp/ZAP proxy, or module-specific CLI tool.
6. Record request evidence, response indicators, and source-code observations in the report.

## Media From Public Guides

### GitHub WalkThrough

![GitHub xss-dom 1](./images/github-01.png)

Source image: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa64.png

![GitHub xss-dom 2](./images/github-02.png)

Source image: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa81.png

![GitHub xss-dom 3](./images/github-03.png)

Source image: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa65.png


## Source-Specific Files

- [GitHub WalkThrough split notes](./sources/github.md)
- [CNBlogs page notes](./sources/cnblogs.md)
