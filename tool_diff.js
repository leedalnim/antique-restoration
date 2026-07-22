const { chromium } = require('playwright');
(async () => {
  const url=process.argv[2], toolSel=process.argv[3], out=process.argv[4];
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:600,height:800,deviceScaleFactor:2}});
  await p.goto(url,{waitUntil:'load'}); await p.waitForTimeout(6500);
  await p.click('.mode[data-mode="clean"]'); await p.waitForTimeout(200);
  // 도구 선택
  await p.click('#toolBtn'); await p.waitForTimeout(200);
  await p.click('.tool[data-tool="'+toolSel+'"]'); await p.waitForTimeout(200);
  // 몸 전체를 촘촘히 문지름(빈 곳 회피, 몸통·무릎·대좌·얼굴)
  const cols=[240,270,300,330,360], rows=[180,230,280,330,390,430,470,520,560];
  for(const cx of cols){
    await p.mouse.move(cx,rows[0]); await p.mouse.down();
    for(const ry of rows){ for(let t=0;t<4;t++){await p.mouse.move(cx+(Math.random()*10-5),ry+t*3);await p.waitForTimeout(6);} }
    await p.mouse.up(); await p.waitForTimeout(30);
  }
  await p.mouse.move(50,730); await p.waitForTimeout(600);
  const pct=await p.evaluate(()=>document.querySelector('#pct')?.textContent);
  await p.screenshot({path:out});
  console.log(toolSel,'-> progress',pct);
  await b.close();
})();
