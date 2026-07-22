const { chromium } = require('playwright');
(async () => {
  const url = process.argv[2];
  const out = process.argv[3] || 'game_scrub.png';
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage({ viewport: { width: 600, height: 800, deviceScaleFactor: 2 } });
  const msgs=[]; page.on('pageerror',e=>msgs.push('[pageerror] '+e.message));
  await page.goto(url,{waitUntil:'load'});
  await page.waitForTimeout(6000);
  // 청소 모드로 전환
  await page.click('.mode[data-mode="clean"]');
  await page.waitForTimeout(400);
  // 불상 위를 지그재그로 문지름 (여러 스와이프)
  // 불상 몸통 위에만(빈 공간 회피) — 얼굴/가슴/무릎/대좌를 촘촘히 문지름
  const swipes = [
    [[300,200],[300,250],[300,310],[300,360]],   // 가슴~배 세로
    [[295,185],[290,210],[300,230]],             // 얼굴
    [[255,420],[300,428],[355,432]],             // 무릎 가로
    [[330,380],[345,420],[350,460]],             // 종아리
    [[275,500],[310,520],[345,530]],             // 대좌 앞
    [[300,270],[270,300],[330,300],[300,330]],   // 가슴 문지르기
    [[300,360],[300,410],[300,300],[300,230]],   // 몸통 왕복
    [[250,430],[360,435],[250,445],[360,450]],   // 무릎 왕복
  ];
  for (const path of swipes) {
    await page.mouse.move(path[0][0], path[0][1]);
    await page.mouse.down();
    for (let i=1;i<path.length;i++){
      // 중간 보간 이동
      const [ax,ay]=path[i-1], [bx,by]=path[i];
      for(let t=1;t<=6;t++){ await page.mouse.move(ax+(bx-ax)*t/6, ay+(by-ay)*t/6); await page.waitForTimeout(12); }
    }
    await page.mouse.up();
    await page.waitForTimeout(120);
  }
  await page.mouse.move(50,720); // 빈 곳으로 이동 → 도구 커서 숨김
  await page.waitForTimeout(700);
  const pct = await page.evaluate(()=>document.querySelector('#pct')?.textContent);
  await page.screenshot({ path: out });
  console.log('progress after scrub:', pct);
  console.log(msgs.slice(-10).join('\n'));
  await browser.close();
})();
