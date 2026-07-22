const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto(process.argv[2],{waitUntil:'load'}); await p.waitForTimeout(6500);
  await p.screenshot({path:'intro_1.png'});
  const btnText=await p.evaluate(()=>document.querySelector('#startBtn')?.textContent);
  await p.click('#startBtn'); await p.waitForTimeout(1200);
  await p.screenshot({path:'intro_2.png'});
  console.log('start button:', btnText, '| errors:', errs.slice(0,4).join(' | ')||'none');
  await b.close();
})();
