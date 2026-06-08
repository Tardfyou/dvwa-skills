# DVWA 自动化靶场解题Skill实验报告

## 0. 文档说明

本文档，用于记录本机 DVWA 授权靶场实验的完整生命周期：环境准备、启动检查、AI Skill 自动化解题和报告输出、漏洞复现、结果分析和最终总结。

后续每一类漏洞会先由 `$dvwa-automated-testing` skill 引导 Codex 在本机 DVWA 环境中完成分析和测试，并产出单题 Markdown 图文报告。随后再根据这些单题报告，把关键过程、截图、命令、证据和结论补充到本文档对应的实验分区。

实验过程逐步优化迭代Skill，对于靠前的漏洞解题报告，可能走一些无法截图，或者执行指令受限的弯路，在靠后的漏洞报告中会体现出对这些问题的解决和优化。

本文档默认只针对本机授权环境：

```text
DVWA URL: http://127.0.0.1/DVWA/ 或 http://127.0.0.1/dvwa/
DVWA 源码路径: D:\phpStudy\PHPTutorial\WWW\DVWA
Skill 项目路径: D:\...\dvwa-skills
Codex Skill 安装路径: C:\Users\...\.codex\skills\dvwa-automated-testing
实验输出目录: D:\...\dvwa-results
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
| Skill 项目 | `D:\...\dvwa-skills` |
| 输出目录 | `D:\...\dvwa-results` |

### 2.2 AI Skill 环境

本实验使用自定义 Codex skill：

```text
Skill 名称: dvwa-automated-testing
Skill 显示名: dvwa-automated-testing Web Lab Solver
项目目录: D:\...\dvwa-skills
安装目录: C:\Users\...\.codex\skills\dvwa-automated-testing
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
cd D:\...\dvwa-skills
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
Get-Item C:\Users\...\.codex\skills\dvwa-automated-testing | Format-List FullName,LinkType,Target
python C:\Users\...\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\...\.codex\skills\dvwa-automated-testing
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

Follow the agent solving protocol. Do not start from the bundled helper, public walkthrough answer, or known default answers. First inspect the live page and matching source code, identify routes, forms, parameters, tokens, cookies, success/failure markers, form hypotheses, choose tools, generate a task-specific Python/requests harness or Burp workflow if needed, execute tests, and report evidence. Do not infer exploitability from difficulty names: `high` is not automatically solvable, and `impossible` is not automatically unsolvable.

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
- 截图说明：Brute Force 子报告已后补 Playwright 运行截图，共 `14` 张，覆盖登录成功页、各难度安全等级页、各难度模块页、`low/medium/high` 成功 proof、`impossible` 防护提示和有效凭证仅验证页。截图目录为 `dvwa-results/brute-force-progression-20260602-094957/screenshots/`，截图脚本为 `generated-harnesses/brute_force_playwright_screenshots.py`。截图补拍时间晚于主 harness，不影响原始 HTTP 请求证据和耗时统计。
- 实验结论：`low`、`medium`、`high` 均存在可自动化验证的弱口令暴力破解风险；`medium` 的固定延迟和 `high` 的 token 只能提高尝试成本，不能代替账户级防爆破控制。`impossible` 不判定为可利用，因为有效凭证登录不等同于暴力破解成功。
- 修复建议：统一使用参数化查询；对账号和来源 IP 设置速率限制、失败计数和锁定策略；禁止默认弱口令；记录失败登录日志并告警；保留 CSRF token，但不能把 token 作为唯一防爆破措施。

