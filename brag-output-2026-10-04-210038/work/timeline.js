// 100 BPM: one beat = 0.6s, half-beat = 0.3s. Times match audio.py.
const BEAT = .6, HALF = .3;
// [id, start, end, entry]
const SCENES = [['s1',0,4.2,'cut'],['s2',4.2,8.4,'wipe'],['s2b',8.4,12,'cut'],['s3',12,15.6,'fade'],['s4',15.6,19.8,'wipe'],['s5',19.8,23.4,'wipe'],['s6',23.4,26.4,'wipe'],['s7',26.4,30.01,'wipe']];
const WIPE = .4, FADE = .35;
const kickOn = t => (t >= 0 && t < 8.4) || (t >= 12 && t < 28.8);
// soft, slow breath on the beat instead of a hard kick bounce
const kickEnv = t => kickOn(t) ? Math.exp(-(t % BEAT) / .22) : 0;
const smooth = t => t*t*(3-2*t);

function rise(el, u, a, d=.45, dy=22){
  const p = eout(prog(u,a,a+d));
  el.style.opacity = p; el.style.transform = `translateY(${(1-p)*dy}px)`;
}
// gentle pop: small settle, no overshoot spikes
function pop(el, u, a, d=.45){
  const p = eout(prog(u,a,a+d));
  el.style.opacity = p;
  el.style.transform = `translateY(${(1-p)*16}px) scale(${lerp(.97,1,p)})`;
}

function render(t){
  SCENES.forEach(([id,a,b,entry], i) => {
    const el = document.getElementById(id);
    const next = SCENES[i+1];
    const tail = next ? (next[3] === 'wipe' ? WIPE : next[3] === 'fade' ? FADE : 0) : 0;
    const on = t >= a && t < b + tail;
    el.style.visibility = on ? 'visible' : 'hidden';
    el.style.zIndex = i;
    el.style.clipPath = 'none'; el.style.opacity = 1;
    if (entry === 'wipe') {
      const p = eio(prog(t, a, a+WIPE));
      el.style.clipPath = p >= 1 ? 'none' : `inset(0 0 0 ${(1-p)*100}%)`;
    } else if (entry === 'fade') {
      el.style.opacity = smooth(prog(t, a, a+FADE));
    }
    if (on) {
      el.style.transform = `scale(${1 + .0025*kickEnv(t)})`;
      SC[id](t - a, t);
    }
  });
  // warm lamp glow that breathes with the groove
  document.getElementById('pulse').style.opacity = .35 * kickEnv(t) * ((t >= 12 && t < 28.8) ? 1 : .6);
  document.getElementById('flash').style.opacity = 0;
  document.getElementById('burst').innerHTML = '';
}

