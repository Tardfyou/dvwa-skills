[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$ToolsRoot = "C:\Tools",
    [switch]$RemovePrerequisites
)

$ErrorActionPreference = "Stop"
$SkillRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Remove-PathEntry {
    param([string]$Entry)
    if ([string]::IsNullOrWhiteSpace($Entry)) { return }
    $current = [Environment]::GetEnvironmentVariable("Path", "User")
    if ([string]::IsNullOrWhiteSpace($current)) { return }
    $items = $current -split ";" | Where-Object { $_ -and ($_ -ne $Entry) }
    if (($items -join ";") -ne $current) {
        if ($PSCmdlet.ShouldProcess("User PATH", "remove $Entry")) {
            [Environment]::SetEnvironmentVariable("Path", ($items -join ";"), "User")
        }
    }
}

function Uninstall-WingetPackage {
    param(
        [string]$Id,
        [string]$Name
    )
    $existing = winget list --id $Id --accept-source-agreements 2>$null
    if ($LASTEXITCODE -ne 0 -or -not ($existing -match [regex]::Escape($Id))) {
        Write-Host "$Name is not installed through winget ($Id)."
        return
    }
    if ($PSCmdlet.ShouldProcess($Name, "winget uninstall $Id")) {
        winget uninstall --id $Id --exact --accept-source-agreements --silent
    }
}

function Remove-FileOrDirectory {
    param([string]$Path)
    if (Test-Path -LiteralPath $Path) {
        if ($PSCmdlet.ShouldProcess($Path, "remove")) {
            Remove-Item -LiteralPath $Path -Recurse -Force
        }
    }
}

function Get-GoBinCandidates {
    $candidates = New-Object System.Collections.Generic.List[string]
    $candidates.Add((Join-Path $env:USERPROFILE "go\bin"))
    if (Get-Command go -ErrorAction SilentlyContinue) {
        $goPath = (& go env GOPATH) 2>$null
        foreach ($entry in ($goPath -split ";")) {
            if (-not [string]::IsNullOrWhiteSpace($entry)) {
                $candidates.Add((Join-Path $entry "bin"))
            }
        }
    }
    return $candidates | Select-Object -Unique
}

Write-Host "Removing optional DVWA security tooling."

Uninstall-WingetPackage -Id "PortSwigger.BurpSuite.Community" -Name "Burp Suite Community"
Uninstall-WingetPackage -Id "ZAP.ZAP" -Name "OWASP ZAP"
Uninstall-WingetPackage -Id "Hex-Rays.IDA.Free" -Name "IDA Free"

Remove-FileOrDirectory (Join-Path $ToolsRoot "sqlmap")
Remove-FileOrDirectory (Join-Path $ToolsRoot "burp-mcp-server")
Remove-FileOrDirectory (Join-Path $ToolsRoot "gradle-9.2.0-bin.zip")
Remove-FileOrDirectory (Join-Path $ToolsRoot "bin\sqlmap.cmd")

foreach ($goBin in Get-GoBinCandidates) {
    Remove-FileOrDirectory (Join-Path $goBin "ffuf.exe")
    Remove-PathEntry $goBin
}
Remove-PathEntry (Join-Path $ToolsRoot "bin")

if ($RemovePrerequisites) {
    Uninstall-WingetPackage -Id "GoLang.Go" -Name "Go"
    Uninstall-WingetPackage -Id "EclipseAdoptium.Temurin.21.JDK" -Name "Temurin JDK"
    Uninstall-WingetPackage -Id "Git.Git" -Name "Git"
    Uninstall-WingetPackage -Id "Python.Python.3.12" -Name "Python"
}

$generatedRecord = Join-Path $SkillRoot "references\local-tool-install-status.generated.json"
Remove-FileOrDirectory $generatedRecord

Write-Host "Uninstall routine complete. Open a new PowerShell window to refresh PATH."