### 6.2 Command Injection

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/exec/` |
| 实验难度 | `low -> medium -> high -> impossible` |
| 当前状态 | 已完成，单题报告见 `dvwa-results/command-injection-progression-20260602-102141/report.md` |
| 最高成功难度 | `high` |
| 停止原因 | `impossible` 使用 CSRF token 和四段数字 IP 校验，含命令分隔符输入被拒绝 |

难度推进结果：

| 难度 | 结论 | 漏洞或防护成因 | 关键证据 |
| --- | --- | --- | --- |
| `low` | 可利用 | `ip` 参数直接拼接到 `shell_exec('ping  ' . $target)` | `127.0.0.1 & whoami` 返回 `vin\31435` |
| `medium` | 可利用 | 黑名单只删除 `&&` 和 `;`，遗漏单个 `&` | `127.0.0.1 && whoami` 未执行，`127.0.0.1 & whoami` 成功 |
| `high` | 可利用 | 黑名单过滤 `&` 和带空格的 `| `，遗漏无空格管道 | `127.0.0.1 & whoami` 未执行，`127.0.0.1|whoami` 成功 |
| `impossible` | 不可利用 | token 校验后按 `.` 拆分输入，要求四段均为数字并重组 IP | `127.0.0.1 & whoami` 和 `127.0.0.1|whoami` 均返回 `ERROR: You have entered an invalid IP.` |

实验记录：

- 页面与请求模型：目标页面为 `http://127.0.0.1/dvwa/vulnerabilities/exec/`，表单使用 `POST`，核心字段为 `ip` 和 `Submit`；`impossible` 额外需要 fresh `user_token`。正常基线使用 `ip=127.0.0.1&Submit=Submit`，以 `TTL=128` 作为 ping 成功标记。
- 源码分析：`low.php` 直接读取 `$_REQUEST['ip']` 并拼接执行系统命令。`medium.php` 使用 `str_replace()` 删除 `&&` 和 `;`，但未过滤单个 `&`。`high.php` 扩展黑名单，过滤 `&` 和 `| ` 等字符串，但未过滤无空格的 `|whoami`。`impossible.php` 检查 token，将输入按 `.` 拆为四段，要求四段均为数字，再重组 IP 执行 ping，因此命令分隔符无法进入 shell。
- 测试设计：测试命令只使用本机无害输出验证 `whoami`，不执行写文件、删除、持久化或外连命令。每个难度先跑正常 ping 基线，再根据源码过滤规则提交最小 proof payload；`impossible` 每次提交前刷新 token，并测试含 `&` 和 `|` 的防御探针。
- 核心 payload/测试输入：`low` 使用 `ip=127.0.0.1 & whoami&Submit=Submit`；`medium` 先用 `ip=127.0.0.1 && whoami&Submit=Submit` 证明被过滤，再用 `ip=127.0.0.1 & whoami&Submit=Submit` 绕过；`high` 先用 `ip=127.0.0.1 & whoami&Submit=Submit` 证明被过滤，再用 `ip=127.0.0.1|whoami&Submit=Submit` 绕过；`impossible` 使用上述两个注入输入并携带 `user_token=<fresh token>` 验证被拒绝。
- 关键证据：本次递进共发起 `31` 个 HTTP 请求，harness 执行时间为 `2026-06-02T10:25:23+08:00` 至 `2026-06-02T10:25:50+08:00`，耗时 `26.373s`。`low/medium/high` 的命令执行标记均为 `whoami` 输出 `vin\31435`；`impossible` 防御标记为 `ERROR: You have entered an invalid IP.`。请求证据位于 `dvwa-results/command-injection-progression-20260602-102141/requests/`，操作日志为 `operation-log.jsonl`。
- 截图与辅助脚本：自动截图已生成，proof 截图包括 `screenshots/proof/low-proof.png`、`medium-proof.png`、`high-proof.png`、`impossible-proof.png`，模块截图位于各难度 `screenshots/<difficulty>/module-<difficulty>.png`。主脚本为 `generated-harnesses/command_injection_progression_harness.py`，截图脚本为 `generated-harnesses/command_injection_proof_screenshots.py`。
- 实验结论：`low`、`medium`、`high` 均存在命令注入风险，且黑名单过滤在 `medium/high` 中均可被源码导出的分隔符变体绕过。`impossible` 不判定为可利用，因为输入在进入命令执行前已经被严格 IP 格式校验拦截。
- 修复建议：不要将用户输入拼接进 shell 命令；必须执行系统命令时使用安全参数数组或专用库；对 IP 使用白名单校验，例如 `filter_var($ip, FILTER_VALIDATE_IP)`；避免黑名单过滤；降低 Web 服务账号权限并记录异常输入。

