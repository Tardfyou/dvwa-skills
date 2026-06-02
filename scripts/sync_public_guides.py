#!/usr/bin/env python3
"""Build the DVWA public-guide knowledge base.

The generated knowledge base stores source links, source-derived testing notes,
locally mirrored public-guide images, and detailed paraphrased walkthrough
processes per DVWA module. It intentionally does not mirror full third-party
articles verbatim; Codex should use the source links for attribution and deeper
inspection when needed.
"""

from __future__ import annotations

import re
import json
import shutil
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parents[1]
KB_ROOT = ROOT / "references" / "knowledge-base"
CNBLOGS_INDEX = "https://www.cnblogs.com/chadlas/p/15707475.html"
GITHUB_WEB = "https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md"
GITHUB_RAW = "https://raw.githubusercontent.com/ffffffff0x/1earn/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md"


@dataclass(frozen=True)
class Module:
    slug: str
    title: str
    cnblogs_url: Optional[str]
    github_heading: str
    route: str
    notes: List[str]


@dataclass(frozen=True)
class MarkdownSection:
    heading: str
    start_line: int
    end_line: int
    text: str
    images: List[str]


MODULES: List[Module] = [
    Module(
        "setup",
        "DVWA Setup And Usage",
        CNBLOGS_INDEX,
        "???/???",
        "setup.php / login.php / security.php",
        [
            "Prefer phpStudy/XAMPP-style Windows labs; confirm DVWA login is reachable before module testing.",
            "Default lab credentials are commonly admin/password, but always use the user-provided values.",
            "Set security level through DVWA UI or `security.php` before each module run.",
        ],
    ),
    Module(
        "brute-force",
        "Brute Force",
        "https://www.cnblogs.com/chadlas/articles/15706231.html",
        "Brute_Force",
        "vulnerabilities/brute/",
        [
            "Low/medium can be tested with repeated credential attempts; medium may add delay and escaping.",
            "High/impossible require fresh `user_token` handling before attempts.",
            "Use response differences such as success text, length, lockout messages, and timing as evidence.",
            "For impossible, treat valid credentials as authentication success, not proof of a brute-force flaw.",
        ],
    ),
    Module(
        "command-injection",
        "Command Injection",
        "https://www.cnblogs.com/chadlas/articles/15706124.html",
        "Command_Injection",
        "vulnerabilities/exec/",
        [
            "Start with harmless OS-discovery payloads against the IP field in the DVWA lab only.",
            "Low generally accepts command separators; medium/high demonstrate blacklist bypass behavior.",
            "On Windows labs, validate with commands like `whoami` or `ipconfig`; avoid destructive commands.",
            "Impossible should validate strict IP parsing and CSRF/token defenses.",
        ],
    ),
    Module(
        "csrf",
        "CSRF",
        "https://www.cnblogs.com/chadlas/articles/15708801.html",
        "CSRF",
        "vulnerabilities/csrf/",
        [
            "Model the password-change request and check whether state change works without an anti-CSRF token.",
            "Use authenticated sessions and controlled local proof pages for testing.",
            "Higher levels add referer/token checks; record which header or token is required.",
        ],
    ),
    Module(
        "file-inclusion",
        "File Inclusion",
        "https://www.cnblogs.com/chadlas/articles/15719775.html",
        "File_Inclusion",
        "vulnerabilities/fi/",
        [
            "Probe the `page` parameter with safe local files first, then source files inside DVWA.",
            "Track whether filtering is blacklist, prefix/suffix based, or strict allowlisting.",
            "Record path traversal, stream wrapper, and null-byte behavior only inside the lab context.",
        ],
    ),
    Module(
        "file-upload",
        "File Upload",
        "https://www.cnblogs.com/chadlas/articles/15720878.html",
        "File_Upload",
        "vulnerabilities/upload/",
        [
            "Test content type, extension, server-side path, and execution behavior separately.",
            "Use benign proof files first; PHP execution checks should be minimal and lab-local.",
            "Higher levels may validate extension, MIME type, image dimensions, or re-encode files.",
        ],
    ),
    Module(
        "insecure-captcha",
        "Insecure CAPTCHA",
        "https://www.cnblogs.com/chadlas/articles/15722429.html",
        "Insecure_Captcha",
        "vulnerabilities/captcha/",
        [
            "Observe multi-step state changes and whether captcha validation is tied to the final action.",
            "Replay or tamper with hidden fields only inside an authenticated DVWA session.",
            "Higher levels should bind validation server-side and reject stale or missing captcha proof.",
        ],
    ),
    Module(
        "sql-injection",
        "SQL Injection",
        "https://www.cnblogs.com/chadlas/articles/15724905.html",
        "SQL_Injection",
        "vulnerabilities/sqli/",
        [
            "Map parameter behavior with boolean, union, and error-based probes before escalating tools.",
            "Use sqlmap only from an exported authenticated request and keep scope to the DVWA route.",
            "Classify whether defenses are escaping, prepared statements, token checks, or allowlisting.",
        ],
    ),
    Module(
        "sql-injection-blind",
        "SQL Injection Blind",
        "https://www.cnblogs.com/chadlas/articles/15735045.html",
        "SQL_Injection\\(Blind\\)",
        "vulnerabilities/sqli_blind/",
        [
            "Prefer boolean and timing probes with small request counts; record response/timing deltas.",
            "Automated tools should use authenticated requests and conservative rate settings.",
            "Impossible should demonstrate parameterization or strict handling that removes inference.",
        ],
    ),
    Module(
        "weak-session-ids",
        "Weak Session IDs",
        "https://www.cnblogs.com/chadlas/articles/15740487.html",
        "Weak_Session_IDs",
        "vulnerabilities/weak_id/",
        [
            "Collect multiple generated session IDs and analyze predictability, monotonicity, and entropy.",
            "Use tables or plots in reports for observed sequence behavior.",
            "Do not reuse discovered sessions outside the local DVWA lab.",
        ],
    ),
    Module(
        "xss-dom",
        "XSS DOM",
        "https://www.cnblogs.com/chadlas/articles/15755444.html",
        "XSS",
        "vulnerabilities/xss_d/",
        [
            "Treat DOM XSS as client-side sink discovery; inspect URL fragments and query parameters.",
            "Use harmless payloads such as `alert(document.domain)` only in the local lab browser.",
            "Record source-to-sink path, affected browser context, and filtering behavior.",
        ],
    ),
    Module(
        "xss-reflected",
        "XSS Reflected",
        "https://www.cnblogs.com/chadlas/articles/15756337.html",
        "XSS",
        "vulnerabilities/xss_r/",
        [
            "Submit reflected input and inspect whether output encoding is absent, partial, or contextual.",
            "Vary payload context across HTML text, attributes, script blocks, and URL contexts.",
            "Use browser evidence plus response snippets in reports.",
        ],
    ),
    Module(
        "xss-stored",
        "XSS Stored",
        "https://www.cnblogs.com/chadlas/articles/15756338.html",
        "XSS",
        "vulnerabilities/xss_s/",
        [
            "Create, reload, and revisit records to prove persistence.",
            "Use minimal harmless payloads and clean up test entries when possible.",
            "Track input length, server-side filtering, stored location, and execution context.",
        ],
    ),
    Module(
        "csp-bypass",
        "CSP Bypass",
        None,
        "CSP_Bypass",
        "vulnerabilities/csp/",
        [
            "Inspect the active Content-Security-Policy and identify allowed script sources.",
            "Test bypass hypotheses with controlled local payloads and browser console evidence.",
            "Report exact CSP directives and why the bypass did or did not work.",
        ],
    ),
    Module(
        "javascript-attacks",
        "JavaScript Attacks",
        None,
        "JavaScript_Attacks",
        "vulnerabilities/javascript/",
        [
            "Read the page JavaScript before sending requests; identify client-side transformations.",
            "Reproduce transformed parameters in Python or browser devtools rather than hard-coding.",
            "Use source review and request evidence to explain the bypass.",
        ],
    ),
]

