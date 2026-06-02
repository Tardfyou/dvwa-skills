# Tool Environment Management

Use this file when a new Windows machine needs the same optional security-tool environment, or when the installed tools should be removed cleanly.

## Install Everything

Run from the skill root:

```powershell
cd <path-to>\dvwa-skills
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_setup.ps1
py -3.11 .\scripts\tool_check.py
```

Use `py -3.11` for all Python commands in this skill. Avoid generic `py -3`; on this machine it may resolve to a Python preview build instead of the stable 3.11 environment used by `requests` and Playwright.

The setup script installs or prepares:

- Python dependencies from `scripts\requirements.txt`
- Playwright Chromium for automatic browser screenshots
- Git, Go, and a JDK when missing
- Burp Suite Community
- OWASP ZAP
- IDA Free
- ffuf through `go install`
- sqlmap under `C:\Tools\sqlmap`
- `sqlmap.cmd` wrapper under `C:\Tools\bin`
- Burp MCP server source under `C:\Tools\burp-mcp-server`
- Burp MCP extension JAR when Gradle can build it
- user PATH entries for `C:\Tools\bin` and the Go bin directory

The script writes an install record to:

```text
references\local-tool-install-status.generated.json
```

## Post-Install Startup Checks

After installation, open a new PowerShell window and run:

```powershell
cd <path-to>\dvwa-skills
py -3.11 .\scripts\tool_check.py
```

If screenshot support is missing, run:

```powershell
py -3.11 -m pip install -r .\scripts\requirements.txt
py -3.11 -m playwright install chromium
```

Check local lab ports:

```powershell
Test-NetConnection 127.0.0.1 -Port 80
Test-NetConnection 127.0.0.1 -Port 3306
Test-NetConnection 127.0.0.1 -Port 8080
Test-NetConnection 127.0.0.1 -Port 9876
```

Check the owning processes:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 80,3306,8080,9876 |
  Select-Object LocalAddress,LocalPort,OwningProcess,
    @{Name='ProcessName';Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}} |
  Sort-Object LocalPort
```

Check DVWA HTTP behavior:

```powershell
curl.exe -sS -L -o NUL -w "final_url=%{url_effective}`nstatus=%{http_code}`n" http://127.0.0.1/DVWA/
```

Check Burp MCP when enabled in Burp:

```powershell
curl.exe -sS -o NUL -w "status=%{http_code}`n" http://127.0.0.1:9876
java -jar C:\Tools\burp-mcp-server\libs\mcp-proxy-all.jar --sse-url http://127.0.0.1:9876
```

Expected notes:

- DVWA should resolve to `login.php` with HTTP status `200`.
- Burp MCP may return HTTP `403` to curl/browser but should accept the stdio proxy connection.
- If MySQL is configured on a non-default port in phpStudy, check that port instead of `3306`.

## Install Minimal Brute Force Environment

For DVWA Brute Force, GUI tools are optional. Use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_setup.ps1 -SkipGui -SkipIda -SkipBurpMcp
```

This leaves the Python dependencies plus command-line support tools needed for generated harnesses and optional helper smoke tests.

## Manual Step For Burp MCP

The script can clone/build the Burp MCP extension JAR, but Burp requires UI loading:

1. Start Burp Suite Community.
2. Open `Extensions`.
3. Add a Java extension.
4. Select `C:\Tools\burp-mcp-server\build\libs\burp-mcp-all.jar`.
5. Open the `MCP` tab and enable the server.
6. Use `http://127.0.0.1:9876` or `/sse` when configuring an MCP client, depending on the client.

## Clean Uninstall

Preview first:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1 -WhatIf
```

Remove tools installed by the setup script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1
```

The uninstall script:

- uninstalls Burp Suite Community, ZAP, and IDA Free through `winget`
- removes `C:\Tools\sqlmap`
- removes `C:\Tools\burp-mcp-server`
- removes `C:\Tools\gradle-9.2.0-bin.zip`
- removes `C:\Tools\bin\sqlmap.cmd`
- removes `ffuf.exe` from detected Go bin directories
- removes the PATH entries it added when they are present

By default it does not uninstall Git, Go, Python, or JDK because those are shared developer tools. To remove those prerequisites too:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\windows_tool_uninstall.ps1 -RemovePrerequisites
```

## Manifest

Use `references\tool-install-manifest.json` as the machine-readable source of package IDs, source repositories, install paths, and cleanup targets.
