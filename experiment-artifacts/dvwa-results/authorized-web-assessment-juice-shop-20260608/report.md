# Authorized Web Assessment Report

## Summary

- Target: `http://127.0.0.1:3000/`
- Scope origin: `http://127.0.0.1:3000`
- Mode: `passive`
- Started: `2026-06-08T15:04:10+08:00`
- Finished: `2026-06-08T15:04:43+08:00`
- Elapsed: `32.743s`
- Pages crawled: `10`
- Forms found: `0`
- ZAP alerts: `39`

This run is a low-risk authorized assessment. It performs same-origin crawling, browser screenshots, request/form inventory, security-header review, and optional ZAP spider/passive alert collection. It does not run destructive payloads, web shells, password spraying, or ZAP active scan.

## Scope And Authorization

- The operator supplied `--authorized` for this local or explicitly authorized target.
- Requests were constrained to the target origin.
- Active exploitation and destructive tests were not performed by this helper.

## HTTP Baseline

- Final URL: `http://127.0.0.1:3000/`
- Status: `200`
- Server: `None`
- Content-Type: `text/html; charset=UTF-8`
- Missing security headers: `content-security-policy, referrer-policy, permissions-policy, strict-transport-security`

Security headers observed:

- `content-security-policy`: `missing`
- `x-frame-options`: `SAMEORIGIN`
- `x-content-type-options`: `nosniff`
- `referrer-policy`: `missing`
- `permissions-policy`: `missing`
- `strict-transport-security`: `missing`

## Crawled Pages

### OWASP Juice Shop

- URL: `http://127.0.0.1:3000/#/`
- Status: `200`
- Links discovered: `14`
- Forms discovered: `0`

![OWASP Juice Shop](screenshots/crawl/01-root.png)

### favicon_js.ico (48×48)

- URL: `http://127.0.0.1:3000/assets/public/favicon_js.ico`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![favicon_js.ico (48×48)](screenshots/crawl/02-assets-public-favicon_js.ico.png)

### http://127.0.0.1:3000/chunk-6RWMKLEX.js

- URL: `http://127.0.0.1:3000/chunk-6RWMKLEX.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/03-chunk-6RWMKLEX.js.png)

### http://127.0.0.1:3000/chunk-7U6P4YGV.js

- URL: `http://127.0.0.1:3000/chunk-7U6P4YGV.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/04-chunk-7U6P4YGV.js.png)

### http://127.0.0.1:3000/chunk-B3RFAYKZ.js

- URL: `http://127.0.0.1:3000/chunk-B3RFAYKZ.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/05-chunk-B3RFAYKZ.js.png)

### http://127.0.0.1:3000/chunk-EMJTEAHL.js

- URL: `http://127.0.0.1:3000/chunk-EMJTEAHL.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/06-chunk-EMJTEAHL.js.png)

### http://127.0.0.1:3000/chunk-KD3CNUZG.js

- URL: `http://127.0.0.1:3000/chunk-KD3CNUZG.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/07-chunk-KD3CNUZG.js.png)

### http://127.0.0.1:3000/chunk-KI34UYIE.js

- URL: `http://127.0.0.1:3000/chunk-KI34UYIE.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/08-chunk-KI34UYIE.js.png)

### http://127.0.0.1:3000/chunk-PX7UKXVL.js

- URL: `http://127.0.0.1:3000/chunk-PX7UKXVL.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/09-chunk-PX7UKXVL.js.png)

### http://127.0.0.1:3000/chunk-R7LX7FKI.js

- URL: `http://127.0.0.1:3000/chunk-R7LX7FKI.js`
- Status: `200`
- Links discovered: `0`
- Forms discovered: `0`

![page screenshot](screenshots/crawl/10-chunk-R7LX7FKI.js.png)


## Forms And Inputs

- No HTML forms were discovered during the bounded crawl.

## Scripts And API Surface Hints

- `http://127.0.0.1:3000/main.js`
- `http://127.0.0.1:3000/polyfills.js`
- `http://127.0.0.1:3000/scripts.js`

## ZAP Spider And Passive Alerts

- ZAP version: `2.17.0`
- Spider status: `100`
- Alerts by risk: `{"Medium": 21, "Informational": 3, "Low": 15}`

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-PX7UKXVL.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Content Security Policy (CSP) Header Not Set

