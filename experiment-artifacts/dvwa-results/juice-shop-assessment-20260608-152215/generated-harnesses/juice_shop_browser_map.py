import argparse
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


ROUTES = [
    ("home", "/#/"),
    ("login", "/#/login"),
    ("search", "/#/search"),
    ("about", "/#/about"),
    ("contact", "/#/contact"),
    ("score-board", "/#/score-board"),
    ("privacy-security", "/#/privacy-security"),
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
    started = time.time()
    pages = []
    network = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 900})
        page = context.new_page()
        page.on("response", lambda r: network.append({"url": r.url, "status": r.status, "method": r.request.method, "type": r.request.resource_type}) if r.url.startswith(base) else None)
        for name, path in ROUTES:
            page.goto(base + path, wait_until="networkidle", timeout=30000)
            for selector in ["button:has-text('Dismiss')", "button:has-text('Me want it!')"]:
                try:
                    page.locator(selector).first.click(timeout=1000)
                except Exception:
                    pass
            page.wait_for_timeout(800)
            shot = shots / f"{name}.png"
            page.screenshot(path=str(shot), full_page=True)
            forms = page.evaluate("() => Array.from(document.querySelectorAll('form')).map(f => ({method: f.method, action: f.action, inputs: Array.from(f.querySelectorAll('input,textarea,select')).map(i => ({name: i.name, id: i.id, type: i.type, placeholder: i.placeholder}))}))")
            links = page.evaluate("() => Array.from(document.querySelectorAll('a[href]')).slice(0, 80).map(a => ({text: (a.innerText || '').trim().slice(0,100), href: a.href}))")
            buttons = page.evaluate("() => Array.from(document.querySelectorAll('button')).slice(0, 60).map(b => ({text: (b.innerText || b.getAttribute('aria-label') || '').trim().slice(0,100), type: b.type, aria: b.getAttribute('aria-label')}))")
            pages.append({"name": name, "url": page.url, "title": page.title(), "screenshot": str(shot.relative_to(out_dir)), "forms": forms, "links": links, "buttons": buttons})
        cookies = context.cookies()
        browser.close()

    result = {"target": args.url, "elapsed_s": round(time.time() - started, 3), "pages": pages, "same_origin_network": network, "cookies": cookies}
    (out_dir / "browser-map.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": True, "pages": len(pages)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
