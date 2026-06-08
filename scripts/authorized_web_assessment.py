#!/usr/bin/env python3
"""Authorized web assessment inventory helper.

This script crawls only the supplied origin, captures screenshots, records
forms/links/scripts/API hints, optionally runs ZAP spider/passive collection,
and can trigger ZAP active scan when explicitly requested for an authorized
lab target. It writes Markdown and JSON evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Page, sync_playwright


TZ = timezone(timedelta(hours=8))
DEFAULT_HEADERS = {
    "User-Agent": "dvwa-skill-authorized-web-assessment/1.0",
}
SENSITIVE_QUERY_KEYS = {"password", "pass", "pwd", "token", "user_token", "csrf", "secret", "key"}
SECURITY_HEADERS = [
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "strict-transport-security",
]
STATIC_EXTENSIONS = {
    ".js",
    ".mjs",
    ".css",
    ".map",
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pdf",
    ".zip",
}
API_HINT_RE = re.compile(
    r"""(?P<quote>['"])(?P<path>/(?:api|rest|graphql|oauth|auth|login|admin|user|users|product|products|basket|cart|order|orders|search)[^'"<>\s\\]*)""",
    re.IGNORECASE,
)


@dataclass
class CrawlPage:
    url: str
    title: str
    status: int | None
    screenshot: str
    links: list[str]
    forms: list[dict[str, Any]]
    scripts: list[str]
    api_hints: list[str]


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def normalize_url(url: str) -> str:
    parsed = urlsplit(url)
    if not parsed.scheme:
        url = f"http://{url}"
        parsed = urlsplit(url)
    if not parsed.path:
        url = urlunsplit((parsed.scheme, parsed.netloc, "/", "", ""))
    return url


def origin(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def same_origin(url: str, base_origin: str) -> bool:
    return origin(url) == base_origin


def safe_url(url: str) -> str:
    parsed = urlsplit(url)
    pairs = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in SENSITIVE_QUERY_KEYS:
            value = "<redacted>"
        pairs.append((key, value))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(pairs), parsed.fragment))


def slug(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-")
    return cleaned[:90] or fallback


def is_static_asset(url: str) -> bool:
    path = urlsplit(url).path.lower()
    return any(path.endswith(extension) for extension in STATIC_EXTENSIONS)


def extract_api_hints(text: str, current_url: str, base_origin: str) -> list[str]:
    hints: set[str] = set()
    for match in API_HINT_RE.finditer(text):
        absolute = urljoin(current_url, match.group("path"))
        if same_origin(absolute, base_origin):
            hints.add(safe_url(absolute))
    return sorted(hints)


def fetch_script_api_hints(script_urls: list[str], current_url: str, base_origin: str) -> list[str]:
    hints: set[str] = set()
    for script_url in script_urls[:20]:
        try:
            response = requests.get(script_url, headers=DEFAULT_HEADERS, timeout=10)
            content_type = response.headers.get("Content-Type", "")
            if response.status_code >= 400 or "javascript" not in content_type.lower():
                continue
            hints.update(extract_api_hints(response.text[:500000], current_url, base_origin))
        except Exception:
            continue
    return sorted(hints)


def extract_page(page: Page, base_origin: str) -> tuple[str, list[str], list[dict[str, Any]], list[str], list[str]]:
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else ""

    links: list[str] = []
    for tag in soup.find_all(["a", "link"]):
        href = tag.get("href")
        if not href:
            continue
        absolute = urljoin(page.url, href)
        if same_origin(absolute, base_origin) and not is_static_asset(absolute):
            links.append(safe_url(absolute.split("#", 1)[0]))

    scripts: list[str] = []
    for tag in soup.find_all("script"):
        src = tag.get("src")
        if src:
            absolute = urljoin(page.url, src)
            if same_origin(absolute, base_origin):
                scripts.append(safe_url(absolute))

    forms: list[dict[str, Any]] = []
    for idx, form in enumerate(soup.find_all("form"), start=1):
        fields = []
        for field in form.find_all(["input", "textarea", "select", "button"]):
            fields.append(
                {
                    "tag": field.name,
                    "name": field.get("name"),
                    "type": field.get("type"),
                    "id": field.get("id"),
                    "value_present": bool(field.get("value")),
                }
            )
        forms.append(
            {
                "index": idx,
                "method": (form.get("method") or "GET").upper(),
                "action": safe_url(urljoin(page.url, form.get("action") or page.url)),
                "fields": fields,
            }
        )

    api_hints = set(extract_api_hints(html, page.url, base_origin))
    api_hints.update(fetch_script_api_hints(sorted(set(scripts)), page.url, base_origin))

    return title, sorted(set(links)), forms, sorted(set(scripts)), sorted(api_hints)


def request_headline(url: str) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15, allow_redirects=True)
        elapsed = round(time.perf_counter() - started, 3)
        headers = {k.lower(): v for k, v in response.headers.items()}
        return {
            "url": safe_url(url),
            "final_url": safe_url(response.url),
            "status": response.status_code,
            "elapsed_s": elapsed,
            "server": response.headers.get("Server"),
            "content_type": response.headers.get("Content-Type"),
            "security_headers": {name: headers.get(name) for name in SECURITY_HEADERS},
            "missing_security_headers": [name for name in SECURITY_HEADERS if not headers.get(name)],
        }
    except Exception as exc:
        return {"url": safe_url(url), "error": str(exc)}


