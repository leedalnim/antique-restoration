const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto(process.argv[2],{waitUntil:'load'}); await p.waitForTimeout(6500);
  await p.screenshot({path:'flow_1_intro.png'});
  await p.click('#startBtn'); await p.waitForTimeout(800);
  await p.screenshot({path:'flow_2_hub.png'});
  await p.click('.acard:not(.locked)'); await p.waitForTimeout(800);
  await p.screenshot({path:'flow_3_game.png'});
  // 전체 세척(면봉)으로 100%
  await p.evaluate(()=>{ const a=window.__getActive&&window.__getActive(); if(a){ for(let v=0.006;v<1;v+=0.01)for(let u=0.006;u<1;u+=0.01) a.brush(u,v,20,'swab'); } });
  await p.waitForTimeout(1400);
  await p.screenshot({path:'flow_4_finish.png'});
  await p.click('#finHome'); await p.waitForTimeout(700);
  await p.screenshot({path:'flow_5_hubdone.png'});
  await p.click('#toCodex'); await p.waitForTimeout(600);
  await p.screenshot({path:'flow_6_codex.png'});
  const pct=await p.evaluate(()=>document.querySelector('#pct')?.textContent);
  console.log('final pct at finish:', pct, '| errors:', errs.slice(0,5).join(' | ')||'none');
  await b.close();
})();
