# File Upload - GitHub WalkThrough

## Source

https://github.com/ffffffff0x/1earn/blob/master/1earn/Security/RedTeam/Web%E5%AE%89%E5%85%A8/%E9%9D%B6%E5%9C%BA/DVWA-WalkThrough.md

## Local Source Location

- File: `D:\WorkSpace\综合实践5\1earn\1earn\Security\RedTeam\Web安全\靶场\DVWA-WalkThrough.md`
- Section: `File_Upload`
- Lines: `1215-1571`

## How This Source Is Used

- Treat this file as local working notes derived from the public guide source.
- The process below is a complete local paraphrase/checklist for solving the DVWA lab module.
- Use the source link for attribution and to inspect exact third-party wording when needed.
- Do not assume the final answer blindly; observe the live DVWA page, source code, and responses first.

## Module Mapping

- DVWA route: `vulnerabilities/upload/`
- GitHub section selector: `File_Upload`
- Knowledge-base directory: `file-upload`

## Source Section Outline

- Line 1215: `## File_Upload`
- Line 1251: `### Low`
- Line 1311: `### Medium`
- Line 1394: `### High`
- Line 1484: `### Impossible`

## Complete Process Notes

## Detailed Walkthrough Process

### Low

1. Open `vulnerabilities/upload/` and upload a benign text/image file to learn the destination path.
2. Check whether the server exposes the uploaded file under `hackable/uploads/`.
3. Upload a minimal PHP proof file in the lab and request it directly.
4. Confirm execution with a harmless output marker, not destructive commands.
5. Report upload path, execution path, filename handling, and absence of extension/MIME validation.

### Medium

1. Observe browser-side and server-side MIME/extension checks.
2. Test content type tampering through Burp/ZAP while keeping the filename controlled.
3. Try image extensions containing PHP content only to prove validation weakness in the lab.
4. Report whether MIME type, extension, or content was trusted.

### High

1. Expect image validation or extension allowlisting.
2. Try a valid image container with controlled metadata or extension tricks only if the lab source indicates that path.
3. Verify whether uploaded content is reprocessed, renamed, or stored safely.
4. Report which validation layer blocked or allowed execution.

### Impossible

1. Confirm the server validates type, size, extension, and image content and renames/reprocesses files.
2. Upload invalid and valid files to prove enforcement.
3. Report that execution is blocked and why.

## Local Images

![GitHub WalkThrough file-upload 1](./images/github-01.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa24.png

![GitHub WalkThrough file-upload 2](./images/github-02.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa25.png

![GitHub WalkThrough file-upload 3](./images/github-03.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa26.png

![GitHub WalkThrough file-upload 4](./images/github-04.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa27.png

![GitHub WalkThrough file-upload 5](./images/github-05.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa28.png

![GitHub WalkThrough file-upload 6](./images/github-06.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa29.png

![GitHub WalkThrough file-upload 7](./images/github-07.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa30.png

![GitHub WalkThrough file-upload 8](./images/github-08.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa31.png

![GitHub WalkThrough file-upload 9](./images/github-09.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa32.png

![GitHub WalkThrough file-upload 10](./images/github-10.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa33.png

![GitHub WalkThrough file-upload 11](./images/github-11.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa34.png

![GitHub WalkThrough file-upload 12](./images/github-12.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa35.png

![GitHub WalkThrough file-upload 13](./images/github-13.png)

Original: D:\WorkSpace\综合实践5\1earn\assets\img\Security\RedTeam\Web安全\靶场\dvwa\dvwa36.png
