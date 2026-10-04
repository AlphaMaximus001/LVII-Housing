import { createRequire } from 'module'; import { execSync } from 'child_process';
const require = createRequire(import.meta.url);
const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY, bypass: '<-loopback>' } : undefined;
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
const fs = await import('fs');
const css = fs.readFileSync('/home/user/LVII-Housing/brag-output/work/fonts/fonts.css','utf8').replace(/url\((?!http)/g, 'url(http://127.0.0.1:8357/brag-output/work/fonts/');
await p.route(/fonts\.googleapis\.com/, r => r.fulfill({ contentType: 'text/css', body: css }));
await p.route(/fonts\.gstatic\.com/, r => r.abort());
await p.goto('http://127.0.0.1:8357/');
const t0 = Date.now();
for (const ms of [400, 1300, 2200, 3200, 4300, 5300, 6300]) {
  await p.waitForTimeout(ms - (Date.now() - t0));
  await p.screenshot({ path: `shots/intro-${ms}.jpg`, type: 'jpeg', quality: 85 });
}
await p.waitForTimeout(1500);
console.log('fonts', await p.evaluate(() => [document.fonts.check('700 40px Tinos'), document.fonts.check('400 20px Onest')]));
await p.screenshot({ path: 'shots/hero.jpg', type: 'jpeg', quality: 85 });
await p.screenshot({ path: 'shots/header.png', clip: { x: 0, y: 0, width: 520, height: 70 } });
await p.evaluate(() => { const b = document.getElementById('playBig'); if (b && !document.getElementById('poster').hidden) b.click(); });
for (let i = 0; i < 26; i++) { await p.waitForTimeout(2000); await p.locator('#stage').screenshot({ path: `shots/story-${String(i).padStart(2,'0')}.jpg`, type: 'jpeg', quality: 85 }); }
await p.locator('#survey').scrollIntoViewIfNeeded(); await p.waitForTimeout(800);
await p.screenshot({ path: 'shots/survey.jpg', type: 'jpeg', quality: 85 });
await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight)); await p.waitForTimeout(800);
await p.screenshot({ path: 'shots/footer.jpg', type: 'jpeg', quality: 85 });
const fb = await p.locator('footer').boundingBox(); await p.screenshot({ path: 'shots/footer.png', clip: { x: 0, y: fb.y, width: 600, height: fb.height } });
await b.close();