### 6.3 CSRF

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/csrf/` |
| 实验难度 | `low -> medium -> high -> impossible` |
| 当前状态 | 已完成，单题报告见 `dvwa-results/csrf-progression-20260602-103818/report.md` |
| 最高成功难度 | `medium`；`high` 为同源 fresh token 条件路径，不按盲跨站 CSRF 成功处理 |
| 停止原因 | `impossible` 同时要求 fresh `user_token` 和当前密码，未观察到独立 CSRF 漏洞 |

难度推进结果：

| 难度 | 结论 | 漏洞或防护成因 | 关键证据 |
| --- | --- | --- | --- |
| `low` | 可利用 | 密码修改接口为 GET 请求，无 CSRF token、无 Referer/Origin 校验、无当前密码校验 | 直接请求 `password_new=<tmp>&password_conf=<tmp>&Change=Change` 返回 `Password Changed.` |
| `medium` | 可利用 | Referer 校验只判断 `HTTP_REFERER` 是否包含 `SERVER_NAME` 子串 | `Referer: http://127.0.0.1.attacker.local/csrf.html` 绕过并修改密码 |
| `high` | 条件性可变更 | 需要 fresh `user_token`，阻止常规盲跨站 CSRF；但仍不要求当前密码 | 缺失/错误 token 失败，同源读取 fresh token 后可返回 `Password Changed.` |
| `impossible` | 不可利用 | 同时要求 fresh `user_token` 和 `password_current` 当前密码校验 | 错误当前密码返回 `Passwords did not match or current password incorrect.`；知道当前密码的合法请求才可变更 |

实验记录：

- 状态变更动作：目标页面为 `http://127.0.0.1/dvwa/vulnerabilities/csrf/`，实验动作是修改 `admin` 密码。每个难度均使用临时密码 `dvwa_csrf_tmp_<difficulty>_20260602` 进行验证，成功后通过 `test_credentials.php` 确认临时密码有效，再恢复为 `admin / password`。
- Token/Referer/Origin 检查：`low` 不检查 token 或 Referer。`medium` 对无 Referer 和外部 Referer 返回 `That request didn't look correct.`，但只做服务器名子串匹配，可被包含 `127.0.0.1` 的伪 Referer 绕过。`high` 表单含 `user_token`，缺失/错误 token 不能完成修改；同源 harness 读取 fresh token 后可修改。`impossible` 在 token 之外还要求提交正确 `password_current`。
- 构造请求或页面：`low` 核心请求为 `GET /dvwa/vulnerabilities/csrf/?password_new=dvwa_csrf_tmp_low_20260602&password_conf=dvwa_csrf_tmp_low_20260602&Change=Change`。`medium` 同请求附加 `Referer: http://127.0.0.1.attacker.local/csrf.html`。`high` 在请求中追加 `user_token=<fresh token>`。`impossible` 需要 `password_current=<current password>&password_new=<tmp>&password_conf=<tmp>&Change=Change&user_token=<fresh token>`。
- 成功或失败证据：HTTP harness 总请求数 `50`，开始时间 `2026-06-02T10:44:52+08:00`，结束时间 `2026-06-02T10:50:44+08:00`。`low/medium/high` 的成功响应标记为 `Password Changed.`，并通过 `test_credentials.php` 验证临时密码有效；`impossible` 的错误当前密码标记为 `Passwords did not match or current password incorrect.`，合法变更只在知道当前密码时成立。
- 关键截图与脚本：截图已生成 22 张，主要包括 `screenshots/low/proof-password-changed.png`、`screenshots/medium/proof-weak-referer.png`、`screenshots/high/token-aware-change.png`、`screenshots/impossible/wrong-current-password.png`、`screenshots/impossible/legitimate-change-with-current-password.png`，完整清单见 `screenshots/screenshots.json`。辅助脚本包括 `generated-harnesses/csrf_progression_harness.py`、`generated-harnesses/csrf_playwright_screenshots.js` 和 `generated-harnesses/fix_report.py`。
- 截图工具问题说明：本次 CSRF 运行首次调用 `npx.cmd -y -p playwright@1.60.0 node ...` 时失败，原因是生成的 Node 脚本通过 `require('playwright')` 加载模块，而临时 `npx -p` 执行方式没有让该外部脚本稳定解析到 `playwright` 包。随后在报告目录执行 `npm.cmd install playwright@1.60.0 --no-audit --no-fund`，让 `node_modules/playwright` 成为本地依赖，再运行 `node .\generated-harnesses\csrf_playwright_screenshots.js .\screenshots` 成功补齐 22 张截图。后续 skill 已要求优先使用已安装的 Python Playwright 截图 helper；若生成 Node Playwright 脚本，应先确保报告目录存在本地 `node_modules/playwright`。
- 实验结论：`low` 和 `medium` 存在明确 CSRF 漏洞；`high` 阻止盲跨站 CSRF，但在同源可读 token 的条件下仍可变更密码，因此记录为条件性路径而非外部盲打成功；`impossible` 因同时要求 fresh token 和当前密码，未发现独立 CSRF 可利用路径。
- 修复建议：所有状态变更请求应使用服务端绑定的 CSRF token；不要依赖 Referer 子串，应严格校验 Origin/Referer 作为辅助控制；密码修改必须要求当前密码或重新认证；Cookie 应设置 `HttpOnly`、`Secure` 和合适的 `SameSite` 策略。

