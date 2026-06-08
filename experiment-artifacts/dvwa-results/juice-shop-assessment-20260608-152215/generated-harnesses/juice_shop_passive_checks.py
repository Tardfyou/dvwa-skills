import argparse
import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests


PATHS = ["/", "/robots.txt", "/ftp", "/.well-known", "/api-docs/", "/rest/products/search?q=apple", "/rest/admin/application-version", "/rest/admin/application-configuration", "/rest/user/whoami", "/api/Products", "/rest/languages"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    base = args.url.rstrip("/") + "/"
    out_dir = Path(args.out_dir)
    req_dir = out_dir / "requests"
    req_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    results = []
    for path in PATHS:
        url = urljoin(base, path.lstrip("/"))
        resp = requests.get(url, timeout=15, allow_redirects=False)
        name = path.strip("/").replace("/", "-").replace("?", "_").replace("=", "-") or "home"
        item = {
            "name": name,
            "url": url,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("content-type", ""),
            "response_len": len(resp.content),
            "headers_subset": {k: resp.headers.get(k) for k in ["Access-Control-Allow-Origin", "Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Feature-Policy"] if k in resp.headers},
            "snippet": " ".join(resp.text.replace("\r", " ").replace("\n", " ").split())[:900] if "text" in resp.headers.get("content-type", "") or "json" in resp.headers.get("content-type", "") or "html" in resp.headers.get("content-type", "") else "",
        }
        results.append(item)
        (req_dir / f"passive-{name}.json").write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding="utf-8")
    result = {"target": args.url, "elapsed_s": round(time.time() - started, 3), "results": results}
    (out_dir / "passive-checks.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": True, "count": len(results)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