def crawl_with_playwright(base_url: str, out_dir: Path, max_pages: int) -> list[CrawlPage]:
    screenshots_dir = out_dir / "screenshots" / "crawl"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    base_origin = origin(base_url)
    pages: list[CrawlPage] = []
    queue: deque[str] = deque([base_url])
    seen: set[str] = set()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 900}, ignore_https_errors=True)
        page = context.new_page()

        while queue and len(pages) < max_pages:
            url = queue.popleft()
            if url in seen or not same_origin(url, base_origin) or is_static_asset(url):
                continue
            seen.add(url)
            status: int | None = None
            try:
                response = page.goto(url, wait_until="networkidle", timeout=20000)
                status = response.status if response else None
                title, links, forms, scripts, api_hints = extract_page(page, base_origin)
                screenshot_rel = Path("screenshots") / "crawl" / f"{len(pages)+1:02d}-{slug(urlsplit(url).path, 'root')}.png"
                page.screenshot(path=str(out_dir / screenshot_rel), full_page=True)
                pages.append(
                    CrawlPage(
                        url=safe_url(page.url),
                        title=title,
                        status=status,
                        screenshot=str(screenshot_rel).replace("\\", "/"),
                        links=links,
                        forms=forms,
                        scripts=scripts,
                        api_hints=api_hints,
                    )
                )
                for link in links:
                    if link not in seen and len(seen) + len(queue) < max_pages * 4:
                        queue.append(link)
            except Exception as exc:
                pages.append(
                    CrawlPage(
                        url=safe_url(url),
                        title=f"crawl error: {exc}",
                        status=status,
                        screenshot="",
                        links=[],
                        forms=[],
                        scripts=[],
                        api_hints=[],
                    )
                )

        browser.close()

    return pages


