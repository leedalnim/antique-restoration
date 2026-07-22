const { chromium } = require('playwright');
(async()=>{
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
  await p.goto(process.argv[2],{waitUntil:'load'}); await p.waitForTimeout(6500);
  await p.click('.mode[data-mode="clean"]'); await p.waitForTimeout(200);
  await p.mouse.move(300,260); await p.mouse.down();
  const samples=[];
  for(let i=0;i<6;i++){
    await p.mouse.move(300+Math.sin(i)*20,260+i*10); await p.waitForTimeout(40);
    const rx=await p.evaluate(()=>{const bb=window.__bristle&&window.__bristle();return bb?+bb.rotation.x.toFixed(3):null;});
    samples.push(rx);
  }
  await p.mouse.up();
  console.log('bristle rotation.x samples during scrub:', JSON.stringify(samples));
  await b.close();
})();
