import { createRequire } from 'module';
import { execSync } from 'child_process';
const require = createRequire(import.meta.url);
const { chromium } = require(execSync('npm root -g').toString().trim() + '/playwright');
const [,, mode, arg] = process.argv; // mode: stills "t1,t2" | frames
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto('file://' + process.cwd() + '/composition.html');
await p.evaluate(() => window.ready);
await p.evaluate(() => new Promise(r => setTimeout(r, 300)));
if (mode === 'stills') {
  for (const t of arg.split(',')) {
    await p.evaluate(t => render(t), +t);
    await p.screenshot({ path: `stills/t${t}.jpg`, quality: 85, type: 'jpeg' });
  }
} else {
  const FPS = 30, N = 900;
  for (let i = 0; i < N; i++) {
    await p.evaluate(t => render(t), i / FPS);
    await p.screenshot({ path: `frames/${String(i).padStart(4,'0')}.jpg`, quality: 95, type: 'jpeg' });
  }
}
await b.close();
