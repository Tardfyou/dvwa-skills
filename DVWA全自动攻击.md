# DVWA 自动化靶场解题实验报告

## 0. 文档说明

本文档，用于记录本机 DVWA 授权靶场实验的完整生命周期：环境准备、启动检查、AI Skill 自动化解题和报告输出、漏洞复现、结果分析和最终总结。

后续每一类漏洞会先由 `$dvwa-automated-testing` skill 引导 Codex 在本机 DVWA 环境中完成分析和测试，并产出单题 Markdown 图文报告。随后再根据这些单题报告，把关键过程、截图、命令、证据和结论补充到本文档对应的实验分区。

本文档默认只针对本机授权环境：

```text
DVWA URL: http://127.0.0.1/DVWA/ 或 http://127.0.0.1/dvwa/
DVWA 源码路径: D:\phpStudy\PHPTutorial\WWW\DVWA
Skill 项目路径: D:\WorkSpace\综合实践5\dvwa-skills
Codex Skill 安装路径: C:\Users\31435\.codex\skills\dvwa-automated-testing
实验输出目录: D:\WorkSpace\综合实践5\dvwa-results
```

## 1. 实验边界与目标

### 1.1 授权边界

本实验仅在本机 DVWA 靶场中进行，实验对象为已经公开、认可且用于安全教学的 Damn Vulnerable Web Application。实验过程中不会访问、扫描、爆破或尝试利用任何外部互联网目标、真实业务系统或非授权服务。

允许范围：

- 本机 DVWA Web 服务。
- 本机 DVWA 源码目录。
- 本机 Burp Suite、OWASP ZAP、Python、ffuf、sqlmap 等工具在授权 DVWA 范围内的使用。
- Codex 通过 `$dvwa-automated-testing` skill 进行页面观察、源码分析、请求构造、测试用例生成和报告整理。

禁止范围：

- 对外部 IP、域名、真实业务系统进行扫描、爆破、利用或数据抓取。
- 将 DVWA payload、字典、脚本或代理流量指向非授权目标。
- 在靶场之外执行破坏性命令、持久化命令或外连回调。
- 在报告中泄露无关敏感信息、真实 Cookie、真实账号凭据或非实验数据。

### 1.2 实验目标

本实验的核心目标不是记忆 DVWA 题解，而是验证 AI Skill 能否引导模型按照 Web 靶场/CTF 的思路完成解题：

1. 明确授权范围和目标模块。
2. 登录 DVWA 并设置对应安全等级。
3. 观察页面、表单、参数、Cookie、Token 和响应特征。
4. 结合源码分析漏洞成因和防护逻辑。
5. 形成假设并生成测试用例。
6. 选择合适工具执行测试。
7. 保存中间操作、截图、请求证据、耗时和结论。
8. 生成可读 Markdown 图文报告。
9. 将单题报告汇总到本课程实验总报告中。

### 1.3 难度策略

本报告中的每类漏洞实验均采用统一的自动递进模式：提示词中不指定 `Difficulty`，由 `$dvwa-automated-testing` 按 `low -> medium -> high -> impossible` 依次推进。每个难度都要重新完成页面观察、源码分析、基线请求、测试设计、执行验证、截图取证、耗时统计和结论归档。

递进过程在遇到以下情况时停止：

- 当前难度已明确不可利用。
- 防护机制阻断继续利用。
- 结论因环境或工具限制无法确认。
- 继续测试可能破坏后续实验状态，例如触发长时间账户锁定。

若某一高难度等级无法利用，报告中必须说明：

- 尝试过的测试路径。
- 阻断利用的防护机制。
- 源码或响应证据。
- 为什么不能把已知合法凭据登录等同于漏洞利用成功。
- 后续若要继续需要什么条件。

## 2. 实验环境

### 2.1 基础环境

