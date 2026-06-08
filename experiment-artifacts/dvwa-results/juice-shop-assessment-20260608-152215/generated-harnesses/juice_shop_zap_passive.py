import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlencode

import requests


def zap_get(zap_url: str, path: str, params: dict | None = None):
    url = zap_url.rstrip("/") + path
    if params:
        url += "?" + urlencode(params)
    resp = requests.get(url, timeout=30)
    try:
        body = resp.json()
    except Exception:
        body = resp.text[:1000]
    return {"url": url, "status_code": resp.status_code, "body": body}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--zap-url", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    started = time.time()
    events = []
    try:
        events.append({"step": "version", **zap_get(args.zap_url, "/JSON/core/view/version/")})
        spider = zap_get(args.zap_url, "/JSON/spider/action/scan/", {"url": args.target, "maxChildren": "25", "recurse": "true", "subtreeOnly": "true"})
        events.append({"step": "spider-start", **spider})
        scan_id = spider.get("body", {}).get("scan") if isinstance(spider.get("body"), dict) else None
        if scan_id is not None:
            deadline = time.time() + 60
            while time.time() < deadline:
                status = zap_get(args.zap_url, "/JSON/spider/view/status/", {"scanId": scan_id})
                events.append({"step": "spider-status", **status})
                if isinstance(status.get("body"), dict) and status["body"].get("status") == "100":
                    break
                time.sleep(2)
        events.append({"step": "alerts", **zap_get(args.zap_url, "/JSON/core/view/alerts/", {"baseurl": args.target, "start": "0", "count": "200"})})
        events.append({"step": "urls", **zap_get(args.zap_url, "/JSON/core/view/urls/", {"baseurl": args.target})})
        result = {"available": True, "target": args.target, "elapsed_s": round(time.time() - started, 3), "events": events}
    except Exception as exc:
        result = {"available": False, "target": args.target, "elapsed_s": round(time.time() - started, 3), "error": str(exc), "events": events}
    (out_dir / "zap-passive.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": result["available"], "elapsed_s": result["elapsed_s"], "error": result.get("error")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
