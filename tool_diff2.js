const { chromium } = require('playwright');
(async () => {
  const url=process.argv[2];
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  for(const tool of ['blow','brush','swab']){
    const p=await b.newPage({viewport:{width:520,height:720,deviceScaleFactor:2}});
    await p.goto(url,{waitUntil:'load'}); await p.waitForTimeout(6500);
    const res=await p.evaluate((tool)=>{
      const a=window.__getActive&&window.__getActive(); if(!a)return {err:'no active'};
      for(let v=0.006;v<1;v+=0.01)for(let u=0.006;u<1;u+=0.01) a.brush(u,v,20,tool);
      a.remain=a.sample();
      return {pct:Math.round((1-a.remain/a.initRemain)*100), remain:+a.remain.toFixed(3), init:+a.initRemain.toFixed(3)};
    }, tool);
    await p.waitForTimeout(500);
    await p.screenshot({path:'diff_'+tool+'.png'});
    console.log(tool.padEnd(6), JSON.stringify(res));
    await p.close();
  }
  await b.close();
})();