| 项目 | 当前配置 |
| --- | --- |
| 操作系统 | Windows |
| Web 集成环境 | phpStudy |
| Web 服务 | Apache/Nginx，默认监听 `127.0.0.1:80` |
| 数据库 | MySQL，常见端口 `3306` |
| 靶场 | DVWA |
| 靶场地址 | `http://127.0.0.1/DVWA/` 或 `http://127.0.0.1/dvwa/` |
| DVWA 源码 | `D:\phpStudy\PHPTutorial\WWW\DVWA` |
| Skill 项目 | `D:\WorkSpace\综合实践5\dvwa-skills` |
| 输出目录 | `D:\WorkSpace\综合实践5\dvwa-results` |

### 2.2 AI Skill 环境

本实验使用自定义 Codex skill：

```text
Skill 名称: dvwa-automated-testing
Skill 显示名: dvwa-automated-testing Web Lab Solver
项目目录: D:\WorkSpace\综合实践5\dvwa-skills
安装目录: C:\Users\31435\.codex\skills\dvwa-automated-testing
```

该 skill 的主要能力包括：

- 引导模型确认授权范围。
- 从页面和源码出发进行漏洞分析。
- 生成临时 Python/requests harness 或 Burp/ZAP 工作流。
- 支持只指定题型后从 low 自动向更高难度推进。
- 控制过程回复和报告语言。
- 生成包含截图、操作日志、耗时、证据和无解原因的 Markdown 图文报告。

### 2.3 工具范围

| 工具 | 用途 | 使用原则 |
| --- | --- | --- |
| Codex + `$dvwa-automated-testing` | 实验主流程引导、分析和报告生成 | 必须先观察页面和源码，不直接套答案 |
| Python / requests | 生成可复现实验 harness | 仅针对本机 DVWA |
| Burp Suite | 代理、抓包、Repeater、Intruder 对比验证 | 仅代理 DVWA 流量 |
| Burp MCP | 可选工具编排能力 | 仅当本机已启用 MCP |
| OWASP ZAP | 可选代理、被动分析、请求重放 | 不对外部目标扫描 |
| ffuf | 参数/路径 fuzz 或低难度演示 | 使用前必须明确请求模型 |
| sqlmap | SQL Injection 模块辅助验证 | 必须先有人工证明和认证请求 |
| IDA | 后续二进制题备用 | DVWA PHP Web 模块一般不用 |
| 浏览器 DevTools | DOM、JS、CSP、页面截图 | 用于前端类漏洞观察 |

## 3. 环境启动与检查

### 3.1 启动步骤

1. 启动 phpStudy。
2. 启动 Web 服务和 MySQL。
3. 浏览器访问 DVWA：

```text
http://127.0.0.1/DVWA/
```

4. 如数据库未初始化，访问：

```text
http://127.0.0.1/DVWA/setup.php
```

5. 登录 DVWA，默认实验账号通常为：

```text
admin / password
```

6. 可选：启动 Burp Suite，确认代理监听：

```text
127.0.0.1:8080
```

7. 可选：启用 Burp MCP，确认监听：

```text
127.0.0.1:9876
```

### 3.2 PowerShell 检查命令

检查 Python 依赖和工具状态：

```powershell
cd D:\WorkSpace\综合实践5\dvwa-skills
py -3.11 .\scripts\tool_check.py
```

检查端口监听：

```powershell
Test-NetConnection 127.0.0.1 -Port 80
Test-NetConnection 127.0.0.1 -Port 3306
Test-NetConnection 127.0.0.1 -Port 8080
Test-NetConnection 127.0.0.1 -Port 9876
```

端口含义：

- `80`：DVWA Web 服务。
- `3306`：MySQL。如 phpStudy 使用自定义端口，以实际配置为准。
- `8080`：Burp/ZAP 代理。
- `9876`：Burp MCP。

查看端口对应进程：

```powershell
Get-NetTCPConnection -State Listen -LocalPort 80,3306,8080,9876 |
  Select-Object LocalAddress,LocalPort,OwningProcess,
    @{Name='ProcessName';Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}} |
  Sort-Object LocalPort
```

检查 DVWA 页面：

```powershell
curl.exe -sS -L -o NUL -w "final_url=%{url_effective}`nstatus=%{http_code}`n" http://127.0.0.1/DVWA/
```

