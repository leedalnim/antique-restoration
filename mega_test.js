const { chromium } = require('playwright');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  const clean=async(tool)=>p.evaluate((tool)=>{const a=window.__getActive&&window.__getActive();if(a){for(let v=0.006;v<1;v+=0.01)for(let u=0.006;u<1;u+=0.01)a.brush(u,v,20,tool);}},tool);
  await p.goto(process.argv[2],{waitUntil:'load'}); await sleep(7000);
  await p.click('#startBtn'); await sleep(700);
  await p.screenshot({path:'m_hub1.png'});           // bapga 대기, amita 잠김
  // bapga 복원
  await p.evaluate(()=>window.__startGame('bapga')); await sleep(900);
  await clean('swab'); await sleep(1300);
  await p.screenshot({path:'m_bapga_fin.png'});
  await p.click('#finHome'); await sleep(700);
  await p.screenshot({path:'m_hub2.png'});           // bapga 완료, amita 해금
  // amita 복원
  await p.evaluate(()=>window.__startGame('amita')); await sleep(2500);
  await p.screenshot({path:'m_amita_dirty.png'});
  await clean('swab'); await sleep(1300);
  await p.screenshot({path:'m_amita_fin.png'});
  console.log('unlocked:', JSON.stringify(await p.evaluate(()=>window.__unlocked())), '| errors:', errs.slice(0,6).join(' | ')||'none');
  await b.close();
})();
