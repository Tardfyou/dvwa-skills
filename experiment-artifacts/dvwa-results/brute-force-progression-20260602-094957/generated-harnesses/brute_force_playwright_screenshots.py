#!/usr/bin/env python3
"""Capture DVWA Brute Force progression screenshots for the existing report."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from playwright.sync_api import Page, sync_playwright


TZ = timezone(timedelta(hours=8))
DIFFICULTIES = ["low", "medium", "high", "impossible"]


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def normalize_base(url: str) -> str:
    return url if url.endswith("/") else f"{url}/"


def safe_url(url: str) -> str:
    parts = urlsplit(url)
    pairs = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() in {"password", "user_token"}:
            value = "<redacted>"
        pairs.append((key, value))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(pairs), parts.fragment))


def capture(page: Page, path: Path, label: str, items: list[dict], difficulty: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), full_page=True)
    items.append(
        {
            "label": label,
            "difficulty": difficulty,
            "path": str(path),
            "url": safe_url(page.url),
            "timestamp": now_iso(),
        }
    )


def login(page: Page, base: str, username: str, password: str) -> None:
    page.goto(base + "login.php", wait_until="networkidle")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('input[name="Login"]')
    page.wait_for_load_state("networkidle")


def set_security(page: Page, base: str, difficulty: str) -> None:
    page.goto(base + "security.php", wait_until="networkidle")
    page.select_option('select[name="security"]', difficulty)
    page.click('input[name="seclev_submit"]')
    page.wait_for_load_state("networkidle")


def submit_brute(page: Page, base: str, username: str, password: str) -> None:
    page.goto(base + "vulnerabilities/brute/", wait_until="networkidle")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('input[name="Login"]')
    page.wait_for_load_state("networkidle")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture DVWA Brute Force proof screenshots.")
    parser.add_argument("--url", default="http://127.0.0.1/dvwa/")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="password")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    base = normalize_base(args.url)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    items: list[dict] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        page = browser.new_page(viewport={"width": 1366, "height": 900})

        login(page, base, args.username, args.password)
        capture(page, out_dir / "setup" / "authenticated-home.png", "authenticated home", items)

        for difficulty in DIFFICULTIES:
            set_security(page, base, difficulty)
            capture(page, out_dir / difficulty / f"security-{difficulty}.png", f"security {difficulty}", items, difficulty)
            page.goto(base + "vulnerabilities/brute/", wait_until="networkidle")
            capture(page, out_dir / difficulty / f"module-{difficulty}.png", f"module {difficulty}", items, difficulty)

        for difficulty in ["low", "medium", "high"]:
            set_security(page, base, difficulty)
            submit_brute(page, base, args.username, args.password)
            capture(
                page,
                out_dir / "proof" / f"{difficulty}-success-admin-password.png",
                f"{difficulty} admin password success",
                items,
                difficulty,
            )

        set_security(page, base, "impossible")
        submit_brute(page, base, "codex_probe_user", "definitely_wrong_20260602")
        capture(
            page,
            out_dir / "proof" / "impossible-defense-invalid-probe.png",
            "impossible invalid probe defense",
            items,
            "impossible",
        )

        set_security(page, base, "impossible")
        submit_brute(page, base, args.username, args.password)
        capture(
            page,
            out_dir / "proof" / "impossible-valid-credential-only.png",
            "impossible valid credential only",
            items,
            "impossible",
        )

        browser.close()

    manifest = {
        "generated_at": now_iso(),
        "base_url": base,
        "module_path": "vulnerabilities/brute/",
        "items": items,
    }
    (out_dir / "screenshots.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
