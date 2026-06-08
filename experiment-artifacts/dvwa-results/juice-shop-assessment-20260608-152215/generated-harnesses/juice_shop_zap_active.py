import argparse
import json
import time
from pathlib import Path
from urllib.parse import urlencode

import requests


def zap_get(zap_url: str, path: str, params: dict | None = None, timeout: int = 30):
    url = zap_url.rstrip("/") + path
    if params:
        url += "?" + urlencode(params)
    resp = requests.get(url, timeout=timeout)
    body = None
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
    parser.add_argument("--max-minutes", default="10")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    started = time.time()
    events = []

    try:
        version = zap_get(args.zap_url, "/JSON/core/view/version/")
        events.append({"step": "version", **version})
        if version["status_code"] != 200:
            raise RuntimeError(f"ZAP version endpoint returned {version['status_code']}")

        scan = zap_get(
            args.zap_url,
            "/JSON/ascan/action/scan/",
            {
                "url": args.target,
                "recurse": "true",
                "inScopeOnly": "false",
                "scanPolicyName": "",
                "method": "",
                "postData": "",
                "maxRuleDurationInMins": "2",
                "maxScanDurationInMins": args.max_minutes,
            },
        )
        events.append({"step": "active-scan-start", **scan})
        scan_id = (scan.get("body") or {}).get("scan") if isinstance(scan.get("body"), dict) else None

        if scan_id is not None:
            deadline = time.time() + (int(args.max_minutes) * 60 + 45)
            while time.time() < deadline:
                status = zap_get(args.zap_url, "/JSON/ascan/view/status/", {"scanId": scan_id})
                events.append({"step": "active-scan-status", **status})
                value = (status.get("body") or {}).get("status") if isinstance(status.get("body"), dict) else None
                if value == "100":
                    break
                time.sleep(5)

        records = zap_get(args.zap_url, "/JSON/pscan/view/recordsToScan/")
        events.append({"step": "passive-records-to-scan", **records})
        for _ in range(20):
            records = zap_get(args.zap_url, "/JSON/pscan/view/recordsToScan/")
            events.append({"step": "passive-records-to-scan", **records})
            value = (records.get("body") or {}).get("recordsToScan") if isinstance(records.get("body"), dict) else None
            if value in ("0", 0):
                break
            time.sleep(2)

        alerts = zap_get(args.zap_url, "/JSON/core/view/alerts/", {"baseurl": args.target, "start": "0", "count": "500"})
        urls = zap_get(args.zap_url, "/JSON/core/view/urls/", {"baseurl": args.target})
        events.append({"step": "alerts", **alerts})
        events.append({"step": "urls", **urls})

        result = {
            "available": True,
            "target": args.target,
            "zap_url": args.zap_url,
            "scan_id": scan_id,
            "elapsed_s": round(time.time() - started, 3),
            "events": events,
        }
    except Exception as exc:
        result = {
            "available": False,
            "target": args.target,
            "zap_url": args.zap_url,
            "elapsed_s": round(time.time() - started, 3),
            "error": str(exc),
            "events": events,
        }

    output = out_dir / "zap-active.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": result.get("available", False), "out": str(output), "elapsed_s": result["elapsed_s"], "error": result.get("error")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
