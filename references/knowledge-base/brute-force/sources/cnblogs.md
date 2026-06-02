# Brute Force - CNBlogs

## Source

https://www.cnblogs.com/chadlas/articles/15706231.html

## Local Source Location

- Local original file not available; use the source URL.

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/brute/`
- GitHub section selector: `Brute_Force`
- Knowledge-base directory: `brute-force`

## Source Section Outline

- Section outline unavailable.

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/brute/` after setting security to low.
2. Observe that the form submits `username`, `password`, and `Login` through a GET request.
3. Send a known-wrong credential and record the failure marker. DVWA commonly returns an incorrect username/password message.
4. Send generated username/password pairs. Start with lab-relevant usernames such as `admin`, then common passwords such as `password`, unless the user provides wordlists.
5. Classify success by the protected-area welcome marker rather than by HTTP status alone.
6. Report the found pair, request count, parameter names, and the absence of throttling/token requirements.

### Medium

1. Repeat the low-level request mapping, but watch response time and source behavior.
2. Expect basic escaping and a delay such as `sleep`, meaning large wordlists are slower.
3. Keep attempts conservative and record timing behavior in the report.
4. Continue using response-marker classification; do not depend on visible redirects only.

### High

1. Load the module page before each credential attempt.
2. Parse the fresh hidden `user_token` from the form.
3. Submit `username`, `password`, `Login`, and that fresh token in the same session.
4. If a request fails unexpectedly, reload the form and retry with a new token before concluding the credential failed.
5. Report token handling as a bypass requirement and include a note that token freshness prevents naive replay but not necessarily automated testing.

### Impossible

1. Confirm the page uses stronger controls such as token checks, prepared queries, failed-login counters, lockout, or stricter validation.
2. Test only enough attempts to prove defensive behavior; do not turn this into a large brute-force run.
3. If a known-valid credential logs in, classify it as `credential_valid`, not as a brute-force vulnerability.
4. Report lockout/throttling/token behavior and why automated brute force is not practically exploitable at this level.

### Tool process

1. Use a generated Python/requests harness or Burp workflow after inspection; `scripts/dvwa_runner.py` is only a reference/regression helper.
2. Add `--proxy http://127.0.0.1:8080` to capture traffic in Burp or ZAP.
3. Add `--export-tool-artifacts` to write raw request and ffuf examples.
4. Use Burp Repeater to inspect one attempt, and Intruder only with a fresh-token strategy or macro for high/impossible.

## Local Images

![CNBlogs brute-force 1](./images/cnblogs-01.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211214150145934-623858734.png

![CNBlogs brute-force 2](./images/cnblogs-02.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211214151654127-1598804735.png

![CNBlogs brute-force 3](./images/cnblogs-03.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211214151834564-233394262.png

![CNBlogs brute-force 4](./images/cnblogs-04.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211214152844497-1217812249.png

![CNBlogs brute-force 5](./images/cnblogs-05.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211214155704008-1647536893.png

![CNBlogs brute-force 6](./images/cnblogs-06.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211215152912357-893606906.png

![CNBlogs brute-force 7](./images/cnblogs-07.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211215153020781-365882319.png

![CNBlogs brute-force 8](./images/cnblogs-08.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211215152701083-699062776.png

![CNBlogs brute-force 9](./images/cnblogs-09.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211215153850803-1589550959.png

![CNBlogs brute-force 10](./images/cnblogs-10.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211215154105717-103375796.png

![CNBlogs brute-force 11](./images/cnblogs-11.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211215154416891-1145592021.png

![CNBlogs brute-force 12](./images/cnblogs-12.png)

Original: https://img2020.cnblogs.com/blog/2640905/202112/2640905-20211215154453004-75802179.png

