from __future__ import annotations

import html
import re
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "scripts" else SCRIPT_DIR
OUT_DIR = ROOT / "final-reports" / "AI在网络安全中的应用研究"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SKILL_ROOT = ROOT / "dvwa-skills" if (ROOT / "dvwa-skills").exists() else ROOT
RESULTS_ROOT = ROOT / "dvwa-results" if (ROOT / "dvwa-results").exists() else ROOT / "experiment-artifacts" / "dvwa-results"

DOCS = [
    ("第一部分 DVWA 自动化靶场解题 Skill 实验总报告", SKILL_ROOT / "DVWA全自动攻击.md"),
    ("第二部分 Brute Force 单题输出报告", RESULTS_ROOT / "brute-force-progression-20260602-094957" / "report.md"),
    ("第三部分 Command Injection 单题输出报告", RESULTS_ROOT / "command-injection-progression-20260602-102141" / "report.md"),
    ("第四部分 CSRF 单题输出报告", RESULTS_ROOT / "csrf-progression-20260602-103818" / "report.md"),
    ("第五部分 File Inclusion 单题输出报告", RESULTS_ROOT / "file-inclusion-progression-20260608-143425" / "report.md"),
    ("第六部分 File Upload 单题输出报告", RESULTS_ROOT / "file-upload-progression-20260608-144621" / "report.md"),
    ("第七部分 OWASP Juice Shop 授权主动渗透测试输出报告", RESULTS_ROOT / "juice-shop-assessment-20260608-152215" / "report.md"),
]


def file_uri_for_link(base_dir: Path, link: str) -> str:
    raw = link.strip()
    if not raw or raw.startswith(("#", "http://", "https://", "data:", "mailto:", "file:")):
        return link
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    target = (base_dir / raw).resolve()
    return target.as_uri() if target.exists() else link