DETAILS: Dict[str, str] = {
    "setup": """
## Detailed Walkthrough Process

### Lab preparation

1. Start the local Windows web stack that hosts DVWA, for example phpStudy, XAMPP, WAMP, Docker Desktop, or a local VM.
2. Open the DVWA base URL in a browser and confirm `login.php` loads.
3. If DVWA has not been initialized, open `setup.php` and create/reset the database.
4. Log in with the user-provided account. Common public-lab defaults are `admin` / `password`, but never assume them when the user supplies different credentials.
5. Open `security.php`, set the requested difficulty, submit, and verify the selected level is reflected in the page/session.
6. For automated testing, keep the same base URL, cookies, `PHPSESSID`, and `security` cookie in one session.

### Source-code orientation

1. Locate the DVWA root, commonly under `D:\\xampp\\htdocs\\DVWA`, `D:\\phpstudy_pro\\WWW\\DVWA`, or a cloned `DVWA` repository.
2. Each module normally has a route under `vulnerabilities/<module>/` and source variants under `vulnerabilities/<module>/source/<level>.php`.
3. Read the matching source level before building payloads. Use it to understand validation and tokens, but still verify behavior through HTTP requests.

### Reporting baseline

Record target URL, login account name, selected difficulty, module route, source path, date, tool commands, proxy settings, and screenshots/images used as supporting evidence.
""",
    "brute-force": """
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
""",
    "command-injection": """
## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/exec/` and identify the IP/input parameter submitted by the ping form.
2. Submit a normal value such as `127.0.0.1` and record the baseline command output.
3. Test command separators one at a time: `&`, `&&`, `|`, `||`, `;` depending on the lab OS.
4. On Windows, use harmless proof commands such as `whoami`, `hostname`, or `ipconfig`; on Linux, use `id`, `whoami`, or `uname -a`.
5. Confirm injection only when both the original ping behavior and injected command output appear.
6. Report the exact separator family that worked, OS assumptions, and response evidence.

### Medium

1. Inspect source or behavior for blacklist filtering.
2. Test whether obvious separators are removed while alternate separators or spacing still work.
3. Try separators with URL encoding, missing spaces, or alternate chaining forms when the page blocks only specific substrings.
4. Keep every command non-destructive and local to the lab.
5. Report the blacklist gap rather than only the final payload.

### High

1. Expect a stricter but still imperfect filter.
2. Compare blocked and accepted payloads to infer whether spaces around separators matter.
3. Use the smallest proof command possible after the separator bypass is found.
4. Record which characters were filtered and which variant survived.

### Impossible

1. Confirm the server validates the input as an IP address or uses a safe command execution pattern.
2. Try malformed IPs and separator payloads to prove they are rejected.
3. Report that command execution could not be reached and identify the defensive control.

### Tool process

Use Burp/ZAP to replay the form request and compare responses. Use OS command output as proof only in the DVWA host context. Do not use destructive commands, persistence commands, or external callbacks for this lab module.
""",
    "csrf": """
## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/csrf/` and observe the password-change form.
2. Submit a controlled new password and capture the request parameters.
3. Rebuild the request as a link or simple HTML form from another local page.
4. While authenticated to DVWA in the same browser, trigger that crafted request.
5. Attempt login with the new password to prove state change.
6. Restore the original password and report that the action lacks anti-CSRF protection.

### Medium

1. Identify any referer/origin check in source or response behavior.
2. Replay the request with and without Referer to see whether DVWA enforces a host substring check.
3. If bypassable, use a same-host or referer-shaped local proof page depending on the lab setup.
4. Record the exact header condition required.

### High

1. Inspect the form for `user_token`.
2. Confirm a direct replay without the current token fails.
3. Build the proof around first obtaining or reusing a valid token in the authenticated session.
4. Report whether token extraction is possible from same-origin pages and whether CSRF remains practical.

### Impossible

1. Confirm password change requires the current password and a valid token.
2. Attempt stale/missing token and wrong-current-password cases.
3. Report that the attack path is blocked by server-side validation.
""",
    "file-inclusion": """
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
""",
    "file-upload": """
## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/upload/` and upload a benign text/image file to learn the destination path.
2. Check whether the server exposes the uploaded file under `hackable/uploads/`.
3. Upload a minimal PHP proof file in the lab and request it directly.
4. Confirm execution with a harmless output marker, not destructive commands.
5. Report upload path, execution path, filename handling, and absence of extension/MIME validation.

### Medium

1. Observe browser-side and server-side MIME/extension checks.
2. Test content type tampering through Burp/ZAP while keeping the filename controlled.
3. Try image extensions containing PHP content only to prove validation weakness in the lab.
4. Report whether MIME type, extension, or content was trusted.

### High

1. Expect image validation or extension allowlisting.
2. Try a valid image container with controlled metadata or extension tricks only if the lab source indicates that path.
3. Verify whether uploaded content is reprocessed, renamed, or stored safely.
4. Report which validation layer blocked or allowed execution.

### Impossible

1. Confirm the server validates type, size, extension, and image content and renames/reprocesses files.
2. Upload invalid and valid files to prove enforcement.
3. Report that execution is blocked and why.
""",
    "insecure-captcha": """
## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/captcha/` and map the password-change workflow.
2. Submit the first step and observe hidden fields or step markers in the second request.
3. Replay or forge the final password-change request without solving captcha when the server trusts client-side state.
4. Log out/in or attempt the changed password to prove success.
5. Restore credentials and report that captcha is not bound to the final server-side action.

### Medium

1. Inspect which hidden field or step value indicates captcha validation.
2. Modify that value through Burp/ZAP and submit the final request.
3. Verify whether the server trusts the client-supplied validation result.
4. Report the trusted-client-state flaw.

### High

1. Identify any bypass/debug parameter or alternate branch in source.
2. Test whether special parameter values skip captcha validation.
3. Keep the proof limited to password change in the lab account.
4. Report the hidden bypass condition.

### Impossible

1. Confirm captcha validation is checked server-side at the final action.
2. Attempt missing, stale, or forged validation state.
3. Report that the state is bound correctly.
""",
    "sql-injection": """
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
""",
    "sql-injection-blind": """
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
""",
    "weak-session-ids": """
## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/weak_id/`.
2. Click the generate button repeatedly and record each `dvwaSession` value.
3. Look for a simple incrementing sequence.
4. Predict the next value and verify after the next generation.
5. Report predictability and sample sequence.

### Medium

1. Generate multiple IDs and inspect whether values resemble timestamps.
2. Compare values with current Unix time or encoded time formats.
3. Predict a narrow next range and verify.
4. Report time dependency and entropy weakness.

### High

1. Generate many IDs and check whether hashes hide a predictable counter/source.
2. Test likely transforms such as MD5 of incrementing numbers if source review suggests it.
3. Report predictability only when the transform and source are demonstrated.

### Impossible

1. Collect a larger sample and check for strong randomness.
2. Report no practical prediction if values are generated from secure random bytes.
3. Include sample size and analysis method.
""",
    "xss-dom": """
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
""",
    "xss-reflected": """
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
""",
    "xss-stored": """
## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/xss_s/` and submit a normal guestbook entry.
2. Locate where name/message are stored and rendered after reload.
3. Submit a harmless script proof in the field that accepts enough length.
4. Reload or revisit the page to prove persistence.
5. Clean up test entries if the lab allows it and report storage location.

### Medium

1. Identify field length limits and filters.
2. Use Burp/ZAP to modify client-side length-limited fields when needed.
3. Test alternate tags/event handlers if `<script>` is filtered.
4. Report which field is vulnerable and whether client-side constraints were bypassed.

### High

1. Inspect stricter filters and output context.
2. Use a context-specific payload, often through an event handler or tag variant if allowed by the lab.
3. Prove persistence across reloads and sessions.
4. Report filter limitations and cleanup status.

### Impossible

1. Confirm stored output is escaped and length/format checks are server-side.
2. Submit representative payloads and show safe rendering.
3. Report effective output encoding.
""",
    "csp-bypass": """
## Detailed Walkthrough Process

### General process

1. Open `vulnerabilities/csp/` and capture the active `Content-Security-Policy` header or meta tag.
2. List allowed script sources, inline permissions, nonce/hash requirements, and JSONP-capable domains.
3. Test whether normal inline script is blocked.
4. Build a payload only from sources allowed by the policy, such as an allowed JSONP endpoint in the lab guide context.
5. Verify execution in the browser console and report the specific CSP weakness.
6. At impossible/secure levels, show that missing unsafe directives and strict allowlists block execution.
""",
    "javascript-attacks": """
## Detailed Walkthrough Process

### General process

1. Open `vulnerabilities/javascript/` and inspect the page JavaScript before submitting anything.
2. Identify client-side transformations, token construction, hashing, or parameter rewriting.
3. Reproduce the transformation manually in browser devtools or Python.
4. Submit the correctly transformed value and verify the server-side response.
5. For higher levels, read minified/obfuscated code, pretty-print it, and isolate the validation function.
6. Report the transformation path and why client-side-only protection is insufficient.
""",
}


class CnblogsImageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.images: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "img":
            return
        data = {key.lower(): value or "" for key, value in attrs}
        src = data.get("data-src") or data.get("src")
        if not src:
            return
        url = urljoin(self.base_url, src)
        if "img202" not in url:
            return
        if "cnblogs.com/blog/2640905/" not in url:
            return
        if url not in self.images:
            self.images.append(url)


def fetch_text(url: str) -> str:
    last_error: Optional[Exception] = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(iri_to_uri(url), headers={"User-Agent": "dvwa-skill-sync/0.1"})
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            last_error = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"failed to fetch text after retries: {url}: {last_error}")


def fetch_bytes(url: str) -> bytes:
    last_error: Optional[Exception] = None
    for attempt in range(3):
        try:
            request = urllib.request.Request(iri_to_uri(url), headers={"User-Agent": "dvwa-skill-sync/0.1"})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except Exception as exc:
            last_error = exc
            time.sleep(1 + attempt)
    raise RuntimeError(f"failed to fetch bytes after retries: {url}: {last_error}")


def iri_to_uri(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(urllib.parse.unquote(parsed.path), safe="/%")
    query = urllib.parse.quote(urllib.parse.unquote(parsed.query), safe="=&?/%:+")
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, query, parsed.fragment))


def cnblogs_images(url: Optional[str]) -> List[str]:
    if not url:
        return []
    parser = CnblogsImageParser(url)
    try:
        parser.feed(fetch_text(url))
    except Exception as exc:
        print(f"[WARN] Failed to fetch CNBlogs page {url}: {exc}", file=sys.stderr)
    return parser.images


