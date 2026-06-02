param(
    [string]$ToolsRoot = "C:\Tools",
    [switch]$SkipGui,
    [switch]$SkipIda,
    [switch]$SkipBurpMcp
)

$ErrorActionPreference = "Stop"
$SkillRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$InstallRecord = Join-Path $SkillRoot "references\local-tool-install-status.generated.json"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Require-Winget {
    if (-not (Test-Command "winget")) {
        throw "winget is required. Install App Installer from Microsoft Store, then rerun this script."
    }
}

function Install-WingetPackage {
    param(
        [string]$Id,
        [string]$Name
    )
    $existing = winget list --id $Id --accept-source-agreements 2>$null
    if ($LASTEXITCODE -eq 0 -and ($existing -match [regex]::Escape($Id))) {
        Write-Host "$Name already installed ($Id)."
        return
    }
    Write-Step "Installing $Name ($Id)"
    winget install --id $Id --exact --accept-package-agreements --accept-source-agreements --silent
}

function Add-UserPath {
    param([string]$Entry)
    if ([string]::IsNullOrWhiteSpace($Entry)) { return }
    $current = [Environment]::GetEnvironmentVariable("Path", "User")
    $items = @()
    if (-not [string]::IsNullOrWhiteSpace($current)) {
        $items = $current -split ";" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    }
    if ($items -notcontains $Entry) {
        $items += $Entry
        [Environment]::SetEnvironmentVariable("Path", ($items -join ";"), "User")
        Write-Host "Added to user PATH: $Entry"
    }
    if (($env:Path -split ";") -notcontains $Entry) {
        $env:Path = "$env:Path;$Entry"
    }
}

function Get-GoBin {
    if (Test-Command "go") {
        $goPath = (& go env GOPATH) 2>$null
        $first = ($goPath -split ";")[0]
        if (-not [string]::IsNullOrWhiteSpace($first)) {
            return (Join-Path $first "bin")
        }
    }
    return (Join-Path $env:USERPROFILE "go\bin")
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Ensure-GitRepo {
    param(
        [string]$Url,
        [string]$Path
    )
    if (Test-Path -LiteralPath (Join-Path $Path ".git")) {
        git -C $Path pull --ff-only
    } elseif (Test-Path -LiteralPath $Path) {
        Write-Host "$Path exists but is not a git repository; leaving it untouched."
    } else {
        git clone $Url $Path
    }
}

function Build-BurpMcp {
    param([string]$RepoPath)
    $jarPath = Join-Path $RepoPath "build\libs\burp-mcp-all.jar"
    if (Test-Path -LiteralPath $jarPath) {
        Write-Host "Burp MCP JAR already exists: $jarPath"
        return
    }
    Push-Location $RepoPath
    try {
        & .\gradlew.bat embedProxyJar
        if ($LASTEXITCODE -eq 0) { return }

        Write-Host "Gradle wrapper download failed; downloading Gradle distribution with PowerShell."
        $gradleZip = Join-Path $ToolsRoot "gradle-9.2.0-bin.zip"
        if (-not (Test-Path -LiteralPath $gradleZip)) {
            Invoke-WebRequest -Uri "https://services.gradle.org/distributions/gradle-9.2.0-bin.zip" -OutFile $gradleZip -TimeoutSec 300
        }
        $wrapperProperties = Join-Path $RepoPath "gradle\wrapper\gradle-wrapper.properties"
        (Get-Content $wrapperProperties) `
            -replace "^networkTimeout=.*", "networkTimeout=120000" `
            -replace "^distributionUrl=.*", "distributionUrl=file:///C:/Tools/gradle-9.2.0-bin.zip" |
            Set-Content $wrapperProperties -Encoding ASCII
        & .\gradlew.bat embedProxyJar
        if ($LASTEXITCODE -ne 0) {
            throw "Burp MCP build failed. Rerun from $RepoPath when network access is stable."
        }
    } finally {
        Pop-Location
    }
}

Require-Winget
Ensure-Directory $ToolsRoot
Ensure-Directory (Join-Path $ToolsRoot "bin")

Write-Step "Installing base prerequisites"
if (-not (Test-Command "py") -and -not (Test-Command "python")) {
    Install-WingetPackage -Id "Python.Python.3.12" -Name "Python"
}
if (-not (Test-Command "git")) {
    Install-WingetPackage -Id "Git.Git" -Name "Git"
}
if (-not (Test-Command "go")) {
    Install-WingetPackage -Id "GoLang.Go" -Name "Go"
}
if (-not (Test-Command "jar")) {
    Install-WingetPackage -Id "EclipseAdoptium.Temurin.21.JDK" -Name "Temurin JDK"
}

Write-Step "Installing Python dependencies"
py -m pip install -r (Join-Path $SkillRoot "scripts\requirements.txt")
py -m playwright install chromium

Write-Step "Installing ffuf"
go install github.com/ffuf/ffuf/v2@latest
$goBin = Get-GoBin
Add-UserPath $goBin

Write-Step "Installing sqlmap"
$sqlmapPath = Join-Path $ToolsRoot "sqlmap"
Ensure-GitRepo -Url "https://github.com/sqlmapproject/sqlmap.git" -Path $sqlmapPath
$sqlmapWrapper = Join-Path $ToolsRoot "bin\sqlmap.cmd"
@"
@echo off
py $sqlmapPath\sqlmap.py %*
"@ | Set-Content -LiteralPath $sqlmapWrapper -Encoding ASCII
Add-UserPath (Join-Path $ToolsRoot "bin")

if (-not $SkipGui) {
    Write-Step "Installing GUI security tools"
    Install-WingetPackage -Id "PortSwigger.BurpSuite.Community" -Name "Burp Suite Community"
    Install-WingetPackage -Id "ZAP.ZAP" -Name "OWASP ZAP"
    if (-not $SkipIda) {
        Install-WingetPackage -Id "Hex-Rays.IDA.Free" -Name "IDA Free"
    }
}

if (-not $SkipBurpMcp) {
    Write-Step "Installing Burp MCP source and extension JAR"
    $burpMcpPath = Join-Path $ToolsRoot "burp-mcp-server"
    Ensure-GitRepo -Url "https://github.com/PortSwigger/mcp-server.git" -Path $burpMcpPath
    Build-BurpMcp -RepoPath $burpMcpPath
}

$record = [ordered]@{
    generated_at = (Get-Date).ToString("o")
    skill_root = $SkillRoot.Path
    tools_root = $ToolsRoot
    path_entries = @((Join-Path $ToolsRoot "bin"), $goBin)
    installed_paths = [ordered]@{
        ffuf = (Join-Path $goBin "ffuf.exe")
        sqlmap = (Join-Path $sqlmapPath "sqlmap.py")
        sqlmap_wrapper = $sqlmapWrapper
        burp = (Join-Path $env:LOCALAPPDATA "Programs\BurpSuiteCommunity\BurpSuiteCommunity.exe")
        zap = "C:\Program Files\ZAP\Zed Attack Proxy\ZAP.exe"
        ida_free = "C:\Program Files\IDA Freeware 8.4\ida64.exe"
        burp_mcp = (Join-Path $ToolsRoot "burp-mcp-server")
        burp_mcp_jar = (Join-Path $ToolsRoot "burp-mcp-server\build\libs\burp-mcp-all.jar")
    }
}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $InstallRecord -Encoding UTF8

Write-Step "Setup complete"
Write-Host "Install record: $InstallRecord"
Write-Host "Open a new PowerShell window so PATH changes are visible to other shells."