def zap_get(zap_base: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = requests.get(f"{zap_base.rstrip('/')}{path}", params=params or {}, timeout=20)
    response.raise_for_status()
    return response.json()


def run_zap_scan(zap_base: str, target_url: str, max_children: int, timeout_s: int, active: bool) -> dict[str, Any]:
    result: dict[str, Any] = {"enabled": True, "zap_base": zap_base, "active_scan_requested": active}
    try:
        result["version"] = zap_get(zap_base, "/JSON/core/view/version/")
        scan = zap_get(
            zap_base,
            "/JSON/spider/action/scan/",
            {"url": target_url, "maxChildren": str(max_children), "recurse": "true"},
        )
        scan_id = scan.get("scan")
        result["spider_scan_id"] = scan_id
        deadline = time.time() + timeout_s
        status = "0"
        while scan_id is not None and time.time() < deadline:
            status_json = zap_get(zap_base, "/JSON/spider/view/status/", {"scanId": scan_id})
            status = status_json.get("status", "0")
            if status == "100":
                break
            time.sleep(2)
        result["spider_status"] = status

        if active:
            active_scan = zap_get(
                zap_base,
                "/JSON/ascan/action/scan/",
                {"url": target_url, "recurse": "true", "inScopeOnly": "false"},
            )
            active_scan_id = active_scan.get("scan")
            result["active_scan_id"] = active_scan_id
            active_deadline = time.time() + timeout_s
            active_status = "0"
            while active_scan_id is not None and time.time() < active_deadline:
                status_json = zap_get(zap_base, "/JSON/ascan/view/status/", {"scanId": active_scan_id})
                active_status = status_json.get("status", "0")
                if active_status == "100":
                    break
                time.sleep(3)
            result["active_scan_status"] = active_status

        time.sleep(3)
        alerts = zap_get(zap_base, "/JSON/core/view/alerts/", {"baseurl": target_url}).get("alerts", [])
        result["alerts"] = alerts
        result["alerts_by_risk"] = {}
        for alert in alerts:
            risk = alert.get("risk", "Unknown")
            result["alerts_by_risk"][risk] = result["alerts_by_risk"].get(risk, 0) + 1
    except Exception as exc:
        result["error"] = str(exc)
        result["alerts"] = []
        result["alerts_by_risk"] = {}
    return result


def summarize_forms(pages: list[CrawlPage]) -> list[dict[str, Any]]:
    forms = []
    for page in pages:
        for form in page.forms:
            forms.append({"page": page.url, **form})
    return forms


def summarize_scripts(pages: list[CrawlPage]) -> list[str]:
    scripts: set[str] = set()
    for page in pages:
        scripts.update(page.scripts)
    return sorted(scripts)


def summarize_api_hints(pages: list[CrawlPage]) -> list[str]:
    hints: set[str] = set()
    for page in pages:
        hints.update(page.api_hints)
    return sorted(hints)


def write_report(out_dir: Path, data: dict[str, Any]) -> None:
    pages: list[dict[str, Any]] = data["crawl_pages"]
    forms: list[dict[str, Any]] = data["forms"]
    zap = data["zap"]
    header = data["http_baseline"]
    lines: list[str] = []
    lines.extend(
        [
            "# Authorized Web Assessment Report",
            "",
            "## Summary",
            "",
            f"- Target: `{data['target_url']}`",
            f"- Scope origin: `{data['scope_origin']}`",
            f"- Mode: `{data['mode']}`",
            f"- Started: `{data['started_at']}`",
            f"- Finished: `{data['finished_at']}`",
            f"- Elapsed: `{data['elapsed_s']}s`",
            f"- Pages crawled: `{len(pages)}`",
            f"- Forms found: `{len(forms)}`",
            f"- API hints found: `{len(data['api_hints'])}`",
            f"- ZAP alerts: `{len(zap.get('alerts', []))}`",
            "",
            "This run is an evidence-collection helper for an authorized assessment. It performs same-origin crawling, browser screenshots, request/form/API hint inventory, security-header review, optional ZAP spider/passive alert collection, and optional ZAP active scan when requested. It does not replace agent-led testing.",
            "",
            "## Scope And Authorization",
            "",
            "- The operator supplied `--authorized` for this local or explicitly authorized target.",
            "- Requests were constrained to the target origin.",
            f"- ZAP active scan requested: `{zap.get('active_scan_requested', False)}`.",
            "",
            "## HTTP Baseline",
            "",
            f"- Final URL: `{header.get('final_url', '')}`",
            f"- Status: `{header.get('status', '')}`",
            f"- Server: `{header.get('server', '')}`",
            f"- Content-Type: `{header.get('content_type', '')}`",
            f"- Missing security headers: `{', '.join(header.get('missing_security_headers', [])) or 'none'}`",
            "",
            "Security headers observed:",
            "",
        ]
    )
    for key, value in (header.get("security_headers") or {}).items():
        lines.append(f"- `{key}`: `{value or 'missing'}`")

    lines.extend(["", "## Crawled Pages", ""])
    for page in pages:
        lines.extend(
            [
                f"### {page.get('title') or page.get('url')}",
                "",
                f"- URL: `{page.get('url')}`",
                f"- Status: `{page.get('status')}`",
                f"- Links discovered: `{len(page.get('links', []))}`",
                f"- Forms discovered: `{len(page.get('forms', []))}`",
            ]
        )
        if page.get("screenshot"):
            lines.extend(["", f"![{page.get('title') or 'page screenshot'}]({page['screenshot']})", ""])

    lines.extend(["", "## Forms And Inputs", ""])
    if forms:
        for form in forms:
            names = [field.get("name") or field.get("id") or field.get("tag") for field in form.get("fields", [])]
            lines.append(f"- `{form.get('method')}` `{form.get('action')}` from `{form.get('page')}` fields=`{', '.join([str(x) for x in names if x])}`")
    else:
        lines.append("- No HTML forms were discovered during the bounded crawl.")

    lines.extend(["", "## Scripts And API Surface Hints", ""])
    scripts = data["scripts"]
    if scripts:
        for script in scripts[:50]:
            lines.append(f"- `{script}`")
    else:
        lines.append("- No same-origin script URLs were discovered during the bounded crawl.")

    lines.extend(["", "API hints extracted from HTML and same-origin JavaScript:", ""])
    api_hints = data["api_hints"]
    if api_hints:
        for hint in api_hints[:80]:
            lines.append(f"- `{hint}`")
    else:
        lines.append("- No likely same-origin API route hints were extracted.")

    lines.extend(["", "## ZAP Spider And Passive Alerts", ""])
    if zap.get("enabled"):
        if zap.get("error"):
            lines.append(f"- ZAP error: `{zap['error']}`")
        else:
            lines.append(f"- ZAP version: `{zap.get('version', {}).get('version', '')}`")
            lines.append(f"- Spider status: `{zap.get('spider_status', '')}`")
            if zap.get("active_scan_requested"):
                lines.append(f"- Active scan status: `{zap.get('active_scan_status', '')}`")
            lines.append(f"- Alerts by risk: `{json.dumps(zap.get('alerts_by_risk', {}), ensure_ascii=False)}`")
            for alert in zap.get("alerts", [])[:30]:
                lines.extend(
                    [
                        "",
                        f"### {alert.get('alert')}",
                        "",
                        f"- Risk: `{alert.get('risk')}`",
                        f"- Confidence: `{alert.get('confidence')}`",
                        f"- URL: `{safe_url(alert.get('url', ''))}`",
                        f"- Evidence: `{(alert.get('evidence') or '')[:200]}`",
                        f"- Description: {(alert.get('description') or '')[:500]}",
                    ]
                )
    else:
        lines.append("- ZAP collection was disabled for this run.")

    lines.extend(
        [
            "",
            "## Findings Triage",
            "",
            "- `Confirmed`: none from this helper alone; confirmation requires targeted reproduction.",
            "- `Likely/Possible`: ZAP passive alerts and missing headers should be reviewed and verified.",
            "- `Informational`: crawl inventory, forms, scripts, and screenshots.",
            "",
            "## Recommended Next Steps",
            "",
            "1. Review the form/API inventory and choose specific vulnerability hypotheses.",
            "2. Confirm each ZAP passive alert manually or with a targeted browser/request harness.",
            "3. Continue from scanner leads to direct validation with browser/request/source evidence where available.",
            "4. Add authenticated browser state if the application has login-only functionality.",
            "",
            "## Artifacts",
            "",
            "- `report.md`: this report",
            "- `report.json`: machine-readable inventory data",
            "- `screenshots/crawl/`: browser screenshots",
            "",
            "## Limitations",
            "",
            "- This helper is not a full penetration test by itself and should not be treated as the skill's default workflow.",
            "- It does not bypass authentication, solve CAPTCHA/MFA, or infer business-logic vulnerabilities.",
            "- It only covers the pages and tool actions reachable within the configured runtime and timeout.",
            "- Single-page applications may require deeper scripted navigation for complete coverage.",
        ]
    )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an authorized web assessment inventory and ZAP evidence collection.")
    parser.add_argument("--url", required=True, help="Target base URL.")
    parser.add_argument("--out-dir", required=True, help="Output directory.")
    parser.add_argument("--authorized", action="store_true", help="Required confirmation that the target is authorized.")
    parser.add_argument("--mode", default="passive", choices=["passive"], help="Only passive mode is currently implemented.")
    parser.add_argument("--max-pages", type=int, default=12)
    parser.add_argument("--zap-url", default="http://127.0.0.1:8090")
    parser.add_argument("--no-zap", action="store_true")
    parser.add_argument("--zap-active", action="store_true", help="Run ZAP active scan after spidering. Use only for an authorized target.")
    parser.add_argument("--zap-timeout", type=int, default=60)
    args = parser.parse_args()

    if not args.authorized:
        raise SystemExit("Refusing to run without --authorized. Confirm scope before assessing a target.")

    started = time.perf_counter()
    started_at = now_iso()
    target_url = normalize_url(args.url)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline = request_headline(target_url)
    crawl_pages = crawl_with_playwright(target_url, out_dir, args.max_pages)
    forms = summarize_forms(crawl_pages)
    scripts = summarize_scripts(crawl_pages)
    api_hints = summarize_api_hints(crawl_pages)
    zap = {"enabled": False, "alerts": [], "alerts_by_risk": {}}
    if not args.no_zap:
        zap = run_zap_scan(args.zap_url, target_url, args.max_pages, args.zap_timeout, args.zap_active)

    finished_at = now_iso()
    elapsed = round(time.perf_counter() - started, 3)
    data = {
        "target_url": safe_url(target_url),
        "scope_origin": origin(target_url),
        "mode": args.mode,
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_s": elapsed,
        "http_baseline": baseline,
        "crawl_pages": [asdict(page) for page in crawl_pages],
        "forms": forms,
        "scripts": scripts,
        "api_hints": api_hints,
        "zap": zap,
    }
    (out_dir / "report.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(out_dir, data)
    print(json.dumps({"report": str(out_dir / "report.md"), "json": str(out_dir / "report.json"), "elapsed_s": elapsed}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