def github_images_by_heading(markdown: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current = ""
    raw_base = GITHUB_RAW.rsplit("/", 1)[0] + "/"
    for line in markdown.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if not current:
            continue
        for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", line):
            href = match.group(1).strip()
            if href.startswith("http://") or href.startswith("https://"):
                image = href
            else:
                image = urljoin(raw_base, href)
            if image not in sections[current]:
                sections[current].append(image)
    return sections


def split_markdown_sections(markdown: str) -> Dict[str, MarkdownSection]:
    lines = markdown.splitlines()
    starts: List[tuple[str, int]] = []
    for index, line in enumerate(lines, start=1):
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            starts.append((match.group(1).strip(), index))
    sections: Dict[str, MarkdownSection] = {}
    for pos, (heading, start_line) in enumerate(starts):
        end_line = starts[pos + 1][1] - 1 if pos + 1 < len(starts) else len(lines)
        section_text = "\n".join(lines[start_line - 1 : end_line])
        images = [m.group(1).strip() for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", section_text)]
        sections[heading] = MarkdownSection(heading, start_line, end_line, section_text, images)
    return sections


def find_local_github_walkthrough() -> Optional[Path]:
    candidates = [
        ROOT.parent / "1earn" / "1earn" / "Security" / "RedTeam" / "Web???" / "???" / "DVWA-WalkThrough.md",
        ROOT / ".." / "1earn" / "1earn" / "Security" / "RedTeam" / "Web???" / "???" / "DVWA-WalkThrough.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    for candidate in ROOT.parent.rglob("DVWA-WalkThrough.md"):
        if "1earn" in [part.lower() for part in candidate.parts]:
            return candidate.resolve()
    return None


def source_image_ref(markdown_path: Optional[Path], image: str) -> str:
    if image.startswith("http://") or image.startswith("https://"):
        return image
    if markdown_path:
        local = (markdown_path.parent / image).resolve()
        if local.exists():
            return str(local)
    return urljoin(GITHUB_RAW.rsplit("/", 1)[0] + "/", image)


def github_images_for(
    module: Module,
    sections: Dict[str, Sequence[str]],
    markdown_path: Optional[Path] = None,
) -> List[str]:
    pattern = re.compile("^" + module.github_heading + "$", re.IGNORECASE)
    images: List[str] = []
    for heading, section_images in sections.items():
        if pattern.match(heading):
            images.extend(source_image_ref(markdown_path, image) for image in section_images)
    if module.slug.startswith("xss-"):
        images.extend(source_image_ref(markdown_path, image) for image in sections.get("XSS", []))
    return list(dict.fromkeys(images))


def github_section_for(module: Module, sections: Dict[str, MarkdownSection]) -> Optional[MarkdownSection]:
    pattern = re.compile("^" + module.github_heading + "$", re.IGNORECASE)
    for heading, section in sections.items():
        if pattern.match(heading):
            return section
    if module.slug.startswith("xss-"):
        return sections.get("XSS")
    return None


def image_extension(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        return suffix
    return ".png"


def mirror_images(module_dir: Path, source: str, urls: List[str]) -> List[tuple[str, str]]:
    images_dir = module_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    mirrored: List[tuple[str, str]] = []
    for index, url in enumerate(urls, start=1):
        filename = f"{source}-{index:02d}{image_extension(url)}"
        path = images_dir / filename
        try:
            if not path.exists():
                parsed = urllib.parse.urlsplit(url)
                if parsed.scheme in {"http", "https"}:
                    path.write_bytes(fetch_bytes(url))
                else:
                    local_source = Path(url)
                    if not local_source.exists():
                        raise FileNotFoundError(url)
                    shutil.copy2(local_source, path)
            mirrored.append((f"./images/{filename}", url))
        except Exception as exc:
            print(f"[WARN] Failed to download image {url}: {exc}", file=sys.stderr)
            mirrored.append((url, f"download-failed: {exc}"))
    return mirrored


def render_module(
    module: Module,
    gh_images: List[tuple[str, str]],
    cb_images: List[tuple[str, str]],
) -> str:
    lines = [
        f"# {module.title}",
        "",
        "## Sources",
        "",
        f"- GitHub WalkThrough: {GITHUB_WEB}",
    ]
    if module.cnblogs_url:
        lines.append(f"- CNBlogs guide: {module.cnblogs_url}")
    lines.extend(
        [
            "",
            "## DVWA Route",
            "",
            f"`{module.route}`",
            "",
            "## Agent Notes",
            "",
        ]
    )
    for note in module.notes:
        lines.append(f"- {note}")
    detail = DETAILS.get(module.slug)
    if detail:
        lines.extend(["", detail.strip(), ""])
    lines.extend(
        [
            "",
            "## Suggested Test Process",
            "",
            "1. Log in to DVWA with the user-provided account.",
            "2. Set the requested security level through `security.php`.",
            "3. Open the module route and inspect visible forms, hidden fields, cookies, and response text.",
            "4. Generate a small hypothesis-driven test set before using external tools.",
            "5. Execute tests through an agent-generated harness, browser, Burp/ZAP proxy, or module-specific CLI tool.",
            "6. Record request evidence, response indicators, and source-code observations in the report.",
            "",
            "## Media From Public Guides",
            "",
        ]
    )
    if cb_images:
        lines.extend(["### CNBlogs", ""])
        for index, (image, original_url) in enumerate(cb_images, start=1):
            lines.append(f"![CNBlogs {module.slug} {index}]({image})")
            lines.append("")
            lines.append(f"Source image: {original_url}")
            lines.append("")
    if gh_images:
        lines.extend(["### GitHub WalkThrough", ""])
        for index, (image, original_url) in enumerate(gh_images, start=1):
            lines.append(f"![GitHub {module.slug} {index}]({image})")
            lines.append("")
            lines.append(f"Source image: {original_url}")
            lines.append("")
    if not cb_images and not gh_images:
        lines.append("No module-specific images were found in the configured public sources.")
    lines.extend(
        [
            "",
            "## Source-Specific Files",
            "",
            "- [GitHub WalkThrough split notes](./sources/github.md)",
        ]
    )
    if module.cnblogs_url:
        lines.append("- [CNBlogs page notes](./sources/cnblogs.md)")
    return "\n".join(lines).rstrip() + "\n"


def render_source_notes(
    module: Module,
    source_name: str,
    source_url: str,
    images: List[tuple[str, str]],
    local_source: Optional[Path] = None,
    section: Optional[MarkdownSection] = None,
) -> str:
    detail = DETAILS.get(module.slug, "").strip()
    lines = [
        f"# {module.title} - {source_name}",
        "",
        "## Source",
        "",
        source_url,
        "",
        "## Local Source Location",
        "",
    ]
    if local_source and section:
        lines.extend(
            [
                f"- File: `{local_source}`",
                f"- Section: `{section.heading}`",
                f"- Lines: `{section.start_line}-{section.end_line}`",
            ]
        )
    elif local_source:
        lines.append(f"- File: `{local_source}`")
    else:
        lines.append("- Local original file not available; use the source URL.")
    lines.extend(
        [
            "",
        "## How This Source Is Used",
        "",
        "- Treat this file as local working notes derived from the public guide source.",
        "- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.",
        "- Use the source link for attribution and to inspect exact third-party wording when needed.",
        "- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.",
        "",
        "## Module Mapping",
        "",
        f"- DVWA route: `{module.route}`",
        f"- GitHub section selector: `{module.github_heading}`",
        f"- Knowledge-base directory: `{module.slug}`",
        "",
        "## Source Section Outline",
        "",
        ]
    )
    if section:
        outline = []
        for line_number, line in enumerate(section.text.splitlines(), start=section.start_line):
            if re.match(r"^#{2,5}\s+", line):
                outline.append(f"- Line {line_number}: `{line.strip()}`")
        lines.extend(outline or ["- No nested headings found."])
    else:
        lines.append("- Section outline unavailable.")
    lines.extend(
        [
            "",
        "## Complete Process Notes",
        "",
        ]
    )
    if detail:
        lines.append(detail)
    else:
        for note in module.notes:
            lines.append(f"- {note}")
    lines.extend(["", "## Local Images", ""])
    if images:
        for index, (image, original_url) in enumerate(images, start=1):
            lines.append(f"![{source_name} {module.slug} {index}]({image})")
            lines.append("")
            lines.append(f"Original: {original_url}")
            lines.append("")
    else:
        lines.append("No module-specific image was found or downloaded for this source.")
    return "\n".join(lines).rstrip() + "\n"


def render_index(modules: Iterable[Module]) -> str:
    lines = [
        "# DVWA Public Guide Knowledge Base",
        "",
        "This directory indexes public DVWA walkthrough knowledge by challenge type.",
        "",
        "Primary sources:",
        f"- CNBlogs DVWA series index: {CNBLOGS_INDEX}",
        f"- GitHub DVWA WalkThrough: {GITHUB_WEB}",
        "",
        "Use these files as source-linked background knowledge. Prefer observing the live DVWA page, source code, and responses before applying any specific technique.",
        "",
        "Each module directory contains:",
        "- `guide.md`: merged local working guide with detailed testing process and local image references.",
        "- `sources/github.md`: split notes for the matching section in the single GitHub WalkThrough document.",
        "- `sources/cnblogs.md`: split notes for the matching CNBlogs series page when one exists.",
        "- `images/`: locally mirrored screenshots from the public guides when available.",
        "",
        "Use `source-map.json` for machine-readable source URLs, local GitHub line ranges, split-note paths, and image counts.",
        "",
        "## Modules",
        "",
    ]
    for module in modules:
        lines.append(f"- [{module.title}](./{module.slug}/guide.md)")
    return "\n".join(lines) + "\n"


def write_source_map(
    modules: Iterable[Module],
    local_github_path: Optional[Path],
    github_sections: Dict[str, MarkdownSection],
) -> None:
    records = []
    for module in modules:
        section = github_section_for(module, github_sections)
        images_dir = KB_ROOT / module.slug / "images"
        records.append(
            {
                "module": module.slug,
                "title": module.title,
                "route": module.route,
                "guide": f"references/knowledge-base/{module.slug}/guide.md",
                "sources": {
                    "github": {
                        "url": GITHUB_WEB,
                        "local_file": str(local_github_path) if local_github_path else None,
                        "heading": section.heading if section else module.github_heading,
                        "start_line": section.start_line if section else None,
                        "end_line": section.end_line if section else None,
                        "split_notes": f"references/knowledge-base/{module.slug}/sources/github.md",
                    },
                    "cnblogs": {
                        "url": module.cnblogs_url,
                        "split_notes": f"references/knowledge-base/{module.slug}/sources/cnblogs.md"
                        if module.cnblogs_url
                        else None,
                    },
                },
                "local_image_count": len(list(images_dir.glob("*"))) if images_dir.exists() else 0,
            }
        )
    (KB_ROOT / "source-map.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    KB_ROOT.mkdir(parents=True, exist_ok=True)
    local_github_path = find_local_github_walkthrough()
    github_markdown_sections: Dict[str, MarkdownSection] = {}
    github_image_sections: Dict[str, Sequence[str]] = {}
    if local_github_path:
        github_markdown = local_github_path.read_text(encoding="utf-8", errors="replace")
        github_markdown_sections = split_markdown_sections(github_markdown)
        github_image_sections = {heading: section.images for heading, section in github_markdown_sections.items()}
        print(f"Using local GitHub WalkThrough: {local_github_path}")
    else:
        try:
            github_markdown = fetch_text(GITHUB_RAW)
            github_image_sections = github_images_by_heading(github_markdown)
            github_markdown_sections = split_markdown_sections(github_markdown)
        except Exception as exc:
            print(f"[WARN] Failed to fetch GitHub WalkThrough: {exc}", file=sys.stderr)
            github_image_sections = {}
            github_markdown_sections = {}

    for module in MODULES:
        module_dir = KB_ROOT / module.slug
        module_dir.mkdir(parents=True, exist_ok=True)
        source_dir = module_dir / "sources"
        source_dir.mkdir(parents=True, exist_ok=True)
        cb_local = mirror_images(module_dir, "cnblogs", cnblogs_images(module.cnblogs_url))
        github_section = github_section_for(module, github_markdown_sections)
        gh_local = mirror_images(
            module_dir,
            "github",
            github_images_for(module, github_image_sections, local_github_path),
        )
        guide = render_module(module, gh_local, cb_local)
        (module_dir / "guide.md").write_text(guide, encoding="utf-8")
        (source_dir / "github.md").write_text(
            render_source_notes(
                module,
                "GitHub WalkThrough",
                GITHUB_WEB,
                gh_local,
                local_source=local_github_path,
                section=github_section,
            ),
            encoding="utf-8",
        )
        if module.cnblogs_url:
            (source_dir / "cnblogs.md").write_text(
                render_source_notes(module, "CNBlogs", module.cnblogs_url, cb_local),
                encoding="utf-8",
            )
    (KB_ROOT / "index.md").write_text(render_index(MODULES), encoding="utf-8")
    write_source_map(MODULES, local_github_path, github_markdown_sections)
    print(f"Wrote knowledge base to {KB_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

