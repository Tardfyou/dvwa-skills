param(
    [string]$DvwaUrl = "http://127.0.0.1/dvwa/",
    [int]$WebPort = 80,
    [int]$MysqlPort = 3306,
    [int]$BurpPort = 8080,
    [int]$ZapPort = 8090,
    [int]$BurpMcpPort = 9876,
    [string]$PhpStudyPath = "D:\phpStudy\phpStudy.exe",
    [string]$BurpPath = "$env:LOCALAPPDATA\Programs\BurpSuiteCommunity\BurpSuiteCommunity.exe",
    [string]$ZapDir = "C:\Program Files\ZAP\Zed Attack Proxy",
    [switch]$NoStart,
    [switch]$SkipZap,
    [switch]$SkipBurp,
    [switch]$SkipPhpStudy
)

$ErrorActionPreference = "Stop"
$SkillRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message"
}

function Get-ListeningPort {
    param([int]$Port)
    $connections = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    $items = @()
    foreach ($connection in $connections) {
        $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
        $items += [pscustomobject]@{
            Port = $connection.LocalPort
            Address = $connection.LocalAddress
            PID = $connection.OwningProcess
            Process = if ($process) { $process.ProcessName } else { "" }
        }
    }
    return $items
}

function Test-Port {
    param([int]$Port)
    return [bool](Get-ListeningPort -Port $Port)
}

function Start-GuiTool {
    param(
        [string]$Name,
        [string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host "$Name not found: $Path"
        return
    }
    Write-Host "Starting ${Name}: $Path"
    Start-Process -FilePath $Path | Out-Null
}

function Start-ZapDaemon {
    param(
        [string]$Directory,
        [int]$Port
    )
    $bat = Join-Path $Directory "zap.bat"
    if (-not (Test-Path -LiteralPath $bat)) {
        Write-Host "ZAP launcher not found: $bat"
        return
    }
    Write-Host "Starting ZAP daemon on 127.0.0.1:$Port"
    $args = "/c `"zap.bat -daemon -host 127.0.0.1 -port $Port -config api.disablekey=true`""
    Start-Process -FilePath "cmd.exe" -ArgumentList $args -WorkingDirectory $Directory -WindowStyle Hidden | Out-Null
}

function Wait-Port {
    param(
        [int]$Port,
        [int]$TimeoutSeconds = 45
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port -Port $Port) { return $true }
        Start-Sleep -Seconds 2
    }
    return $false
}

function Invoke-CurlStatus {
    param([string]$Url)
    try {
        $output = & curl.exe -sS -L -o NUL -w "final_url=%{url_effective}`nstatus=%{http_code}`n" $Url 2>&1
        return ($output -join "`n")
    } catch {
        return "curl failed: $($_.Exception.Message)"
    }
}

Write-Step "Python and optional tool check"
$env:PYTHONIOENCODING = "utf-8"
& py -3.11 (Join-Path $SkillRoot "scripts\tool_check.py")

Write-Step "Start missing GUI/proxy tools"
if (-not $NoStart) {
    if (-not $SkipPhpStudy -and -not (Get-Process -Name "phpStudy" -ErrorAction SilentlyContinue)) {
        Start-GuiTool -Name "phpStudy" -Path $PhpStudyPath
        Start-Sleep -Seconds 5
    }

    if (-not $SkipBurp -and -not (Test-Port -Port $BurpPort) -and -not (Get-Process -Name "BurpSuiteCommunity" -ErrorAction SilentlyContinue)) {
        Start-GuiTool -Name "Burp Suite Community" -Path $BurpPath
        Start-Sleep -Seconds 12
    }

    if (-not $SkipZap -and -not (Test-Port -Port $ZapPort)) {
        Start-ZapDaemon -Directory $ZapDir -Port $ZapPort
        [void](Wait-Port -Port $ZapPort -TimeoutSeconds 75)
    }
}

Write-Step "Listening ports"
$ports = @($WebPort, $MysqlPort, $BurpPort, $ZapPort, $BurpMcpPort)
$rows = @()
foreach ($port in $ports) {
    $listeners = Get-ListeningPort -Port $port
    if ($listeners) {
        $rows += $listeners
    } else {
        $rows += [pscustomobject]@{
            Port = $port
            Address = ""
            PID = ""
            Process = "NOT_LISTENING"
        }
    }
}
$rows | Sort-Object Port, Address | Format-Table -AutoSize

Write-Step "DVWA HTTP check"
Write-Host (Invoke-CurlStatus -Url $DvwaUrl)

Write-Step "ZAP API check"
if (Test-Port -Port $ZapPort) {
    try {
        & curl.exe -sS "http://127.0.0.1:$ZapPort/JSON/core/view/version/"
        Write-Host ""
    } catch {
        Write-Host "ZAP API check failed: $($_.Exception.Message)"
    }
} else {
    Write-Host "ZAP is not listening on 127.0.0.1:$ZapPort"
}

Write-Step "Process summary"
Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -in @("phpStudy", "httpd", "mysqld", "BurpSuiteCommunity", "java") } |
    Select-Object ProcessName, Id, Path |
    Sort-Object ProcessName, Id |
    Format-Table -AutoSize

Write-Step "Notes"
Write-Host "Burp proxy:      127.0.0.1:$BurpPort"
Write-Host "ZAP daemon:      127.0.0.1:$ZapPort"
Write-Host "Burp MCP:        127.0.0.1:$BurpMcpPort (must be enabled inside Burp)"
Write-Host "phpStudy services are verified by ports $WebPort and $MysqlPort. If phpStudy opens but those ports stay closed, start Apache/MySQL in the phpStudy UI."
Write-Host "Use -NoStart for check-only mode."
