const { chromium } = require('playwright');
(async () => {
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto(process.argv[2],{waitUntil:'load'}); await p.waitForTimeout(6500);
  await p.click('.mode[data-mode="clean"]'); await p.waitForTimeout(200);
  // 문지르는 중 캡처(마우스 누른 채)
  await p.mouse.move(300,260); await p.mouse.down();
  for(let i=0;i<8;i++){ await p.mouse.move(300+Math.sin(i)*18,260+i*8); await p.waitForTimeout(20); }
  await p.mouse.move(305,330); // 방금 움직여 pulse 높음
  await p.waitForTimeout(30);
  await p.screenshot({path: process.argv[3]||'brush_scrub.png'});
  await p.mouse.up();
  console.log('errors:', errs.slice(0,5).join(' | ')||'none');
  await b.close();
})();