- Risk: `Medium`
- Confidence: `High`
- URL: `http://127.0.0.1:3000/sitemap.xml`
- Evidence: ``
- Description: Content Security Policy (CSP) is an added layer of security that helps to detect and mitigate certain types of attacks, including Cross Site Scripting (XSS) and data injection attacks. These attacks are used for everything from data theft to site defacement or distribution of malware. CSP provides a set of standard HTTP headers that allow website owners to declare approved sources of content that browsers should be allowed to load on that page — covered types are JavaScript, CSS, HTML frames, fo

### Content Security Policy (CSP) Header Not Set

- Risk: `Medium`
- Confidence: `High`
- URL: `http://127.0.0.1:3000/`
- Evidence: ``
- Description: Content Security Policy (CSP) is an added layer of security that helps to detect and mitigate certain types of attacks, including Cross Site Scripting (XSS) and data injection attacks. These attacks are used for everything from data theft to site defacement or distribution of malware. CSP provides a set of standard HTTP headers that allow website owners to declare approved sources of content that browsers should be allowed to load on that page — covered types are JavaScript, CSS, HTML frames, fo

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-EMJTEAHL.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/assets/public/favicon_js.ico`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-B3RFAYKZ.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-Y3BEW76R.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/polyfills.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-KI34UYIE.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-UNFVUBM2.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-R7LX7FKI.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/scripts.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/robots.txt`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-KD3CNUZG.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-7U6P4YGV.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/styles.css`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/chunk-6RWMKLEX.js`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/sitemap.xml`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Cross-Domain Misconfiguration

- Risk: `Medium`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/`
- Evidence: `Access-Control-Allow-Origin: *`
- Description: Web browser data loading may be possible, due to a Cross Origin Resource Sharing (CORS) misconfiguration on the web server.

### Modern Web Application

- Risk: `Informational`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/`
- Evidence: `<script>
    window.addEventListener("load", function(){
      window.cookieconsent.initialise({
        "palette": {
          "popup": { "background": "var(--theme-primary)", "text": "var(--them`
- Description: The application appears to be a modern web application. If you need to explore it automatically then the Ajax Spider may well be more effective than the standard one.

### Modern Web Application

- Risk: `Informational`
- Confidence: `Medium`
- URL: `http://127.0.0.1:3000/sitemap.xml`
- Evidence: `<script>
    window.addEventListener("load", function(){
      window.cookieconsent.initialise({
        "palette": {
          "popup": { "background": "var(--theme-primary)", "text": "var(--them`
- Description: The application appears to be a modern web application. If you need to explore it automatically then the Ajax Spider may well be more effective than the standard one.

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/sitemap.xml`
- Evidence: `1666666667`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/`
- Evidence: `1666666667`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/sitemap.xml`
- Evidence: `1839622642`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/`
- Evidence: `1839622642`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/styles.css`
- Evidence: `1528301887`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/styles.css`
- Evidence: `1578947368`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/styles.css`
- Evidence: `1602209945`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/styles.css`
- Evidence: `1636363636`
- Description: A timestamp was disclosed by the application/web server. - Unix

### Timestamp Disclosure - Unix

- Risk: `Low`
- Confidence: `Low`
- URL: `http://127.0.0.1:3000/styles.css`
- Evidence: `1818181818`
- Description: A timestamp was disclosed by the application/web server. - Unix

## Findings Triage

- `Confirmed`: none from this helper alone; confirmation requires targeted reproduction.
- `Likely/Possible`: ZAP passive alerts and missing headers should be reviewed and verified.
- `Informational`: crawl inventory, forms, scripts, and screenshots.

## Recommended Next Steps

1. Review the form/API inventory and choose specific vulnerability hypotheses.
2. Confirm each ZAP passive alert manually or with a targeted harness.
3. Enable safe active tests only after explicit authorization and rate limits are set.
4. Add authenticated browser state if the application has login-only functionality.

## Artifacts

- `report.md`: this report
- `report.json`: machine-readable data
- `screenshots/crawl/`: browser screenshots

## Limitations

- This helper is not a full penetration test by itself.
- It does not bypass authentication, solve CAPTCHA/MFA, or infer business-logic vulnerabilities.
- It does not run ZAP active scan, password attacks, destructive file upload tests, command execution, or persistence.
- Single-page applications may require deeper scripted navigation for complete coverage.
