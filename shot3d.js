const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const file = process.argv[2] || 'test_glb.html';
  const out  = process.argv[3] || 'shot3d.png';
  const waitMs = parseInt(process.argv[4] || '3500', 10);
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader',
           '--ignore-gpu-blocklist','--enable-webgl'],
  });
  const page = await browser.newPage({ viewport: { width: 600, height: 800, deviceScaleFactor: 2 } });
  const msgs=[];
  page.on('console',m=>msgs.push(`[${m.type()}] ${m.text()}`));
  page.on('pageerror',e=>msgs.push(`[pageerror] ${e.message}`));
  const url = file.startsWith('http') ? file : 'file://'+path.resolve(file);
  await page.goto(url,{waitUntil:'load'});
  await page.waitForTimeout(waitMs);
  const info = await page.evaluate(()=>({ready:window.__ready,err:window.__err,title:document.title}));
  await page.screenshot({ path: out });
  console.log('ready=',info.ready,'err=',info.err,'title=',info.title);
  console.log(msgs.slice(-15).join('\n'));
  await browser.close();
})();
