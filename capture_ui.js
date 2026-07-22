const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  const p = await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
  await p.goto(process.argv[2],{waitUntil:'load'}); await p.waitForTimeout(6000);
  await p.click('.mode[data-mode="clean"]'); await p.waitForTimeout(300);
  await p.click('#toolBtn'); await p.waitForTimeout(400);
  await p.screenshot({path: process.argv[3]||'ui_tools.png'});
  await b.close();
})();
