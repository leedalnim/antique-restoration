const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const file = process.argv[2] || 'antique-restoration.html';
  const out  = process.argv[3] || 'shot.png';
  const waitMs = parseInt(process.argv[4] || '4500', 10);
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', `--proxy-server=${process.env.HTTPS_PROXY}`, '--ignore-certificate-errors'],
  });
  const page = await browser.newPage({ viewport: { width: 430, height: 850, deviceScaleFactor: 2 } });
  const msgs = [];
  page.on('console', m => msgs.push(`[${m.type()}] ${m.text()}`));
  page.on('pageerror', e => msgs.push(`[pageerror] ${e.message}`));
  await page.goto('file://' + path.resolve(file), { waitUntil: 'load' });
  await page.waitForTimeout(waitMs);
  await page.screenshot({ path: out });
  console.log('--- console ---');
  console.log(msgs.slice(-40).join('\n'));
  await browser.close();
})();