const SC = {
  s1(u){
    const c = $('#clock'), p = eout(prog(u,0,.5));
    c.style.opacity = p; c.style.transformOrigin = '0 70%';
    c.style.transform = `scale(${lerp(1.05,1,p)})`;
    $('#colon').style.opacity = (Math.floor(u/BEAT)%2) ? .3 : 1;
    rise($('#clockSub'), u, .3);
    $$('#s1 .note').forEach((n,k) => pop(n, u, BEAT*(k+1)));
    $$('#s1 .ring').forEach(r => r.style.opacity = 0);
  },
  s2(u){
    rise($('#s2 .cap'), u, .15); rise($('#s2 .sub'), u, .5);
    $$('#s2 li').forEach((li,k) => {
      const a = .45 + k*HALF, p = eout(prog(u, a, a+.4));
      li.style.opacity = p; li.style.transform = `translateX(${(1-p)*36}px)`;
    });
    // a slow lean as the list gets heavy, no shaking
    const lean = smooth(prog(u, 2.1, 3.0));
    $('#s2 .list').style.transform = `rotate(${lean*1.2}deg) translateY(${lean*6}px)`;
  },
  s2b(u){
    rise($('#l1'), u, .1, .5, 18); rise($('#l2'), u, 1.2, .5, 18);
    const box = $('#s2b > div:last-child');
    box.style.transform = `scale(${1 + .02*prog(u, 0, 3.6)})`;
    box.style.opacity = 1 - smooth(prog(u, 3.3, 3.6));
    // the lamp comes on as the problem lands, warming into the reveal
    const g = $('#glowS'), gp = smooth(prog(u, 2.2, 3.6));
    g.style.opacity = gp; g.style.transform = `scale(${lerp(.7,1.15,gp)})`;
  },
  s3(u){
    $('#pine').style.transform = `scale(${1.08 - .05*prog(u,0,3.6)})`;
    const w = $('#bigWord'), wp = eout(prog(u,.05,.6));
    w.style.opacity = wp; w.style.transform = `translate(-50%,-50%) scale(${lerp(1.04,1,wp)})`;
    const bin = eio(prog(u,.55,.9)), bout = eio(prog(u,1.35,1.65)), b = bin - bout;
    $('.band.top').style.transform = `translateY(${(b-1)*101}%)`;
    $('.band.bottom').style.transform = `translateY(${(1-b)*101}%)`;
    const off = u * 80;
    $('.band.top .track').style.transform = `translateX(${-1400 + off}px)`;
    $('.band.bottom .track').style.transform = `translateX(${-200 - off}px)`;
    // green wash, then it fades to white while the mark settles at centre (as on the site)
    const fin = eio(prog(u,1.35,1.65)), fout = smooth(prog(u,1.85,2.5));
    $('#fill').style.opacity = fin * (1 - fout);
    $('#paper').style.opacity = u >= 1.65 ? 1 : 0;
    const e = $('#introEnd'), mp = eio(prog(u,1.75,2.5));
    e.style.opacity = clamp((u-1.7)/.15);
    e.querySelector('svg').style.transform = `scale(${lerp(2.2,1,mp)})`;
    const iw = e.querySelector('.iw'), ip = eout(prog(u,2.35,2.8));
    iw.style.opacity = ip; iw.style.transform = `translateY(${(1-ip)*10}px)`;
    e.style.transform = `translate(-50%,-50%)`;
  },
  s4(u){
    rise($('#s4 .cap'), u, .15); rise($('#s4 .sub'), u, .5);
    $$('#s4 li').forEach((li,k) => {
      const a = .3 + k*HALF, p = eout(prog(u, a, a+.4));
      li.style.opacity = p; li.style.transform = `translateX(${(1-p)*36}px)`;
      const tk = 1.8 + k*HALF, q = smooth(prog(u, tk, tk+.25));
      const box = li.querySelector('.box'), tg = li.querySelector('.tag'), sv = box.querySelector('svg');
      box.style.background = q > 0 ? `rgba(6,84,66,${q})` : 'transparent';
      sv.style.opacity = q; sv.style.transform = `scale(${lerp(.6,1,q)})`;
      tg.style.opacity = q; tg.style.transform = `translateX(${(1-q)*-8}px)`;
      const r = box.querySelector('.ring'); if (r) r.style.opacity = 0;
      li.style.boxShadow = 'none';
    });
  },
  s5(u){
    rise($('#s5 .cap'), u, .15); rise($('#s5 .sub'), u, .6);
    const bill = $('#s5 .bill'), bp = eout(prog(u,.3,.8));
    bill.style.opacity = bp; bill.style.transform = `translateY(${(1-bp)*30}px)`;
    const steps = Math.max(0, Math.min(6, Math.floor((u - 1.2)/.15) + 1));
    const n = 6 - steps, z = $('#zero'); z.textContent = n;
    const glow = n === 0 ? Math.sin(prog(u,2.1,2.7)*Math.PI) : 0;
    z.style.transform = `scale(${1 + .15*glow})`;
    z.style.color = n === 0 ? 'var(--green)' : 'var(--ink)';
    const row = $('#s5 .row.total');
    row.style.background = n === 0 ? `rgba(6,84,66,${.06 + .06*glow})` : 'transparent';
  },
  s6(u){
    rise($('#s6 h2'), u, .15); rise($('#s6 .lede'), u, .3);
    const A = $('#qA'), B = $('#qB');
    const aIn = eout(prog(u,.3,.6)), aOut = eio(prog(u,1.4,1.6));
    A.style.opacity = aIn * (1-aOut); A.style.transform = `translateX(${(1-aIn)*30 - aOut*50}px)`;
    const bIn = eout(prog(u,1.5,1.8));
    B.style.opacity = bIn; B.style.transform = `translateX(${(1-bIn)*50}px)`;
    const oA = $('#oA'), oB = $('#oB');
    oA.classList.toggle('on', u >= 1.2); oA.style.setProperty('--dot', eout(prog(u,1.2,1.35)));
    oB.classList.toggle('on', u >= 2.4); oB.style.setProperty('--dot', eout(prog(u,2.4,2.55)));
    oA.style.transform = oB.style.transform = 'none';
    const ra = oA.getBoundingClientRect(), rb = oB.getBoundingClientRect();
    const bdx = (1-bIn)*50;
    const pA = [ra.left + 42, ra.top + ra.height*.6], pB = [rb.left - bdx + 42, rb.top + rb.height*.6];
    const p0 = [1760, 1000];
    let x, y;
    if (u < 1.3) { const k = eio(prog(u,.4,1.1)); x = lerp(p0[0],pA[0],k); y = lerp(p0[1],pA[1],k); }
    else if (u < 2.4) { const k = eio(prog(u,1.8,2.3)); x = lerp(pA[0],pB[0],k); y = lerp(pA[1],pB[1],k); }
    else { x = pB[0]; y = pB[1]; }
    const press = Math.max(Math.sin(prog(u,1.12,1.28)*Math.PI), Math.sin(prog(u,2.32,2.48)*Math.PI));
    const c = $('#cursor'); c.style.opacity = eout(prog(u,.35,.5));
    c.style.transform = `translate(${x-8}px,${y-6}px) scale(${1 - press*.1})`;
    const r = $('#ripple');
    const second = u >= 1.9, rp = second ? prog(u,2.4,2.8) : prog(u,1.2,1.6), rc = second ? pB : pA;
    r.style.opacity = rp > 0 && rp < 1 ? (1-rp)*.5 : 0;
    r.style.transform = `translate(${rc[0]-45}px,${rc[1]-45}px) scale(${lerp(.4,1.1,eout(rp))})`;
  },
  s7(u, t){
    const m = $('#endMark'), mp = eout(prog(u,.1,.6));
    m.style.opacity = mp; m.style.transform = `scale(${lerp(.85,1,mp)})`;
    rise($('#endCap'), u, .3, .5, 26); rise($('#endSub'), u, .6);
    const b = $('#endBtn'), bp = eout(prog(u,.9,1.35));
    const press = Math.sin(prog(u,2.4,2.6)*Math.PI);
    b.style.opacity = bp;
    b.style.transform = `translateY(${(1-bp)*20}px) scale(${1 - press*.04})`;
    const g = prog(u,2.45,3.1);
    b.style.boxShadow = g > 0 && g < 1 ? `0 0 0 ${eout(g)*20}px rgba(242,181,68,${.35*(1-g)})` : 'none';
    rise($('#foot'), u, 1.2, .5, 10);
  }
};
