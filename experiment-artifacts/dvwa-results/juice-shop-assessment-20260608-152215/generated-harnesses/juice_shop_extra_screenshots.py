import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


PAGES = [
    ("ftp-listing", "/ftp"),
    ("well-known-listing", "/.well-known"),
    ("api-docs", "/api-docs/"),
    ("metrics", "/metrics"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    base = args.url.rstrip("/")
    out_dir = Path(args.out_dir)
    shots = out_dir / "screenshots"
    shots.mkdir(parents=True, exist_ok=True)
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        for name, path in PAGES:
            url = base + path
            page.goto(url, wait_until="networkidle", timeout=30000)
            shot = shots / f"{name}.png"
            page.screenshot(path=str(shot), full_page=True)
            items.append({"name": name, "url": url, "screenshot": str(shot.relative_to(out_dir)), "title": page.title()})
        browser.close()

    (out_dir / "extra-screenshots.json").write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": True, "count": len(items)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
