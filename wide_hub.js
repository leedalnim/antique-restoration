const {chromium}=require('playwright');const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1600,height:900,deviceScaleFactor:1}});
await p.goto(process.argv[2],{waitUntil:'load'});await sleep(7000);
await p.click('#startBtn');await sleep(700);await p.screenshot({path:'wide_hub.png'});
await b.close();})();