### 6.4 File Inclusion

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/fi/` |
| 实验难度 | `low -> medium -> high -> impossible` |
| 当前状态 | 已完成，单题报告见 `dvwa-results/file-inclusion-progression-20260608-143425/report.md` |
| 最高成功难度 | `high` |
| 停止原因 | `impossible` 使用固定 allowlist，仅允许 `include.php,file1.php,file2.php,file3.php`，遍历、隐藏文件和 `file://` 均被拒绝 |

难度推进结果：

| 难度 | 结论 | 漏洞或防护成因 | 关键证据 |
| --- | --- | --- | --- |
| `low` | 可利用 | `page` 参数直接赋给 `$file`，入口 `index.php` 调用 `include($file)` | `page=../../robots.txt` 返回 `User-agent: *` 和 `Disallow: /` |
| `medium` | 可利用 | 仅用单次 `str_replace()` 删除 `../`、`..\` 和 URL 前缀，重叠序列可在替换后重新形成遍历 | `page=....//....//robots.txt` 成功包含 `robots.txt` |
| `high` | 可利用 | `fnmatch("file*", $file)` 只是前缀匹配，非严格 allowlist | `page=file://D:/phpStudy/PHPTutorial/WWW/DVWA/robots.txt` 成功包含本地文件 |
| `impossible` | 不可利用 | 固定允许 `include.php`、`file1.php`、`file2.php`、`file3.php`，其他输入返回错误 | `../../robots.txt`、`file4.php`、`file://.../robots.txt` 均返回 `ERROR: File not found!` |

实验记录：

- 页面与请求模型：目标页面为 `http://127.0.0.1/dvwa/vulnerabilities/fi/`，核心参数为 `GET page=<value>`。登录和安全等级设置仍通过 `login.php`、`security.php` 完成；每个难度均先访问合法页面如 `include.php`、`file1.php` 建立正常基线，再提交缺失文件或被拦截 payload 建立失败基线。
- 源码分析：`low.php` 第 4 行直接读取 `$_GET['page']`，`index.php` 第 36 行执行 `include($file)`。`medium.php` 第 7-8 行使用黑名单替换，但只替换一次，无法处理 `....//` 这类重叠遍历。`high.php` 第 7 行要求 `file*` 或 `include.php`，导致 `file://` 包装器和 `file4.php` 都满足前缀条件。`impossible.php` 第 7-12 行采用固定 allowlist，第 14-17 行拒绝 allowlist 外输入。
- 测试设计：所有 proof 均限定在本机 DVWA 目录内，只读包含 `robots.txt`、DVWA bundled 文件和隐藏示例文件；未使用外部 URL、远程回调、shell、持久化或破坏性文件访问。`high` 的可利用结论不是由难度名推断，而是由 `file://.../robots.txt` 响应内容和源码前缀匹配共同证明。
- 核心 payload/测试输入：`low` 使用 `page=../../robots.txt`；`medium` 先用 `page=../../robots.txt` 证明被改写失败，再用 `page=....//....//robots.txt` 绕过；`high` 先用 `page=../../robots.txt` 证明被拒绝，再用 `page=file4.php` 和 `page=file://D:/phpStudy/PHPTutorial/WWW/DVWA/robots.txt` 验证前缀绕过；`impossible` 使用 `page=../../robots.txt`、`page=file4.php`、`page=file://D:/phpStudy/PHPTutorial/WWW/DVWA/robots.txt` 验证防护。
- 关键证据：HTTP harness 共发起 `30` 个请求，执行时间为 `2026-06-08T14:36:15+08:00` 至 `2026-06-08T14:36:16+08:00`，耗时 `1.169s`。`low/medium/high` 的成功标记均为 `User-agent: *` 和 `Disallow: /`；`impossible` 的防护标记为 `ERROR: File not found!`。请求证据位于 `dvwa-results/file-inclusion-progression-20260608-143425/requests/`，操作日志为 `operation-log.jsonl`。
- 截图与辅助脚本：自动截图已生成，基础截图包括 `screenshots/low/module-low.png`、`medium/module-medium.png`、`high/module-high.png`、`impossible/module-impossible.png`，proof 截图包括 `screenshots/proof/low-proof.png`、`medium-proof.png`、`high-proof.png`、`impossible-proof.png`。主脚本为 `generated-harnesses/file_inclusion_progression_harness.py`，proof 截图脚本为 `generated-harnesses/file_inclusion_proof_screenshots.py`。
- 实验结论：`low`、`medium`、`high` 均存在文件包含风险，且 `medium/high` 的过滤或前缀控制均可被源码导出的路径变体绕过。`impossible` 不因名称被预设为无解，而是因为源码 allowlist 与三类探针响应共同证明未发现可利用包含路径。
- 修复建议：使用严格 allowlist 并比较规范化后的文件名；避免直接把用户输入传入 `include()`；禁用不必要的 `allow_url_include`；限制 PHP 可访问目录；降低错误信息暴露，避免泄露路径和 include warning。