def rewrite_markdown_image_paths(text: str, base_dir: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, link, suffix = match.group(1), match.group(2), match.group(3)
        return f"{prefix}{file_uri_for_link(base_dir, link)}{suffix}"

    text = re.sub(r"(!\[[^\]]*\]\()([^)]+)(\))", repl, text)

    def html_repl(match: re.Match[str]) -> str:
        prefix, link, suffix = match.group(1), match.group(2), match.group(3)
        return f"{prefix}{file_uri_for_link(base_dir, link)}{suffix}"

    return re.sub(r"(<img\b[^>]*\bsrc=[\"'])([^\"']+)([\"'][^>]*>)", html_repl, text, flags=re.IGNORECASE)


def make_architecture_svg(path: Path) -> str:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="720" viewBox="0 0 1200 720">
<style>
text{font-family:'Microsoft YaHei','SimHei',sans-serif;fill:#172033}
.title{font-size:30px;font-weight:700}
.box{fill:#f8fafc;stroke:#2f5597;stroke-width:2;rx:12}
.box2{fill:#eef7ff;stroke:#1b75bb;stroke-width:2;rx:12}
.box3{fill:#fff7ed;stroke:#c2410c;stroke-width:2;rx:12}
.box4{fill:#f0fdf4;stroke:#15803d;stroke-width:2;rx:12}
.label{font-size:22px;font-weight:700}
.small{font-size:17px}
.arrow{stroke:#334155;stroke-width:3;marker-end:url(#arrow)}
</style>
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#334155"/></marker></defs>
<text x="60" y="55" class="title">AI 辅助网络安全实验与渗透测试体系架构</text>
<rect x="55" y="105" width="245" height="145" class="box"/>
<text x="80" y="145" class="label">授权目标层</text>
<text x="80" y="180" class="small">DVWA 本机靶场</text>
<text x="80" y="210" class="small">OWASP Juice Shop</text>
<text x="80" y="240" class="small">源码与运行环境</text>
<rect x="370" y="105" width="265" height="145" class="box2"/>
<text x="395" y="145" class="label">AI 编排层</text>
<text x="395" y="180" class="small">Codex + dvwa skill</text>
<text x="395" y="210" class="small">观察-建模-假设-验证</text>
<text x="395" y="240" class="small">报告自动整理</text>
<rect x="705" y="105" width="430" height="145" class="box3"/>
<text x="730" y="145" class="label">工具执行层</text>
<text x="730" y="180" class="small">Playwright / Python requests / Burp / ZAP</text>
<text x="730" y="210" class="small">ffuf / sqlmap / 源码审阅 / 截图采集</text>
<text x="730" y="240" class="small">主动验证、证据保存、状态清理</text>
<line x1="300" y1="178" x2="370" y2="178" class="arrow"/>
<line x1="635" y1="178" x2="705" y2="178" class="arrow"/>
<rect x="55" y="330" width="1080" height="115" class="box4"/>
<text x="80" y="370" class="label">证据与报告层</text>
<text x="80" y="405" class="small">Markdown 图文报告、请求/响应 JSON、operation-log、截图、ZAP/ffuf/sqlmap 输出、复现步骤、修复建议</text>
<line x1="920" y1="250" x2="920" y2="330" class="arrow"/>
<rect x="55" y="520" width="320" height="120" class="box"/>
<text x="80" y="560" class="label">原理分析</text>
<text x="80" y="595" class="small">漏洞成因、输入流向、认证/授权</text>
<text x="80" y="625" class="small">过滤缺陷、防护机制与绕过路径</text>
<rect x="440" y="520" width="320" height="120" class="box"/>
<text x="465" y="560" class="label">失败分析</text>
<text x="465" y="595" class="small">截图依赖、编码、工具可达性</text>
<text x="465" y="625" class="small">误报、不可利用与环境差异</text>
<rect x="815" y="520" width="320" height="120" class="box"/>
<text x="840" y="560" class="label">安全建设闭环</text>
<text x="840" y="595" class="small">发现-验证-复现-修复-复测</text>
<text x="840" y="625" class="small">沉淀为可复用 Skill 与流程</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")
    return path.as_uri()


def supplemental_markdown(architecture_uri: str) -> str:
    return f"""
# 第八部分 综合分析：AI 在网络安全中的应用研究

## 8.1 体系架构

本研究形成了“授权目标层 - AI 编排层 - 工具执行层 - 证据与报告层 - 安全建设闭环”的体系。DVWA 用于验证单点漏洞的可控解题能力，OWASP Juice Shop 用于验证面对更接近真实应用的综合渗透测试能力。

![AI 辅助网络安全实验与渗透测试体系架构]({architecture_uri})

### 架构说明

| 层级 | 组成 | 作用 |
| --- | --- | --- |
| 授权目标层 | DVWA、OWASP Juice Shop、源码目录、phpStudy/Node/ZAP/Burp 运行环境 | 提供可控、可复现、可主动验证的网络安全实验对象 |
| AI 编排层 | Codex 与 `$dvwa-automated-testing` skill | 完成范围确认、页面观察、源码审阅、请求建模、假设生成、工具选择和报告生成 |
| 工具执行层 | Playwright、Python/requests、Burp、ZAP、ffuf、sqlmap | 支撑截图、请求重放、主动扫描、fuzz、注入复核和证据保存 |
| 证据与报告层 | Markdown、截图、JSON、operation-log、请求证据、扫描输出 | 将实验过程转化为可审计、可复现、可用于修复的图文报告 |
| 安全建设闭环 | 漏洞发现、复现、影响分析、修复建议、复测 | 将 AI 自动化结果转化为人工修复和安全治理输入 |

## 8.2 实验过程说明

本报告前半部分保留了 DVWA 全自动攻击总报告、五项 DVWA 漏洞单题报告和 Juice Shop 主动渗透测试报告。整体实验流程如下：

1. 在本机授权靶场中启动目标服务和工具环境。
2. 使用 Codex skill 读取页面、源码、表单、参数、Cookie、Token 和响应特征。
3. 针对 DVWA 的 Brute Force、Command Injection、CSRF、File Inclusion、File Upload 五类漏洞，从 low 到 impossible 逐级分析。
4. 对 Juice Shop 执行主动综合评估，包括浏览器路由探索、API 暴露、登录 SQL 注入绕过、搜索 SQL 注入、DOM XSS、NoSQL 探针、目录索引、CORS、CSP、metrics/API docs 暴露、ZAP active scan、ffuf 和 sqlmap 复核。
5. 使用 Playwright 自动截图，保存 proof 页面、模块页面、目录索引、API 文档、metrics 页面和 XSS 弹窗证据。
6. 输出 Markdown 图文报告，并最终汇总为本 PDF。

## 8.3 关键截图与证据汇总

| 实验 | 代表截图 | 说明 |
| --- | --- | --- |
| Brute Force | `brute-force.../screenshots/proof/high-success-admin-password.png` | high 难度中通过 fresh token 逐次验证弱口令 |
| Command Injection | `command-injection.../screenshots/proof/high-proof.png` | high 难度中使用无空格管道绕过黑名单 |
| CSRF | `csrf.../screenshots/medium/proof-weak-referer.png` | medium 难度中 Referer 子串校验可被绕过 |
| File Inclusion | `file-inclusion.../screenshots/proof/high-proof.png` | high 难度中 `file://` 前缀绕过证明本地文件包含 |
| File Upload | `file-upload.../screenshots/proof/medium-proof.png` | medium 难度中伪造 MIME 后上传并执行 PHP marker |
| Juice Shop | `juice-shop.../screenshots/xss-search-proof.png` | 搜索参数触发 DOM XSS，Playwright 捕获 dialog |

这些截图在前述原始报告中已经以内嵌图片方式展示。它们共同证明 AI 不只输出结论，还能沉淀过程证据。

## 8.4 原理分析

### 8.4.1 AI 辅助漏洞发现原理

AI 在本实验中的作用不是替代安全原理，而是将人工渗透测试中的观察、建模、验证和报告编排自动化。其核心能力包括：

- 从页面和源码中抽取输入点、状态参数、Token、Cookie、路由和响应标记。
- 将输入点映射到漏洞假设，例如 SQL 注入、命令注入、CSRF、文件包含、文件上传、XSS 和访问控制问题。
- 根据假设选择工具，例如 Playwright 用于浏览器证据，Python/requests 用于请求复现，ZAP 用于主动扫描，ffuf 用于路径发现，sqlmap 用于注入复核。
- 把失败尝试、不可利用原因和防护机制纳入报告，而不是只记录成功 payload。

### 8.4.2 DVWA 五项漏洞原理

- Brute Force：low/medium/high 缺少账户级锁定或有效速率限制，token 与延迟只能提高成本；impossible 增加预处理、Token、失败计数和锁定机制。
- Command Injection：low 直接拼接命令；medium/high 依赖黑名单，遗漏分隔符变体；impossible 使用 IP 格式白名单阻断 shell 元字符进入命令。
- CSRF：low 无 Token，medium Referer 子串校验弱，high 通过 fresh token 抑制盲打，impossible 增加当前密码校验。
- File Inclusion：low 直接 include 用户输入，medium 单次替换可被重叠路径绕过，high 前缀匹配允许 `file://`，impossible 使用固定 allowlist。
- File Upload：low/medium 可上传并执行 PHP，high 可存储 polyglot 但受服务器解析限制未执行，impossible 通过 Token、扩展名/MIME/内容校验、随机文件名和重编码剥离 marker。

### 8.4.3 Juice Shop 综合漏洞原理

Juice Shop 实验验证了 AI skill 从单题 CTF 模式扩展到综合 Web 应用评估的能力。其原理包括：

- 对 SPA 路由、REST API 和静态资源进行综合建模。
- 使用 SQL 注入登录绕过证明认证绕过风险。
- 使用 XSS payload 和浏览器 dialog 证明前端 DOM 执行风险。
- 通过公开目录、Swagger UI、metrics 和配置接口证明信息暴露风险。
- 使用 ZAP active scan、ffuf、sqlmap 与自定义 harness 交叉验证工具发现。

## 8.5 失败分析与改进

### 8.5.1 截图失败与修复

早期 Brute Force 报告缺少运行截图，CSRF 报告中曾出现 Node Playwright 依赖解析失败。失败原因是临时 `npx -p playwright node <script>` 无法稳定让外部脚本 `require('playwright')`。后续改进为优先使用 Python Playwright，或在报告目录安装本地 Node Playwright 后再运行截图脚本。

### 8.5.2 编码与中文报告问题

PowerShell 直接显示 UTF-8 Markdown 时可能出现中文乱码，但文件本身可由 Python UTF-8 正确读取。因此报告生成流程中使用 Python 读取和写入 UTF-8，避免把控制台显示乱码误判为文件损坏。

### 8.5.3 工具可用性与误报

ZAP、ffuf、sqlmap 等工具能提高覆盖面，但扫描结果不是最终结论。ZAP passive/active alerts 需要通过浏览器证据、请求复现、源码审阅或 harness 输出确认。sqlmap 也需要先有明确请求模型，避免对无关参数做无效扫描。

### 8.5.4 防护等级与可利用性判断

DVWA 的 `high` 不一定可利用，`impossible` 也不能仅凭名称判定不可利用。报告中必须以源码、响应、截图、状态变化和请求证据作为判断依据。例如 File Upload high 只能证明 polyglot 存储，不能在当前服务器配置下写成 PHP RCE。

### 8.5.5 主动测试边界

网络安全建设需要完整发现问题，因此在明确授权的本地靶场中应允许登录绕过、注入、主动扫描、fuzz 和上传验证等手段。实际生产环境中仍需要独立授权、影响评估、时间窗口和回滚方案。本研究中的边界是本机授权靶场和模拟真实环境，所有结果用于修复验证和安全能力建设。

## 8.6 研究结论

本研究表明，AI skill 可以把 Web 安全实验中的重复性工作自动化，包括环境检查、页面观察、源码审阅、测试用例生成、工具调用、截图取证和报告编写。DVWA 五项漏洞验证了 AI 对单点漏洞机制的推理和复现能力；Juice Shop 验证了 AI 面对综合 Web 应用时的主动评估能力。

AI 在网络安全中的价值主要体现在：

- 提升漏洞发现和复现效率。
- 降低报告整理和证据归档成本。
- 将工具输出转化为可读、可修复、可审计的安全报告。
- 通过失败分析推动工具链和工作流持续改进。

其局限也较明确：

- AI 需要明确授权边界和目标上下文。
- 工具输出需要证据复核，不能直接等同于确认漏洞。
- 对复杂业务逻辑、权限模型和真实生产影响仍需要人工安全专家判断。

因此，AI 更适合作为安全工程师的自动化协作层，而不是无监督替代者。合理的落地方式是让 AI 承担信息收集、初步验证、证据整理和报告生成，把人工精力集中在业务风险判断、修复决策和复测闭环上。
"""


def build_combined_markdown() -> str:
    arch_uri = make_architecture_svg(OUT_DIR / "architecture.svg")
    parts: list[str] = [
        "# AI在网络安全中的应用研究",
        "",
        "## 摘要",
        "",
        "本文围绕 AI 辅助网络安全实验与授权渗透测试展开研究，以 DVWA 本机靶场和 OWASP Juice Shop 本地模拟真实应用为实验对象，验证 AI 在环境检查、漏洞分析、工具编排、主动验证、截图取证和报告生成中的应用价值。",
        "",
        "研究内容包括：DVWA 自动化靶场解题 Skill 实验总报告、Brute Force、Command Injection、CSRF、File Inclusion、File Upload 五项漏洞的图文输出报告，以及 OWASP Juice Shop 主动综合渗透测试报告。最后从体系架构、实验过程、漏洞原理、失败原因和安全建设闭环角度进行综合分析。",
        "",
        "## 研究范围",
        "",
        "- 实验对象：本机授权 DVWA 靶场与 OWASP Juice Shop 靶场。",
        "- 技术方法：AI 编排、浏览器自动化、源码审阅、请求复现、主动扫描、fuzz、注入复核和证据归档。",
        "- 输出形式：Markdown、HTML 和 PDF 图文报告。",
        "- 目标价值：形成可复现、可审计、可用于修复验证的网络安全实验流程。",
        "",
        '<div class="page-break"></div>',
    ]
    for title, path in DOCS:
        if not path.exists():
            raise FileNotFoundError(path)
        body = path.read_text(encoding="utf-8")
        body = rewrite_markdown_image_paths(body, path.parent)
        parts.extend([f"# {title}", "", body, "", '<div class="page-break"></div>', ""])
    parts.append(supplemental_markdown(arch_uri))
    return "\n".join(parts)


def render_pdf(markdown_text: str) -> None:
    combined_md = OUT_DIR / "AI在网络安全中的应用研究.md"
    combined_html = OUT_DIR / "AI在网络安全中的应用研究.html"
    combined_pdf = OUT_DIR / "AI在网络安全中的应用研究.pdf"
    combined_md.write_text(markdown_text, encoding="utf-8")

    body = markdown.markdown(
        markdown_text,
        extensions=["extra", "tables", "fenced_code", "sane_lists", "toc"],
        output_format="html5",
    )
    css = """
@page { size: A4; margin: 18mm 14mm 18mm 14mm; }
body {
  font-family: "Microsoft YaHei", "SimHei", "SimSun", Arial, sans-serif;
  color: #111827;
  line-height: 1.62;
  font-size: 13px;
}
h1, h2, h3, h4 { color: #0f172a; line-height: 1.28; }
h1 { font-size: 26px; border-bottom: 2px solid #1f4e79; padding-bottom: 8px; }
h2 { font-size: 21px; margin-top: 28px; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; }
h3 { font-size: 17px; margin-top: 22px; }
code, pre { font-family: Consolas, "Microsoft YaHei", monospace; }
pre {
  background: #f8fafc;
  border: 1px solid #d8dee9;
  padding: 10px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
}
code { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; }
table { width: 100%; border-collapse: collapse; margin: 12px 0 18px; font-size: 12px; page-break-inside: auto; }
th, td { border: 1px solid #cbd5e1; padding: 6px 8px; vertical-align: top; word-break: break-word; }
th { background: #e2e8f0; font-weight: 700; }
tr { page-break-inside: avoid; page-break-after: auto; }
img { max-width: 100%; height: auto; border: 1px solid #d0d7de; border-radius: 4px; margin: 8px 0 14px; }
blockquote { border-left: 4px solid #94a3b8; padding-left: 12px; color: #475569; }
.page-break { break-after: page; page-break-after: always; height: 0; }
a { color: #0b5cad; text-decoration: none; }
"""
    html_doc = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>AI在网络安全中的应用研究</title>
  <style>{css}</style>
</head>
<body>{body}</body>
</html>
"""
    combined_html.write_text(html_doc, encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(combined_html.resolve().as_uri(), wait_until="networkidle", timeout=120000)
        page.evaluate(
            """async () => {
                const imgs = Array.from(document.images);
                await Promise.all(imgs.map(img => img.complete ? Promise.resolve() : new Promise(resolve => {
                    img.onload = resolve;
                    img.onerror = resolve;
                })));
            }"""
        )
        page.pdf(
            path=str(combined_pdf),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template="<div style='font-size:9px;width:100%;text-align:center;color:#64748b;'>AI在网络安全中的应用研究 - 第 <span class='pageNumber'></span> / <span class='totalPages'></span> 页</div>",
            margin={"top": "18mm", "right": "14mm", "bottom": "18mm", "left": "14mm"},
        )
        browser.close()


if __name__ == "__main__":
    render_pdf(build_combined_markdown())
    print((OUT_DIR / "AI在网络安全中的应用研究.pdf").resolve())
