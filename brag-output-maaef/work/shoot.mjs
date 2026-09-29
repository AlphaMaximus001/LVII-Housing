import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url);
const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const b = await chromium.launch({ args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required'] });
const p = await b.newPage({ viewport:{width:1920,height:1080} });
await p.goto('http://localhost:3100/', { waitUntil:'networkidle' });
for (const t of [500,1500,3000,5000,8000]) { await p.waitForTimeout(t - (globalThis.last||0)); globalThis.last=t; await p.screenshot({path:`shots/home-intro-${t}.jpg`,quality:85,type:'jpeg'}); }
// scroll through intro + page
for (let i=0;i<14;i++){ await p.mouse.wheel(0,900); await p.waitForTimeout(900); await p.screenshot({path:`shots/home-scroll-${String(i).padStart(2,'0')}.jpg`,quality:85,type:'jpeg'}); }
for (const r of ['services','work','expertise','about','writingspace','contact']) {
  await p.goto('http://localhost:3100/'+r, { waitUntil:'networkidle' }); await p.waitForTimeout(2500);
  await p.screenshot({path:`shots/${r}.jpg`,quality:85,type:'jpeg'});
  await p.mouse.wheel(0,1100); await p.waitForTimeout(1200); await p.screenshot({path:`shots/${r}-2.jpg`,quality:85,type:'jpeg'});
}
await b.close();