预期结果：最终 URL 通常为 `http://127.0.0.1/DVWA/login.php`，状态码为 `200`。

检查 Burp MCP：

```powershell
curl.exe -sS -o NUL -w "status=%{http_code}`n" http://127.0.0.1:9876
java -jar C:\Tools\burp-mcp-server\libs\mcp-proxy-all.jar --sse-url http://127.0.0.1:9876
```

说明：浏览器或 curl 访问 `9876` 返回 `403` 通常是正常现象；stdio proxy 输出 `Successfully connected to SSE server` 表示 MCP 连接正常。

检查 skill 安装：

```powershell
Get-Item C:\Users\31435\.codex\skills\dvwa-automated-testing | Format-List FullName,LinkType,Target
python C:\Users\31435\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\31435\.codex\skills\dvwa-automated-testing
```

预期结果：`LinkType` 为空，且输出 `Skill is valid!`。

## 4. 实验流程管理

### 4.1 开始实验

开始某类漏洞实验前，需要记录：

- 实验日期。
- DVWA URL。
- DVWA 登录账号。
- 漏洞模块。
- 难度递进策略，本报告固定为 `low -> medium -> high -> impossible`。
- 是否使用代理或 MCP。
- 输出目录。
- 本次提示词。

推荐提示词模板：

```text
Use $dvwa-automated-testing to solve my authorized local DVWA <MODULE> challenge.

Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, identify routes, forms, parameters, tokens, cookies, success/failure markers, form hypotheses, choose tools, generate a task-specific Python/requests harness or Burp workflow if needed, execute tests, and report evidence.

URL: http://127.0.0.1/DVWA/
Login: admin / password
Module: <MODULE>
Source path: D:\phpStudy\PHPTutorial\WWW\DVWA
Optional proxy: http://127.0.0.1:8080
Output language: zh-CN
Console language: zh-CN
No difficulty is specified. Start at low, then continue to medium, high, and impossible until a level is defended, blocked, or inconclusive. For each attempted level, repeat page inspection, source review, baseline probing, test generation, execution, evidence collection, automatic Playwright screenshot capture, and timing.
Report requirements: produce a readable Markdown report with detailed solving process, intermediate operations, operation log, timing summary with start time, finish time, and elapsed time, automatic Playwright screenshots or screenshot-not-captured notes with the failed command/error, evidence, difficulty progression table, result, remediation, limitations, and no-solution reason when a level is defended.
Course-report extraction requirements: add a compact zh-CN section named `实验总报告可提取信息`, containing `实验结论`, `各难度漏洞成因`, `解题步骤`, `使用工具与操作`, `核心 payload/测试输入`, `关键截图`, `复现步骤总结`, `impossible/无解原因`, `辅助脚本`, `起止时间和耗时`, and `人工验证关注点`. Keep payloads, paths, parameters, commands, and evidence snippets exact.
```

### 4.2 完成单题

单题完成标准：

- 已说明目标模块和难度范围。
- 已完成页面观察和源码分析。
- 已记录请求模型。
- 已生成并执行测试用例。
- 已保存关键证据和截图。
- 已给出漏洞结论或不可利用原因。
- 已生成可读 Markdown 图文报告。

### 4.3 归档题解

每类漏洞实验完成后，将单题报告中的以下内容提取到本文档对应分区：

- 难度推进表。
- 最高成功难度或停止难度。
- 关键源码分析。
- 关键请求/响应证据。
- 截图链接。
- 工具使用记录。
- 修复建议。
- AI 解题过程评价。

## 5. 证据与报告规范

### 5.1 截图要求

报告中应尽量包含以下截图：

- 登录或已认证状态。
- DVWA 安全等级设置页面。
- 目标模块初始页面。
- 关键源码片段。
- baseline 失败请求结果。
- 成功利用结果或防护阻断结果。
- Burp/ZAP 关键请求记录。

如果当前运行环境无法截图，应在报告中说明原因，并用源码片段、响应片段或代理记录替代。

### 5.2 操作日志要求

每个单题报告至少记录：

- 时间戳。
- 当前难度。
- 使用工具。
- 操作说明。
- 输入摘要。
- 输出摘要。
- 耗时。
- 证据文件路径。

## 6. DVWA 漏洞实验分区

下面每个分区后续均由对应单题 Markdown 报告补充。

### 6.1 Brute Force

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/brute/` |
| 实验难度 | `low -> medium -> high -> impossible` |
| 当前状态 | 已完成，单题报告见 `dvwa-results/brute-force-progression-20260602-094957/report.md` |
| 最高成功难度 | `high` |
| 停止原因 | `impossible` 具备 token、PDO 预处理、失败计数和 15 分钟锁定机制，判定为防御级别 |

