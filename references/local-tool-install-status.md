# Local Tool Install Status

Generated after setup on this Windows machine.

## Installed

- Python: `C:\Users\31435\AppData\Local\Programs\Python\Python311\python.exe`
- Java: `C:\Program Files\Common Files\Oracle\Java\javapath\java.exe`
- Git: `D:\Program Files\Git\cmd\git.exe`
- ffuf: `D:\WorkSpace\GOLEARN\bin\ffuf.exe`
- sqlmap: `C:\Tools\sqlmap\sqlmap.py`
- sqlmap wrapper: `C:\Tools\bin\sqlmap.cmd`
- Playwright Python package: installed in Python 3.11 environment
- Playwright Chromium: `C:\Users\31435\AppData\Local\ms-playwright\chromium-1223`
- Burp Suite Community: `C:\Users\31435\AppData\Local\Programs\BurpSuiteCommunity\BurpSuiteCommunity.exe`
- OWASP ZAP: `C:\Program Files\ZAP\Zed Attack Proxy\ZAP.exe`
- IDA Free: `C:\Program Files\IDA Freeware 8.4\ida64.exe`
- Burp MCP source: `C:\Tools\burp-mcp-server`
- Burp MCP extension JAR: `C:\Tools\burp-mcp-server\build\libs\burp-mcp-all.jar`

## PATH Notes

The user PATH was updated to include:

- `C:\Tools\bin`
- `D:\WorkSpace\GOLEARN\bin`

Open a new PowerShell window before expecting `ffuf` and `sqlmap` to resolve through `where.exe`.

## Manual Steps Still Required

Burp MCP cannot be fully enabled from the command line because Burp extensions are loaded through the Burp UI:

1. Start Burp Suite Community.
2. Go to `Extensions`.
3. Add a Java extension.
4. Select `C:\Tools\burp-mcp-server\build\libs\burp-mcp-all.jar`.
5. Open the `MCP` tab.
6. Enable the MCP server, normally on `http://127.0.0.1:9876`.
7. Configure Codex MCP connection if the runtime supports user-defined MCP servers.

For DVWA Brute Force testing, Burp MCP is optional. Codex can still solve the lab with live page/source inspection, browser or proxy observations, and a generated Python harness.

## Automatic Screenshot Support

Playwright screenshot support is enabled. Smoke-test output was generated under:

```text
D:\WorkSpace\综合实践5\dvwa-results\screenshot-smoke\brute-low
```

Useful command:

```powershell
cd D:\WorkSpace\综合实践5\dvwa-skills
py -3.11 .\scripts\dvwa_screenshot.py --url http://127.0.0.1/dvwa/ --username admin --password password --difficulty low --module-path vulnerabilities/brute/ --output-dir ..\dvwa-results\screenshot-smoke\brute-low
```

CSRF proof screenshots used a generated Node Playwright script. The first temporary `npx.cmd -y -p playwright@1.60.0 node ...` attempt failed because the external generated script did not reliably resolve `require('playwright')` from the temporary npx package. The successful repair was:

```powershell
cd D:\WorkSpace\综合实践5\dvwa-results\csrf-progression-20260602-103818
npm.cmd install playwright@1.60.0 --no-audit --no-fund
node .\generated-harnesses\csrf_playwright_screenshots.js .\screenshots
```

For future runs, prefer Python Playwright. If a Node proof script is generated, install Node Playwright in the run directory before executing it.
