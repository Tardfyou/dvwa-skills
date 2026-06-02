#!/usr/bin/env python3
"""Check local optional tooling for the DVWA skill."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def candidate_paths() -> list[Path]:
    paths = [
        Path(r"C:\Tools\bin"),
        Path.home() / "go" / "bin",
        Path.home() / "AppData" / "Local" / "Programs" / "BurpSuiteCommunity",
        Path(r"C:\Program Files\ZAP\Zed Attack Proxy"),
        Path(r"C:\Program Files\IDA Freeware 8.4"),
    ]
    for root in (Path(r"D:\WorkSpace\GOLEARN"), Path(r"D:\WorkSpace\GOSELF")):
        paths.append(root / "bin")
    for entry in (sub for sub in __import__("os").environ.get("GOPATH", "").split(";") if sub):
        paths.append(Path(entry) / "bin")
    return paths


def command_version(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=8,
            check=False,
        )
    except Exception as exc:
        return f"unavailable ({exc})"
    first_line = (completed.stdout or "").strip().splitlines()
    return first_line[0] if first_line else f"exit={completed.returncode}"


def find_executable(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    suffixes = ["", ".exe", ".cmd", ".bat"]
    for directory in candidate_paths():
        for suffix in suffixes:
            candidate = directory / f"{name}{suffix}"
            if candidate.exists():
                return str(candidate)
    return None


def find_local_walkthrough() -> Path | None:
    search_roots = [
        ROOT.parent,
        Path.cwd(),
        Path(r"D:\WorkSpace\综合实践5"),
    ]
    seen: set[Path] = set()
    for root in search_roots:
        try:
            resolved = root.resolve()
        except Exception:
            continue
        if resolved in seen or not resolved.exists():
            continue
        seen.add(resolved)
        match = next(resolved.rglob("DVWA-WalkThrough.md"), None)
        if match:
            return match
    return None


def main() -> int:
    checks = []
    checks.append(("Python", sys.executable, sys.version.split()[0]))
    python_note = (
        "preferred"
        if sys.version_info[:2] == (3, 11)
        else "warning: use py -3.11 for DVWA skill helpers"
    )
    checks.append(("Python runtime", "py -3.11", python_note))
    checks.append(("requests", "python package", "installed" if importlib.util.find_spec("requests") else "missing"))
    checks.append(("beautifulsoup4", "python package", "installed" if importlib.util.find_spec("bs4") else "missing"))
    checks.append(("playwright", "python package", "installed" if importlib.util.find_spec("playwright") else "missing"))

    for name, exe, version_args in [
        ("Java", "java", ["java", "--version"]),
        ("ffuf", "ffuf", ["ffuf", "-V"]),
        ("sqlmap", "sqlmap", ["sqlmap", "--version"]),
        ("git", "git", ["git", "--version"]),
    ]:
        path = find_executable(exe)
        command = [path, *version_args[1:]] if path else version_args
        if exe == "sqlmap" and path:
            checks.append((name, path, "installed"))
        else:
            checks.append((name, path or "not on PATH", command_version(command) if path else "missing"))

    gui_tools = [
        (
            "Burp Suite Community",
            str(Path.home() / "AppData" / "Local" / "Programs" / "BurpSuiteCommunity" / "BurpSuiteCommunity.exe"),
        ),
        ("OWASP ZAP", r"C:\Program Files\ZAP\Zed Attack Proxy\ZAP.exe"),
        ("IDA Free", r"C:\Program Files\IDA Freeware 8.4\ida64.exe"),
        ("Burp MCP JAR", r"C:\Tools\burp-mcp-server\build\libs\burp-mcp-all.jar"),
    ]
    for name, path_text in gui_tools:
        path = Path(path_text)
        checks.append((name, str(path), "installed" if path.exists() else "missing"))

    chromium_cache = Path.home() / "AppData" / "Local" / "ms-playwright"
    chromium_installed = bool(list(chromium_cache.glob("chromium-*"))) if chromium_cache.exists() else False
    checks.append(("Playwright Chromium", str(chromium_cache), "installed" if chromium_installed else "missing"))

    local_walkthrough = find_local_walkthrough()
    checks.append(("1earn DVWA-WalkThrough", str(local_walkthrough) if local_walkthrough else "not found", "local source"))

    print("DVWA skill tool check")
    print("=====================")
    for name, location, status in checks:
        print(f"{name}: {status} [{location}]")

    print()
    print("Brute Force minimum: Python + requests + reachable DVWA URL.")
    print("Automatic screenshots: playwright package + Playwright Chromium.")
    print("Preferred Windows interpreter: py -3.11. Avoid generic py -3 for generated harnesses.")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'not set')}")
    print("Burp/ZAP/ffuf/sqlmap/IDA are optional; sqlmap and IDA are not used for Brute Force.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
