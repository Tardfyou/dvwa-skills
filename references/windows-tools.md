# Windows Tooling

Use this file for install/setup notes. Use `references\usage.md` for the main skill usage guide, `references\tool-environment-management.md` for reproducible install/uninstall automation, and `references\tool-capabilities.md` for when to use each tool.

## Minimum For Brute Force

Required:

- Windows with local DVWA running
- Python 3
- `requests`, `beautifulsoup4`, and `playwright` packages from `scripts\requirements.txt`
- Playwright Chromium browser for automatic screenshots

Check:

```powershell
cd <path-to>\dvwa-skills
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 -m playwright install chromium
py -3.11 .\scripts\tool_check.py
```

Automatic screenshot helper:

```powershell
py -3.11 .\scripts\dvwa_screenshot.py `
  --url http://127.0.0.1/dvwa/ `
  --username admin `
  --password password `
  --difficulty low `
  --module-path vulnerabilities/brute/ `
  --output-dir ..\dvwa-results\screenshot-smoke\low
```

## Burp Suite

Install Burp Suite Community or Professional from PortSwigger's official download/install page.

Use with this skill:

1. Start Burp.
2. Keep the proxy listener on `127.0.0.1:8080`.
3. Configure the browser or generated Python harness to use `http://127.0.0.1:8080` as proxy.
4. Inspect Proxy HTTP history.
5. Send a request to Repeater for manual verification.
6. Use Intruder for low/medium Brute Force comparison; high/impossible need token refresh handling.

Optional Burp MCP path:

1. Install Java/JDK so `java --version` and `jar --version` work.
2. Clone `https://github.com/PortSwigger/mcp-server.git`.
3. Build the extension JAR with Gradle, for example `.\gradlew.bat embedProxyJar` on Windows.
4. Load `build\libs\burp-mcp-all.jar` in Burp under Extensions.
5. Enable/configure the MCP server in the Burp `MCP` tab. The documented default is a local server on `127.0.0.1:9876`.
6. Configure Codex to connect to the local MCP endpoint or stdio proxy.

If Burp MCP is not connected, this skill still works through browser/manual proxy traffic, generated Python harnesses, and exported raw request files.

## OWASP ZAP

Install OWASP ZAP from the official ZAP download page. Use the local proxy listener the same way as Burp:

```powershell
# Example for a generated harness or optional helper:
# --proxy http://127.0.0.1:8080
```

Use ZAP for:

- request capture
- passive scan review
- manual replay
- optional API-driven spider/passive scan when the API is enabled

ZAP's API can be explored through the local ZAP listener, commonly `http://localhost:8080/`, when proxying through ZAP.

Keep active scanning limited to the provided DVWA URL.

## ffuf

Install Go, then run:

```powershell
go install github.com/ffuf/ffuf/v2@latest
```

Use ffuf for later fuzzing tasks or low/medium Brute Force demonstrations from exported artifacts. Prefer generated Python/requests harnesses for Brute Force because high/impossible require coherent sessions and fresh CSRF tokens; `dvwa_runner.py` is only a reusable reference helper.

## sqlmap

Install Python and clone the official project:

```powershell
git clone https://github.com/sqlmapproject/sqlmap.git C:\Tools\sqlmap
py -3.11 C:\Tools\sqlmap\sqlmap.py -h
```

Use sqlmap for DVWA SQL Injection and SQL Injection Blind after exporting an authenticated request or providing correct cookies. Do not use sqlmap for Brute Force.

## Browser DevTools

Use F12/DevTools for:

- DOM XSS
- CSP bypass
- JavaScript Attacks
- visual confirmation of XSS execution
- console function calls in JavaScript-based modules

For Brute Force, DevTools is optional; Burp/ZAP history or generated harness reports give cleaner evidence.

## IDA Free / IDA Pro

IDA is not used by the public DVWA web walkthroughs and is not needed for Brute Force. It is useful for binary reverse engineering, not PHP source review.

Install IDA Free from Hex-Rays only if later exercises include compiled binaries. IDA Free has limitations, including no IDAPython SDK; use IDA Home/Pro where automation or MCP integration needs IDAPython.

Optional IDA MCP path:

1. Install an IDA edition that supports your automation needs.
2. Install the IDA MCP bridge required by your Codex environment.
3. Start IDA with the target binary loaded.
4. Connect Codex to the MCP endpoint.

Do not invoke IDA for DVWA Brute Force.


