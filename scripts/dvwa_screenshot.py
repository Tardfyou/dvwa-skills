#!/usr/bin/env python3
"""Capture authenticated DVWA screenshots with Playwright."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


TZ = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def normalize_base(url: str) -> str:
    return url if url.endswith("/") else f"{url}/"


def capture(page, path: Path, label: str, items: list[dict]) -> None:
    page.screenshot(path=str(path), full_page=True)
    items.append(
        {
            "label": label,
            "path": str(path),
            "url": page.url,
            "timestamp": now_iso(),
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture DVWA page screenshots after login.")
    parser.add_argument("--url", required=True, help="DVWA base URL, for example http://127.0.0.1/dvwa/")
    parser.add_argument("--username", default="admin", help="DVWA login username")
    parser.add_argument("--password", default="password", help="DVWA login password")
    parser.add_argument("--difficulty", required=True, choices=["low", "medium", "high", "impossible"])
    parser.add_argument("--module-path", required=True, help="DVWA module path, for example vulnerabilities/brute/")
    parser.add_argument("--output-dir", required=True, help="Directory where screenshots and manifest are written")
    parser.add_argument("--headed", action="store_true", help="Run browser visibly instead of headless")
    args = parser.parse_args()

    base_url = normalize_base(args.url)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    items: list[dict] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        page = browser.new_page(viewport={"width": 1366, "height": 900})

        page.goto(urljoin(base_url, "login.php"), wait_until="networkidle")
        page.fill('input[name="username"]', args.username)
        page.fill('input[name="password"]', args.password)
        page.click('input[name="Login"]')
        page.wait_for_load_state("networkidle")
        capture(page, output_dir / "authenticated-home.png", "authenticated home", items)

        page.goto(urljoin(base_url, "security.php"), wait_until="networkidle")
        page.select_option('select[name="security"]', args.difficulty)
        page.click('input[name="seclev_submit"]')
        page.wait_for_load_state("networkidle")
        capture(page, output_dir / f"security-{args.difficulty}.png", f"security {args.difficulty}", items)

        module_url = urljoin(base_url, args.module_path.lstrip("/"))
        page.goto(module_url, wait_until="networkidle")
        capture(page, output_dir / f"module-{args.difficulty}.png", f"module {args.difficulty}", items)

        browser.close()

    manifest = {
        "generated_at": now_iso(),
        "base_url": base_url,
        "difficulty": args.difficulty,
        "module_path": args.module_path,
        "items": items,
    }
    (output_dir / "screenshots.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
