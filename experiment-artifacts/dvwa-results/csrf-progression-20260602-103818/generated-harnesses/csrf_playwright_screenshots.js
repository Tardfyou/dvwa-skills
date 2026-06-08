
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const base = 'http://127.0.0.1/dvwa/';
const outDir = process.argv[2];
const manifest = [];

async function shot(page, difficulty, name) {
  const dir = path.join(outDir, difficulty);
  fs.mkdirSync(dir, { recursive: true });
  const file = path.join(dir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  manifest.push({ difficulty, name, path: file });
}

async function token(page) {
  return await page.locator('input[name="user_token"]').last().inputValue().catch(() => null);
}

async function login(page) {
  await page.goto(base + 'login.php');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'password');
  await page.click('input[name="Login"]');
  await page.waitForLoadState('networkidle');
}

async function setSecurity(page, level) {
  await page.goto(base + 'security.php');
  await page.selectOption('select[name="security"]', level);
  await page.click('input[name="seclev_submit"]');
  await page.waitForLoadState('networkidle');
  await shot(page, level, 'security-set');
}

async function testCredential(page, difficulty, password, name) {
  await page.goto(base + 'vulnerabilities/csrf/test_credentials.php');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', password);
  await page.click('input[name="Login"]');
  await page.waitForLoadState('networkidle');
  await shot(page, difficulty, name);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  await login(page);

  await setSecurity(page, 'low');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'low', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_low_a&password_conf=shot_low_b&Change=Change');
  await shot(page, 'low', 'baseline-mismatch');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_low_tmp_20260602&password_conf=shot_low_tmp_20260602&Change=Change');
  await shot(page, 'low', 'proof-password-changed');
  await testCredential(page, 'low', 'shot_low_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change');

  await setSecurity(page, 'medium');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'medium', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_medium_a&password_conf=shot_medium_b&Change=Change');
  await shot(page, 'medium', 'baseline-no-referer');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_medium_tmp_20260602&password_conf=shot_medium_tmp_20260602&Change=Change', { referer: 'http://127.0.0.1.attacker.local/csrf.html' });
  await shot(page, 'medium', 'proof-weak-referer');
  await testCredential(page, 'medium', 'shot_medium_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change', { referer: 'http://127.0.0.1.attacker.local/csrf.html' });

  await setSecurity(page, 'high');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'high', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_new=shot_high_tmp_20260602&password_conf=shot_high_tmp_20260602&Change=Change');
  await shot(page, 'high', 'baseline-missing-token');
  await page.goto(base + 'vulnerabilities/csrf/');
  let t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_new=shot_high_tmp_20260602&password_conf=shot_high_tmp_20260602&Change=Change&user_token=${t}`);
  await shot(page, 'high', 'token-aware-change');
  await testCredential(page, 'high', 'shot_high_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_new=password&password_conf=password&Change=Change&user_token=${t}`);

  await setSecurity(page, 'impossible');
  await page.goto(base + 'vulnerabilities/csrf/');
  await shot(page, 'impossible', 'module-page');
  await page.goto(base + 'vulnerabilities/csrf/?password_current=password&password_new=shot_impossible_tmp_20260602&password_conf=shot_impossible_tmp_20260602&Change=Change');
  await shot(page, 'impossible', 'baseline-missing-token');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_current=wrong-current-password&password_new=shot_impossible_tmp_20260602&password_conf=shot_impossible_tmp_20260602&Change=Change&user_token=${t}`);
  await shot(page, 'impossible', 'wrong-current-password');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_current=password&password_new=shot_impossible_tmp_20260602&password_conf=shot_impossible_tmp_20260602&Change=Change&user_token=${t}`);
  await shot(page, 'impossible', 'legitimate-change-with-current-password');
  await testCredential(page, 'impossible', 'shot_impossible_tmp_20260602', 'verify-temp-password');
  await page.goto(base + 'vulnerabilities/csrf/');
  t = await token(page);
  await page.goto(base + `vulnerabilities/csrf/?password_current=shot_impossible_tmp_20260602&password_new=password&password_conf=password&Change=Change&user_token=${t}`);
  await testCredential(page, 'impossible', 'password', 'verify-restored-password');

  await browser.close();
  fs.writeFileSync(path.join(outDir, 'screenshots.json'), JSON.stringify(manifest, null, 2), 'utf8');
}

main().catch(err => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