### 6.5 File Upload

| 项目 | 内容 |
| --- | --- |
| 模块路径 | `vulnerabilities/upload/` |
| 实验难度 | `low -> medium -> high -> impossible` |
| 当前状态 | 已完成，单题报告见 `dvwa-results/file-upload-progression-20260608-144621/report.md` |
| 最高 PHP 执行成功难度 | `medium` |
| 最高有限漏洞难度 | `high`，可上传 Web 可访问的 `.php.jpg` polyglot，但当前服务器未执行 PHP |
| 停止原因 | `impossible` 使用 token、扩展名/MIME/图片内容校验、随机文件名和 GD 重编码，PHP marker 被剥离 |

难度推进结果：

| 难度 | 结论 | 漏洞或防护成因 | 关键证据 |
| --- | --- | --- | --- |
| `low` | 可利用，PHP echo marker 执行 | 原始文件名直接拼接到 `hackable/uploads/` 并 `move_uploaded_file()`，无扩展名、MIME、内容或 token 校验 | 访问 `http://127.0.0.1/dvwa/hackable/uploads/dvwa_upload_low_20260608.php` 返回 `DVWA_UPLOAD_PROOF_20260608`，且 `php_tag_present=False`、`executed_echo_only=True` |
| `medium` | 可利用，客户端 MIME 绕过后 PHP echo marker 执行 | 只检查 `$_FILES['uploaded']['type']` 是否为 `image/jpeg` 或 `image/png`，保留 `.php` 文件名 | `text/plain` 的 `.php` 被拒绝；同一 `.php` 声明为 `image/jpeg` 后上传成功并返回 marker |
| `high` | 有限漏洞，polyglot 可存储但未证明 PHP 执行 | 检查末尾扩展名和 `getimagesize()`，阻止普通 `.php` 和无效 `.jpg`，但保留原始文件名，允许真实 JPEG 追加 PHP marker 的 `.php.jpg` | `dvwa_upload_high_20260608.php.jpg` 上传成功；访问为 `content_type=image/jpeg`，`marker_present=True`、`php_tag_present=True`、`executed_echo_only=False` |
| `impossible` | 不可利用，本次防御有效 | 校验 `user_token`、扩展名、MIME、大小和 `getimagesize()`，随机化文件名，并使用 GD 重编码图片 | polyglot 被保存为 `d99a75736dcf8ec9d068b63faac18951.jpg`，访问结果 `marker_present=False`、`php_tag_present=False` |

实验记录：

