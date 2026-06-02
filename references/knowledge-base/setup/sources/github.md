# DVWA Setup And Usage - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `搭建/使用`
- Lines: `44-71`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `setup.php / login.php / security.php`
- GitHub section selector: `搭建/使用`
- Knowledge-base directory: `setup`

## Source Section Outline

- Line 44: `## 搭建/使用`

## Complete Process Notes

## Detailed Walkthrough Process

### Lab preparation

1. Start the local Windows web stack that hosts DVWA, for example phpStudy, XAMPP, WAMP, Docker Desktop, or a local VM.
2. Open the DVWA base URL in a browser and confirm `login.php` loads.
3. If DVWA has not been initialized, open `setup.php` and create/reset the database.
4. Log in with the user-provided account. Common public-lab defaults are `admin` / `password`, but never assume them when the user supplies different credentials.
5. Open `security.php`, set the requested difficulty, submit, and verify the selected level is reflected in the page/session.
6. For automated testing, keep the same base URL, cookies, `PHPSESSID`, and `security` cookie in one session.

### Source-code orientation

1. Locate the DVWA root, commonly under `D:\xampp\htdocs\DVWA`, `D:\phpstudy_pro\WWW\DVWA`, or a cloned `DVWA` repository.
2. Each module normally has a route under `vulnerabilities/<module>/` and source variants under `vulnerabilities/<module>/source/<level>.php`.
3. Read the matching source level before building payloads. Use it to understand validation and tokens, but still verify behavior through HTTP requests.

### Reporting baseline

Record target URL, login account name, selected difficulty, module route, source path, date, tool commands, proxy settings, and screenshots/images used as supporting evidence.

## Local Images

![GitHub WalkThrough setup 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa1.png

![GitHub WalkThrough setup 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa2.png

![GitHub WalkThrough setup 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa3.png

![GitHub WalkThrough setup 4](./images/github-04.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa4.png
