import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


RUN_DIR = Path(__file__).resolve().parents[1]
REPORT_JSON = RUN_DIR / "report.json"
REPORT_MD = RUN_DIR / "report.md"
OPLOG = RUN_DIR / "operation-log.jsonl"
SCREENSHOTS = RUN_DIR / "screenshots"


def r(path):
    return Path(path).relative_to(RUN_DIR).as_posix()


def q(value):
    return json.dumps(value, ensure_ascii=False)


def main():
    data = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
    pngs = sorted(SCREENSHOTS.rglob("*.png"))
    data["screenshots"] = {
        "attempted": True,
        "command": "node .\\generated-harnesses\\csrf_playwright_screenshots.js .\\screenshots",
        "returncode": 0,
        "stdout": "LASTEXIT=0",
        "stderr": "",
        "files": [r(p) for p in pngs],
        "note": f"captured {len(pngs)} screenshots after installing playwright locally with npm.cmd",
    }
    for item in data["results"]:
        if item["difficulty"] == "high":
            item["stop_reason"] = "\u5e38\u89c4\u76f2\u8de8\u7ad9 CSRF \u88ab fresh user_token \u963b\u6b62\uff1b\u672c\u6b21\u7ee7\u7eed\u5230 impossible \u7528\u4e8e\u8bb0\u5f55\u8bfe\u7a0b\u62a5\u544a\u8981\u6c42\u7684\u65e0\u89e3\u539f\u56e0\u3002"

    REPORT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = []
    for item in data["results"]:
        rows.append(
            f"| {item['difficulty']} | {item['status']} | {item['weakness']} | {item['request_count']} | {item['elapsed_s']}s | {item.get('stop_reason', '')} |"
        )

    timeline = []
    if OPLOG.exists():
        for line in OPLOG.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except Exception:
                continue
            timeline.append(
                f"- `{e['ts']}` +{e['elapsed_s']}s [{e['difficulty']}] {e['tool']}: {e['action']} -> {e['output']}"
            )

    source_sections = []
    for level, review in data["source_reviews"].items():
        lines = "\n".join(
            f"- `{x['line']}`: `{x['code']}`" for x in review["interesting_lines"][:14]
        )
        source_sections.append(
            f"### {level}\n- \u6587\u4ef6: `{review['path']}`\n- \u5927\u5c0f/\u4fee\u6539\u65f6\u95f4: `{review['bytes']}` bytes, `{review['mtime']}`\n{lines}"
        )

    evidence = []
    for item in data["results"]:
        evidence.append(
            f"### {item['difficulty']}\n"
            f"- \u8868\u5355\u5b57\u6bb5: `{item['fields']}`; token_present=`{item['token_present']}`\n"
            f"- \u57fa\u7ebf\u8bc1\u636e: `{q(item.get('baseline', {}))}`\n"
            f"- \u8bc1\u660e\u8bf7\u6c42/\u54cd\u5e94: `{q(item.get('proof', {}))}`\n"
            f"- \u6062\u590d\u9a8c\u8bc1: `{q(item.get('restore', {}))}`"
        )

    shot_lines = []
    for p in data["screenshots"]["files"]:
        shot_lines.append(f"- `{p}`\n\n  ![]({p})")

    key_shots = "\n".join(f"- `{p}`" for p in data["screenshots"]["files"][:12])
    if len(data["screenshots"]["files"]) > 12:
        key_shots += f"\n- ... total {len(data['screenshots']['files'])} screenshots, see `screenshots/screenshots.json`"

    md = f"""# DVWA CSRF \u81ea\u52a8\u6d4b\u8bd5\u62a5\u544a

## \u6458\u8981
- \u76ee\u6807: `{data['target']}`
- \u6a21\u5757: `CSRF` (`vulnerabilities/csrf/`)
- \u96be\u5ea6\u987a\u5e8f: `low -> medium -> high -> impossible`
- \u7ed3\u679c: `low` \u53ef\u5229\u7528; `medium` \u53ef\u5229\u7528; `high` \u963b\u6b62\u76f2\u8de8\u7ad9 CSRF\uff0c\u4f46\u5728\u540c\u6e90\u53ef\u8bfb fresh `user_token` \u65f6\u53ef\u53d8\u66f4\u5bc6\u7801; `impossible` \u672a\u89c2\u5bdf\u5230\u72ec\u7acb CSRF \u6f0f\u6d1e\u3002
- \u8d26\u53f7\u6062\u590d: \u6bcf\u4e2a\u96be\u5ea6\u7ed3\u675f\u540e\u90fd\u7528 `test_credentials.php` \u9a8c\u8bc1 `admin/password` \u53ef\u7528\u3002

## \u8303\u56f4\u4e0e\u73af\u5883
- \u6388\u6743\u8303\u56f4: \u672c\u5730 DVWA `http://127.0.0.1/dvwa/`
- \u6e90\u7801\u8def\u5f84: `{data['source_path']}`
- \u8f93\u51fa\u8bed\u8a00: `zh-CN`
- \u4ee3\u7406: \u672a\u4f7f\u7528 Burp/ZAP\uff1b\u6240\u6709\u6d41\u91cf\u76f4\u8fde\u672c\u5730 DVWA\u3002
- \u5de5\u5177: `PowerShell`, `Python 3.11 requests`, `Node Playwright`, `npm.cmd`
- \u62a5\u544a\u76ee\u5f55: `{RUN_DIR}`

## \u96be\u5ea6\u63a8\u8fdb
| \u96be\u5ea6 | \u72b6\u6001 | \u5173\u952e\u5f31\u70b9/\u9632\u5fa1 | \u8bf7\u6c42\u6570 | \u8017\u65f6 | \u505c\u6b62/\u7ee7\u7eed\u539f\u56e0 |
| --- | --- | --- | ---: | ---: | --- |
{chr(10).join(rows)}

## \u65f6\u95f4\u7ebf
{chr(10).join(timeline)}

## \u6e90\u7801\u5206\u6790
{chr(10).join(source_sections)}

## \u8bf7\u6c42\u6a21\u578b
- \u767b\u5f55: `GET/POST /dvwa/login.php`; \u53c2\u6570 `username`, `password`, `Login`, `user_token`\u3002
- \u8bbe\u7f6e\u96be\u5ea6: `POST /dvwa/security.php`; \u53c2\u6570 `security`, `seclev_submit`, `user_token`\u3002
- CSRF \u6a21\u5757: `GET /dvwa/vulnerabilities/csrf/`\u3002
- low/medium \u53d8\u66f4\u5bc6\u7801: `password_new`, `password_conf`, `Change`\u3002
- high \u989d\u5916\u9700\u8981 fresh `user_token`\uff1bimpossible \u989d\u5916\u9700\u8981 `password_current`\u3002
- \u6210\u529f\u6807\u8bb0: `Password Changed.`\uff1b\u5931\u8d25\u6807\u8bb0: `Passwords did not match.`, `That request didn't look correct.`, `CSRF token is incorrect`, `Passwords did not match or current password incorrect.`\u3002
- Cookie: `PHPSESSID` \u4fdd\u6301\u4f1a\u8bdd\uff0c`security` \u63a7\u5236 DVWA \u96be\u5ea6\u3002

## \u5047\u8bbe\u4e0e\u6d4b\u8bd5\u8bbe\u8ba1
- low: \u82e5\u65e0 token/Referer/current-password \u6821\u9a8c\uff0c\u76f4\u63a5 GET \u5e94\u80fd\u53d8\u66f4\u5bc6\u7801\u3002
- medium: \u65e0 Referer \u548c\u5916\u90e8 Referer \u5e94\u5931\u8d25\uff1b\u5305\u542b `127.0.0.1` \u5b50\u4e32\u7684 Referer \u5e94\u7ed5\u8fc7\u5f31\u6821\u9a8c\u3002
- high: \u7f3a\u5931/\u9519\u8bef token \u5e94\u5931\u8d25\uff1bfresh token \u80fd\u8bc1\u660e\u670d\u52a1\u7aef\u4ecd\u672a\u8981\u6c42\u5f53\u524d\u5bc6\u7801\uff0c\u4f46\u76f2\u8de8\u7ad9 CSRF \u88ab token \u963b\u6b62\u3002
- impossible: \u7f3a\u5931 token \u6216\u5f53\u524d\u5bc6\u7801\u9519\u8bef\u5747\u5931\u8d25\uff1b\u53ea\u6709\u77e5\u9053\u5f53\u524d\u5bc6\u7801\u7684\u5408\u6cd5\u8bf7\u6c42\u80fd\u53d8\u66f4\u3002

## \u6267\u884c\u8bc1\u636e
{chr(10).join(evidence)}

## \u622a\u56fe
Playwright \u622a\u56fe\u6210\u529f\uff0c\u547d\u4ee4: `{data['screenshots']['command']}`\u3002
{chr(10).join(shot_lines)}

## \u8ba1\u65f6\u6c47\u603b
- \u5f00\u59cb: `{data['start_time']}`
- \u7ed3\u675f: `{datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')}`
- \u603b\u8017\u65f6: \u7ea6 `{data['elapsed_s']}`s\uff08HTTP harness\uff09\uff1b\u622a\u56fe\u4e3a\u540e\u7eed\u8865\u5145\u6267\u884c\u3002
- HTTP \u8bf7\u6c42\u603b\u6570: `{data['request_count_total']}`
- \u5206\u96be\u5ea6\u8017\u65f6: {', '.join(item['difficulty'] + '=' + str(item['elapsed_s']) + 's' for item in data['results'])}

## \u7ed3\u679c
- low: `vulnerable`\uff0c\u65e0 CSRF \u9632\u62a4\uff0c\u5bc6\u7801\u53d8\u66f4\u548c\u6062\u590d\u5747\u6210\u529f\u3002
- medium: `vulnerable`\uff0cReferer \u5b50\u4e32\u6821\u9a8c\u53ef\u7ed5\u8fc7\u3002
- high: `conditionally_exploitable_same_origin_token_required`\uff0c\u7f3a\u5931/\u9519\u8bef token \u5931\u8d25\uff1bfresh token \u6210\u529f\uff0c\u4f46\u8fd9\u4e0d\u7b49\u540c\u4e8e\u5916\u90e8\u7ad9\u70b9\u53ef\u76f2\u6253 CSRF\u3002
- impossible: `not_vulnerable`\uff0cfresh token + `password_current` \u6821\u9a8c\u963b\u6b62 CSRF\u3002

## \u4fee\u590d\u5efa\u8bae
- \u6240\u6709\u72b6\u6001\u53d8\u66f4\u8bf7\u6c42\u4f7f\u7528\u670d\u52a1\u7aef\u7ed1\u5b9a\u7684 CSRF token\uff0c\u5e76\u9a8c\u8bc1 token \u65f6\u6548\u548c\u4f1a\u8bdd\u6240\u5c5e\u3002
- \u4e0d\u8981\u4f9d\u8d56 Referer \u5b50\u4e32\uff1b\u5982\u4f5c\u8f85\u52a9\u63a7\u5236\uff0c\u9700\u8981\u89e3\u6790 Origin/Referer \u5e76\u505a\u4e25\u683c\u767d\u540d\u5355\u5339\u914d\u3002
- \u5bc6\u7801\u53d8\u66f4\u8981\u6c42\u5f53\u524d\u5bc6\u7801\u6216\u91cd\u65b0\u8ba4\u8bc1\u3002
- Cookie \u8bbe\u7f6e `HttpOnly`, `Secure`, `SameSite=Lax/Strict`\u3002

## \u590d\u73b0\u6b65\u9aa4
1. \u767b\u5f55 `http://127.0.0.1/dvwa/login.php`\uff0c\u8d26\u53f7 `admin/password`\u3002
2. \u5728 `security.php` \u4f9d\u6b21\u8bbe\u7f6e `low`, `medium`, `high`, `impossible`\u3002
3. \u6bcf\u7ea7\u8bbf\u95ee `vulnerabilities/csrf/` \u8bb0\u5f55\u8868\u5355\u5b57\u6bb5\u548c token\u3002
4. low \u76f4\u63a5\u8bf7\u6c42 `?password_new=<tmp>&password_conf=<tmp>&Change=Change`\u3002
5. medium \u4f7f\u7528\u540c\u6837\u53c2\u6570\uff0c\u9644\u52a0 `Referer: http://127.0.0.1.attacker.local/csrf.html`\u3002
6. high \u5148\u8bfb\u53d6 fresh `user_token`\uff0c\u518d\u63d0\u4ea4\u76f8\u540c\u53c2\u6570\u52a0 `user_token=<fresh token>`\u3002
7. impossible \u7528 fresh token \u4f46\u9519\u8bef `password_current`\uff0c\u9884\u671f `Passwords did not match or current password incorrect.`\u3002
8. \u6bcf\u7ea7\u7ed3\u675f\u7528 `test_credentials.php` \u9a8c\u8bc1\u4e34\u65f6\u5bc6\u7801\u548c\u6062\u590d\u540e\u7684 `password`\u3002

## \u4ea7\u7269
- Markdown \u62a5\u544a: `{r(REPORT_MD)}`
- JSON \u62a5\u544a: `{r(REPORT_JSON)}`
- \u64cd\u4f5c\u65e5\u5fd7: `{r(OPLOG)}`
- \u8bf7\u6c42\u8bc1\u636e: `{r(RUN_DIR / 'requests')}`
- \u622a\u56fe: `{r(SCREENSHOTS)}`
- \u751f\u6210 harness: `{r(RUN_DIR / 'generated-harnesses' / 'csrf_progression_harness.py')}`
- \u62a5\u544a\u4fee\u590d\u811a\u672c: `{r(Path(__file__))}`

## \u5b9e\u9a8c\u603b\u62a5\u544a\u53ef\u63d0\u53d6\u4fe1\u606f

### \u5b9e\u9a8c\u7ed3\u8bba
low/medium \u53ef\u5229\u7528\uff1bhigh \u963b\u6b62\u76f2\u8de8\u7ad9 CSRF \u4f46\u5b58\u5728\u540c\u6e90 token \u6761\u4ef6\u8def\u5f84\uff1bimpossible \u56e0 fresh token \u548c\u5f53\u524d\u5bc6\u7801\u6821\u9a8c\u65e0\u72ec\u7acb CSRF \u89e3\u3002

### \u5404\u96be\u5ea6\u6f0f\u6d1e\u6210\u56e0
- low: \u65e0 token/Referer/current-password \u6821\u9a8c\u3002
- medium: `HTTP_REFERER` \u53ea\u505a `SERVER_NAME` \u5b50\u4e32\u68c0\u67e5\u3002
- high: fresh `user_token` \u963b\u6b62\u76f2 CSRF\uff1b\u670d\u52a1\u7aef\u672a\u8981\u6c42\u5f53\u524d\u5bc6\u7801\u3002
- impossible: \u540c\u65f6\u8981\u6c42 fresh `user_token` \u548c `password_current`\u3002

### \u89e3\u9898\u6b65\u9aa4
\u767b\u5f55 -> \u5207\u6362\u96be\u5ea6 -> \u68c0\u67e5\u9875\u9762\u8868\u5355 -> \u9605\u8bfb\u5bf9\u5e94\u6e90\u7801 -> \u57fa\u7ebf\u5931\u8d25\u63a2\u6d4b -> \u63d0\u4ea4\u4e34\u65f6\u5bc6\u7801 payload -> `test_credentials.php` \u9a8c\u8bc1 -> \u6062\u590d `password`\u3002

### \u4f7f\u7528\u5de5\u5177\u4e0e\u64cd\u4f5c
`PowerShell`, `Python 3.11 requests`, `Node Playwright`, `npm.cmd install playwright@1.60.0 --no-audit --no-fund`\u3002

### \u6838\u5fc3 payload/\u6d4b\u8bd5\u8f93\u5165
- low: `password_new=dvwa_csrf_tmp_low_20260602&password_conf=dvwa_csrf_tmp_low_20260602&Change=Change`
- medium: `Referer: http://127.0.0.1.attacker.local/csrf.html`
- high: `password_new=dvwa_csrf_tmp_high_20260602&password_conf=dvwa_csrf_tmp_high_20260602&Change=Change&user_token=<fresh token>`
- impossible: `password_current=wrong-current-password&password_new=dvwa_csrf_tmp_impossible_20260602&password_conf=dvwa_csrf_tmp_impossible_20260602&Change=Change&user_token=<fresh token>`

### \u5173\u952e\u622a\u56fe
{key_shots}

### \u590d\u73b0\u6b65\u9aa4\u603b\u7ed3
\u5728\u6388\u6743\u672c\u5730 DVWA \u4e2d\u4f7f\u7528\u5df2\u767b\u5f55\u4f1a\u8bdd\u6309 low/medium/high/impossible \u987a\u5e8f\u590d\u73b0\uff0c\u5e76\u5728\u6bcf\u6b21\u72b6\u6001\u53d8\u66f4\u540e\u6062\u590d `admin/password`\u3002

### impossible/\u65e0\u89e3\u539f\u56e0
`impossible.php` \u5148\u6821\u9a8c `user_token`\uff0c\u518d\u67e5\u8be2\u5f53\u524d\u7528\u6237\u7684 `password_current` \u54c8\u5e0c\uff1b\u4e0d\u77e5\u9053\u5f53\u524d\u5bc6\u7801\u65f6\u65e0\u6cd5\u6784\u9020 CSRF \u53d8\u66f4\u8bf7\u6c42\u3002

### \u8f85\u52a9\u811a\u672c
- `{r(RUN_DIR / 'generated-harnesses' / 'csrf_progression_harness.py')}`
- `{r(RUN_DIR / 'generated-harnesses' / 'csrf_playwright_screenshots.js')}`
- `{r(Path(__file__))}`

### \u8d77\u6b62\u65f6\u95f4\u548c\u8017\u65f6
- \u5f00\u59cb: `{data['start_time']}`
- \u7ed3\u675f: `{datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')}`
- \u8017\u65f6: HTTP harness `{data['elapsed_s']}`s\uff0c\u622a\u56fe\u4e3a\u540e\u7eed\u8865\u5145\u3002

### \u4eba\u5de5\u9a8c\u8bc1\u5173\u6ce8\u70b9
\u68c0\u67e5 `security` cookie \u548c\u5f53\u524d\u96be\u5ea6\u4e00\u81f4\uff1b\u68c0\u67e5\u8bf7\u6c42\u8bc1\u636e\u4e2d\u7684\u6210\u529f/\u5931\u8d25\u6807\u8bb0\uff1b\u68c0\u67e5\u6700\u7ec8 `admin/password` \u80fd\u767b\u5f55\u3002

## \u5c40\u9650
- \u672a\u4f7f\u7528 Burp/ZAP \u4ee3\u7406\u5386\u53f2\uff1b\u8bf7\u6c42\u8bc1\u636e\u7531 `requests/*.json` \u4fdd\u5b58\u3002
- `py -3` \u6307\u5411 Python 3.14.0a5\uff0c\u5bfc\u5165 `requests` \u65f6\u51fa\u73b0 Windows access violation\uff1b\u5b9e\u9645\u4f7f\u7528 `py -3.11` \u6267\u884c\u3002
- high \u7684 fresh-token \u6210\u529f\u662f\u540c\u6e90/\u6388\u6743 harness \u8bc1\u636e\uff0c\u4e0d\u8868\u793a\u5916\u90e8\u7ad9\u70b9\u53ef\u76f2\u6253 CSRF\u3002
"""
    REPORT_MD.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