难度推进结果：

| 难度 | 结论 | 漏洞或防护成因 | 关键证据 |
| --- | --- | --- | --- |
| `low` | 可利用 | GET 参数直接进入查询逻辑，无 token、无延迟、无锁定 | `admin / password` 返回 `Welcome to the password protected area admin` |
| `medium` | 可利用 | 增加输入转义和失败后 `sleep(2)`，但没有账户锁定或次数限制 | 错误请求约 2 秒延迟，最终仍成功验证 `admin / password` |
| `high` | 可利用 | 增加 `user_token` 和随机延迟，但 token 可在同一会话中逐次刷新 | 每次尝试前重新 GET 页面获取 fresh token 后成功 |
| `impossible` | 不可利用 | POST、CSRF token、PDO 预处理、3 次失败计数、15 分钟锁定 | 错误基线出现锁定提示，有效凭证登录只证明凭证正确 |

实验记录：

- 页面与请求模型：目标页面为 `http://127.0.0.1/dvwa/vulnerabilities/brute/`。登录和设置安全等级均先解析 `user_token`，再提交认证或安全等级表单。`low/medium` 使用 `GET username,password,Login`；`high` 在 GET 请求中增加 fresh `user_token`；`impossible` 使用 POST 表单 `username,password,Login,user_token`。
- 测试设计：每个难度先提交错误基线 `codex_probe_user:definitely_wrong_20260602`，再按 `admin:dvwa2026!`、`admin:letmein`、`admin:123456`、`admin:password` 顺序测试，避免直接把默认凭证作为首个尝试。`high` 每次尝试前刷新 token；`impossible` 只验证防护行为和一次有效凭证，不进行大规模错误尝试，避免触发真实账户锁定。
- 核心 payload/测试输入：`low/medium` 的成功请求为 `GET /dvwa/vulnerabilities/brute/?username=admin&password=password&Login=Login`；`high` 为同一请求追加 `user_token=<fresh token>`；`impossible` 为 `POST /dvwa/vulnerabilities/brute/`，字段为 `username=admin&password=password&Login=Login&user_token=<fresh token>`。
- 关键证据：本次递进共发起 `38` 个 HTTP 请求，harness 执行时间为 `2026-06-02T09:54:03+08:00` 至 `2026-06-02T09:54:22+08:00`，耗时 `19.735s`。`low/medium/high` 的成功标记均为 `Welcome to the password protected area admin`；`impossible` 防护提示包含 `Alternative, the account has been locked because of too many failed logins.`。证据文件位于 `dvwa-results/brute-force-progression-20260602-094957/requests/`，操作日志为 `operation-log.jsonl`，辅助脚本为 `generated-harnesses/brute_force_progression_harness.py`。
- 截图说明：原 Brute Force 单题运行时尚未启用 Playwright 自动截图，因此该单题主要依赖 HTTP 响应、源码和日志证据。当前 skill 已补充 Playwright 自动截图能力，后续漏洞实验会自动保存登录页、安全等级页、模块页和利用/防护证明页。
- 实验结论：`low`、`medium`、`high` 均存在可自动化验证的弱口令暴力破解风险；`medium` 的固定延迟和 `high` 的 token 只能提高尝试成本，不能代替账户级防爆破控制。`impossible` 不判定为可利用，因为有效凭证登录不等同于暴力破解成功。
- 修复建议：统一使用参数化查询；对账号和来源 IP 设置速率限制、失败计数和锁定策略；禁止默认弱口令；记录失败登录日志并告警；保留 CSRF token，但不能把 token 作为唯一防爆破措施。