- 上传表单分析：目标页面为 `http://127.0.0.1/dvwa/vulnerabilities/upload/`。表单为 `POST`，`enctype="multipart/form-data"`，字段包括 `MAX_FILE_SIZE=100000`、文件字段 `uploaded` 和提交字段 `Upload=Upload`。`impossible` 页面额外包含 fresh `user_token`。
- 源码分析：`index.php` 根据安全等级加载 `source/low.php`、`medium.php`、`high.php` 或 `impossible.php`。`low.php` 第 `5-9` 行直接拼接上传目录并移动文件。`medium.php` 第 `14-15` 行只信任客户端 MIME 和大小。`high.php` 第 `15-17` 行增加末尾扩展名和 `getimagesize()`，但第 `20` 行仍保留原始文件名。`impossible.php` 第 `5` 行检查 token，第 `18` 行随机化文件名，第 `23-26` 行做联合校验，第 `28-36` 行用 GD 重编码剥离追加内容。
- 测试设计：仅使用本机 harmless 上传证明，核心 payload 为 `<?php echo "DVWA_UPLOAD_PROOF_20260608"; ?>`。`low` 直接上传 `.php`；`medium` 先用 `text/plain` 建立失败基线，再将同一 `.php` 声明为 `image/jpeg`；`high` 分别验证 `.php` 和无效 `.jpg` 被拦截，再上传真实 JPEG 追加 PHP marker 的 `.php.jpg`；`impossible` 携带 fresh token 上传 `.php` 和 `.php.jpg` polyglot，观察随机命名和重编码效果。
- 核心 payload/测试输入：`low` 使用 `filename=dvwa_upload_low_20260608.php`、`Content-Type=application/x-php`；`medium` 成功用例为 `filename=dvwa_upload_medium_20260608.php`、`Content-Type=image/jpeg`；`high` polyglot 为 `filename=dvwa_upload_high_20260608.php.jpg`、`Content-Type=image/jpeg`；`impossible` 防御探针为 `filename=dvwa_upload_impossible_20260608.php.jpg`、`Content-Type=image/jpeg`、`user_token=<fresh token>`。
- 上传路径与访问验证：上传目录为 `D:\phpStudy\PHPTutorial\WWW\DVWA\hackable\uploads`，访问前缀为 `http://127.0.0.1/dvwa/hackable/uploads/`。`low/medium` 的访问响应长度为 `26`，正文为 `DVWA_UPLOAD_PROOF_20260608`。`high` 访问响应为 JPEG，marker 和 PHP tag 仍在文件字节中但未执行。`impossible` 返回随机文件 `d99a75736dcf8ec9d068b63faac18951.jpg`，访问后 marker 和 PHP tag 均不存在。
- 关键证据：本次递进共发起 `34` 个 HTTP 请求，harness 执行时间为 `2026-06-08T14:48:49+08:00` 至 `2026-06-08T14:48:50+08:00`，耗时 `0.988s`。请求证据位于 `dvwa-results/file-upload-progression-20260608-144621/requests/`，操作日志为 `operation-log.jsonl`，机器可读结果为 `report.json`。
- 截图与辅助脚本：自动截图已生成，proof 截图包括 `screenshots/proof/low-proof.png`、`medium-proof.png`、`high-proof.png`、`impossible-proof.png`，模块截图位于 `screenshots/<difficulty>/module-<difficulty>.png`。主脚本为 `generated-harnesses/file_upload_progression_harness.py`，截图脚本为 `generated-harnesses/file_upload_proof_screenshots.py`。
- 清理结果：正式 harness 删除了 `dvwa_upload_low_20260608.php`、`dvwa_upload_medium_20260608.php`、`dvwa_upload_high_20260608.php.jpg` 和 `d99a75736dcf8ec9d068b63faac18951.jpg`；截图脚本临时上传文件也全部删除；收尾时手工删除预探测残留 `3945d230292b5308f97a079c5444cd91.jpg`。最终上传目录只保留 DVWA 默认 `dvwa_email.png`。
- 实验结论：`low` 和 `medium` 存在可直接证明的危险文件上传到 PHP 执行风险；`high` 存在 Web 可访问 polyglot 存储风险，但当前服务器未执行 `.php.jpg`，不能写成 PHP RCE；`impossible` 通过严格校验和重编码防住了本次测试。
- 修复建议：上传目录不要允许脚本解释；不要信任客户端 `Content-Type`；使用服务端白名单、文件签名和内容校验；对图片执行重编码；使用随机服务端文件名；限制大小、尺寸、数量和频率；展示或下载时设置准确 `Content-Type` 与 `X-Content-Type-Options: nosniff`；记录上传审计日志并保留 CSRF token。

### 6.6 后续未测模块概览

本课程实验报告的详细自动化解题记录到 `6.5 File Upload` 为止。`6.6` 及之后的 DVWA 模块本次不再逐题运行 `$dvwa-automated-testing`，因此不补充难度推进表、源码证据、请求/响应证据、截图、payload、耗时或修复验证结果。下表仅保留模块类型介绍和后续如需扩展时的观察重点。

