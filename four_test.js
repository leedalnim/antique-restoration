const {chromium}=require('playwright');const sleep=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:560,height:760,deviceScaleFactor:2}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
const clean=t=>p.evaluate(t=>{const a=window.__getActive();if(a)for(let v=.006;v<1;v+=.01)for(let u=.006;u<1;u+=.01)a.brush(u,v,20,t);},t);
await p.goto(process.argv[2],{waitUntil:'load'});await sleep(8000);
for(const id of ['naut','lion']){
  await p.evaluate(i=>{window.__unlock(i);window.__startGame(i);},id);await sleep(2500);
  await p.screenshot({path:'f_'+id+'_dirty.png'});
  await clean('swab');await sleep(1200);await p.screenshot({path:'f_'+id+'_clean.png'});
}
console.log('errors:',errs.slice(0,6).join(' | ')||'none');await b.close();})();