### 6.2 Command Injection

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/exec/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 页面观察：待补充。
- 源码分析：待补充。
- Payload 设计：待补充。
- 系统命令执行证据：待补充。
- 防护绕过或失败原因：待补充。
- 修复建议：待补充。

### 6.3 CSRF

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/csrf/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 状态变更动作：待补充。
- Token/Referer/Origin 检查：待补充。
- 构造请求或页面：待补充。
- 成功或失败证据：待补充。
- 修复建议：待补充。

### 6.4 File Inclusion

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/fi/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 参数识别：待补充。
- 路径拼接与过滤分析：待补充。
- 本地文件包含证据：待补充。
- 防护机制：待补充。
- 修复建议：待补充。

### 6.5 File Upload

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/upload/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 上传表单分析：待补充。
- 后缀/MIME/内容检查：待补充。
- 上传路径与访问验证：待补充。
- 关键截图：待补充。
- 修复建议：待补充。

### 6.6 Insecure CAPTCHA

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/captcha/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 业务流程分析：待补充。
- CAPTCHA 校验位置：待补充。
- 请求篡改或流程绕过：待补充。
- 证据截图：待补充。
- 修复建议：待补充。

### 6.7 SQL Injection

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/sqli/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 输入点识别：待补充。
- SQL 拼接与过滤分析：待补充。
- 手工证明过程：待补充。
- sqlmap 使用情况，如有：待补充。
- 数据库回显证据：待补充。
- 修复建议：待补充。

### 6.8 SQL Injection Blind

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/sqli_blind/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 布尔/时间差异基线：待补充。
- 手工探测过程：待补充。
- 请求次数和耗时：待补充。
- sqlmap 使用情况，如有：待补充。
- 修复建议：待补充。

### 6.9 Weak Session IDs

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/weak_id/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- Session ID 样本采集：待补充。
- 规律分析：待补充。
- 可预测性验证：待补充。
- 截图与证据：待补充。
- 修复建议：待补充。

### 6.10 XSS DOM

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/xss_d/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- DOM sink 识别：待补充。
- URL/前端参数分析：待补充。
- Payload 和执行结果：待补充。
- 浏览器截图：待补充。
- 修复建议：待补充。

### 6.11 XSS Reflected

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/xss_r/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 输入点和输出上下文：待补充。
- 过滤逻辑：待补充。
- Payload 设计：待补充。
- 执行证据：待补充。
- 修复建议：待补充。

### 6.12 XSS Stored

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/xss_s/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 存储点和展示点：待补充。
- 数据库存储与输出上下文：待补充。
- Payload 设计：待补充。
- 持久化执行证据：待补充。
- 清理步骤：待补充。
- 修复建议：待补充。

### 6.13 CSP Bypass

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/csp/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- CSP 策略观察：待补充。
- 允许源和绕过思路：待补充。
- Payload 或资源加载证据：待补充。
- 浏览器控制台/截图：待补充。
- 修复建议：待补充。

### 6.14 JavaScript Attacks

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/javascript/` |
| 当前状态 | 待根据 skill 运行报告补充 |

实验记录：

- 前端逻辑分析：待补充。
- JavaScript 函数或混淆逻辑：待补充。
- 控制台操作记录：待补充。
- 成功或失败证据：待补充。
- 修复建议：待补充。

## 7. AI Skill 解题过程评价

每类漏洞完成后，从以下角度评价 `$dvwa-automated-testing` 的效果：

- 是否先观察页面和源码，而不是直接套用公开题解。
- 是否合理选择工具。
- 是否生成了可复现的临时 harness 或请求模板。
- 是否记录了失败尝试和防护原因。
- 是否生成了包含截图、证据、耗时和操作日志的 Markdown 报告。
- 是否在高难度或不可利用等级给出清晰原因。
- 是否有不必要的自动化、过度扫描或范围外行为。