| 原编号 | 模块 | 模块路径 | 漏洞类型简介 | 本报告处理方式 |
| --- | --- | --- | --- | --- |
| 6.6 | Insecure CAPTCHA | `vulnerabilities/captcha/` | 验证码流程或服务端校验位置设计不当，可能导致关键业务步骤绕过。 | 仅做类型介绍，不再填充实验结果。 |
| 6.7 | SQL Injection | `vulnerabilities/sqli/` | 用户输入进入 SQL 查询构造，可能造成条件绕过、数据枚举或数据库信息泄露。 | 仅做类型介绍，不再填充实验结果。 |
| 6.8 | SQL Injection Blind | `vulnerabilities/sqli_blind/` | 页面无直接回显时，通过布尔差异、时间延迟或响应长度推断 SQL 查询结果。 | 仅做类型介绍，不再填充实验结果。 |
| 6.9 | Weak Session IDs | `vulnerabilities/weak_id/` | 会话标识生成规律弱，可能被预测、枚举或重放。 | 仅做类型介绍，不再填充实验结果。 |
| 6.10 | XSS DOM | `vulnerabilities/xss_d/` | 前端 JavaScript 从 URL、hash 或 DOM 读取不可信数据并写入危险 sink。 | 仅做类型介绍，不再填充实验结果。 |
| 6.11 | XSS Reflected | `vulnerabilities/xss_r/` | 请求参数被服务端即时反射到响应页面，输出编码不足时可能触发脚本执行。 | 仅做类型介绍，不再填充实验结果。 |
| 6.12 | XSS Stored | `vulnerabilities/xss_s/` | 恶意输入被存储到后端并在后续页面展示时执行，影响范围通常大于反射型 XSS。 | 仅做类型介绍，不再填充实验结果。 |
| 6.13 | CSP Bypass | `vulnerabilities/csp/` | CSP 策略配置过宽或信任源可被利用，导致原本应被限制的脚本或资源加载绕过。 | 仅做类型介绍，不再填充实验结果。 |
| 6.14 | JavaScript Attacks | `vulnerabilities/javascript/` | 前端校验、混淆逻辑或客户端生成参数被逆向分析后绕过。 | 仅做类型介绍，不再填充实验结果。 |

若后续需要继续扩展，应重新按本文档前述统一流程执行：确认授权范围，设置难度，观察页面和源码，生成最小测试计划，保存请求证据和截图，再把对应单题报告追加到本节之后。

## 7. AI Skill 解题过程评价

每类漏洞完成后，从以下角度评价 `$dvwa-automated-testing` 的效果：

- 是否先观察页面和源码，而不是直接套用公开题解。
- 是否合理选择工具。
- 是否生成了可复现的临时 harness 或请求模板。
- 是否记录了失败尝试和防护原因。
- 是否生成了包含截图、证据、耗时和操作日志的 Markdown 报告。
- 是否在高难度或不可利用等级给出清晰原因。
- 是否有不必要的自动化、过度扫描或范围外行为。

## 8. 泛化能力调研与增量改进

### 8.1 当前结论

原始 `$dvwa-automated-testing` 已经具备较好的 DVWA 单模块自动解题能力：能按页面观察、源码分析、请求建模、payload 设计、自动截图、证据归档和 Markdown 报告的流程完成实验。但如果直接面对一个新的网页 URL 或新靶场，早期版本仍偏向“DVWA 模块/难度递进”语境，泛化能力不足主要体现在：

- 入口假设偏 DVWA，需要补充通用授权范围、同源边界、认证状态和测试强度确认。
- 报告结构偏单题 walkthrough，需要补充渗透测试报告中的资产地图、发现表、风险分级、复现步骤、影响和修复建议。
- 工具选择已有 Playwright、Python、Burp、ZAP、ffuf、sqlmap 等说明，但缺少“先观察建模，再按假设调用工具”的通用 Web 评估模式。
- 辅助脚本可用于收集证据，但不能作为固定扫描流程，否则无法满足“新开 Codex 窗口调用 skill 后由 AI 自主完成渗透测试”的目标。

因此本次增量改进的方向不是写死扫描脚本，而是在 skill 中新增 `Authorized Web Assessment Mode`：要求 Codex 在明确授权后，自主浏览目标、建立页面/表单/API/会话模型，选择 Playwright、Python、ZAP、Burp 等工具做低风险验证，最后输出图文详实的渗透测试 Markdown 报告。

### 8.2 已完成的 Skill 改进

