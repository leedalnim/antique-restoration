const {chromium}=require('playwright');const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
await p.goto(process.argv[2],{waitUntil:'load'});await sleep(7000);
await p.evaluate(()=>window.__startGame('bapga'));await sleep(1500);
await p.evaluate(()=>{const a=window.__getActive();a.reset();
  // 세척솔: 넓은 밴드(위), 면봉: 가는 밴드(아래) — rPx 비율=실제 wr 비율(0.145:0.032≈4.5x)
  for(let u=0.18;u<=0.82;u+=0.01) a.brush(u,0.33,42,'brush');
  for(let u=0.18;u<=0.82;u+=0.01) a.brush(u,0.62,9,'swab');
});
await sleep(1200);await p.screenshot({path:'demo_tools.png'});
await b.close();})();