| 文件 | 改进内容 |
| --- | --- |
| `SKILL.md` | 新增授权 Web 评估模式；明确新靶场不走 DVWA 难度递进；强调 agent 主导，不以固定脚本为主流程。 |
| `references/authorized-web-assessment.md` | 新增通用 Web 评估工作流、授权边界、默认禁止动作、报告结构和可复制提示词。 |
| `references/usage.md` | 新增 OWASP Juice Shop 新窗口测试提示词；整理 DVWA 单难度和递进提示词；修正中文字段。 |
| `references/tool-capabilities.md` | 增加通用授权评估工具契约，明确 ZAP 被动告警只是线索，需由浏览器、请求、源码或 harness 复核。 |
| `references/reporting-and-artifacts.md` | 新增通用 Web 渗透测试报告结构，包括资产地图、发现表、详细发现、截图、复现、修复和限制。 |
| `scripts/authorized_web_assessment.py` | 保留为可选证据采集助手；改进为默认不把静态资源当页面截图，并从 HTML/同源 JS 中提取 API 线索。 |
| `scripts/check_and_start_lab_tools.ps1` | 用于快速检查并按需启动 phpStudy、Burp、ZAP 等本地工具。 |

### 8.3 模拟真实环境测试靶场

本地已部署 OWASP Juice Shop 作为模拟真实 Web 应用靶场：

```text
源码目录: D:\WorkSpace\综合实践5\targets\juice-shop
访问地址: http://127.0.0.1:3000/
启动方式: node build/app
ZAP API: http://127.0.0.1:8090/
```

如果进程未运行，可在 PowerShell 中启动：

```powershell
Start-Process -FilePath node.exe -ArgumentList "build/app" -WorkingDirectory "D:\WorkSpace\综合实践5\targets\juice-shop" -WindowStyle Hidden
```

如需重新安装或构建，使用：

```powershell
cd D:\WorkSpace\综合实践5\targets\juice-shop
npm.cmd install
npm.cmd run build:frontend
npm.cmd run build:server
node build/app
```

### 8.4 通用 Web 评估提示词

```text
Use $dvwa-automated-testing in authorized web assessment mode against my local simulated target.

Target URL: http://127.0.0.1:3000/
Authorization: This is my local OWASP Juice Shop lab running on 127.0.0.1, and I authorize same-origin testing.
Assessment mode: passive/safe first, then targeted harmless verification only when a hypothesis is supported by observed evidence.
Scope: same-origin only. Do not scan other hosts, ports, or external networks.
Credentials: no credentials initially; create or use a lab account only if the application workflow requires it and record the account state.
Source path: D:\WorkSpace\综合实践5\targets\juice-shop
Tools: use Playwright/browser exploration and screenshots, Python/requests for targeted harnesses, ZAP spider/passive alerts if available at http://127.0.0.1:8090, and Burp only if useful. Do not rely on a fixed helper script as the primary workflow.
Output language: zh-CN
Report output directory: D:\WorkSpace\综合实践5\dvwa-results
Report requirements: produce a detailed Markdown penetration testing report with scope, methodology, application map, crawled pages, forms/API hints, screenshots, security headers, ZAP passive alerts, verified findings, evidence, severity/confidence triage, reproduction steps, remediation, operation timeline, artifacts, limitations, and next recommended manual verification steps.
Prohibited actions: no destructive payloads, no credential attacks, no web shells, no reverse shells, no persistence, no external callbacks, no ZAP active scan, and no out-of-scope network access.
```

### 8.5 后续增强方向

当前改进重点是让现有工具链被合理调用：Playwright 做真实浏览器观察和截图，Python/requests 做小型复现 harness，ZAP 做爬虫和被动告警，Burp 做代理抓包和重放，ffuf/sqlmap 在明确输入点后再使用。后续如果继续加强 skill，可按工具能力继续扩展：

- 增加认证态录制与复用，例如保存 Playwright storage state。
- 增加 Burp/ZAP 导出证据的统一报告模板。
- 增加 API 规范识别，如 OpenAPI、GraphQL introspection 的授权检查流程。
- 增加安全测试强度分级，从 passive、safe-targeted 到 explicitly-authorized-active。
- 增加更多靶场回归目标，例如 WebGoat、bWAPP、Mutillidae、PortSwigger Web Security Academy 本地/授权题目。
- 增加更多可支配渗透测试工具。
