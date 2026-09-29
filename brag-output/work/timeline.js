// 120 BPM: one beat = 0.5s, one bar = 2s. Times match audio.py.
const BEAT = .5;
// [id, start, end, entry] entry: 'wipe' or 'cut'
const SCENES = [['s1',0,6,'cut'],['s2',6,12,'wipe'],['s2b',12,16,'cut'],['s3',16,20,'cut'],['s4',20,26,'wipe'],['s5',26,30,'wipe'],['s6',30,34,'wipe'],['s7',34,40.01,'cut']];
const WIPE = .32;
const DROPS = [16, 34];
const kickOn = t => (t >= 0 && t < 12) || (t >= 16 && t < 38);
const kickEnv = t => kickOn(t) ? Math.exp(-(t % BEAT) / .12) : 0;

function rise(el, u, a, d=.35, dy=30){
  const p = eout(prog(u,a,a+d));
  el.style.opacity = p; el.style.transform = `translateY(${(1-p)*dy}px)`;
}
function pop(el, u, a, d=.4, extra=''){
  const p = prog(u,a,a+d), s = back(p);
  el.style.opacity = eout(clamp(p*2.2));
  el.style.transform = `translateY(${(1-s)*-26}px) scale(${lerp(.9,1,s)}) ${extra}`;
}
function ring(el, u, a, d=.5){
  const p = prog(u,a,a+d);
  el.style.opacity = p > 0 && p < 1 ? .9*(1-p) : 0;
  el.style.transform = `scale(${lerp(.6,2.6,eout(p))})`;
}
function burst(t){
  const svg = document.getElementById('burst');
  let html = '';
  for (const [t0, col] of [[16,'#fff'],[18.5,'#F2B544'],[34,'#F2B544']]) {
    const p = prog(t, t0, t0+.65);
    if (p <= 0 || p >= 1) continue;
    const e = eout(p), r0 = lerp(90, 760, e), r1 = lerp(150, 980, Math.min(1, e*1.15));
    for (let k = 0; k < 18; k++) {
      const a = k/18*Math.PI*2 + t0;
      html += `<line x1="${960+Math.cos(a)*r0}" y1="${540+Math.sin(a)*r0}" x2="${960+Math.cos(a)*r1}" y2="${540+Math.sin(a)*r1}" stroke="${col}" stroke-width="${lerp(10,2,p)}" stroke-linecap="round" opacity="${1-p}"/>`;
    }
  }
  svg.innerHTML = html;
}

function render(t){
  SCENES.forEach(([id,a,b,entry], i) => {
    const el = document.getElementById(id);
    const next = SCENES[i+1];
    const tail = next && next[3] === 'wipe' ? WIPE : 0;
    const on = t >= a && t < b + tail;
    el.style.visibility = on ? 'visible' : 'hidden';
    el.style.zIndex = i;
    if (entry === 'wipe') {
      const p = eio(prog(t, a, a+WIPE));
      el.style.clipPath = p >= 1 ? 'none' : `inset(0 0 0 ${(1-p)*100}%)`;
    }
    if (on) {
      // every scene breathes with the kick
      el.style.transform = `scale(${1 + .007*kickEnv(t)})`;
      SC[id](t - a, t);
    }
  });
  const k = kickEnv(t), full = (t >= 16 && t < 32) || (t >= 34 && t < 38);
  document.getElementById('pulse').style.opacity = k * (full ? 1 : .55);
  const f = Math.max(...DROPS.map(d => t >= d ? .9*Math.exp(-(t-d)/.13) : 0));
  document.getElementById('flash').style.opacity = f;
  burst(t);
}

const SC = {
  s1(u){
    const c = $('#clock'), p = eout(prog(u,0,.3));
    c.style.opacity = p; c.style.transformOrigin = '0 70%';
    c.style.transform = `scale(${lerp(1.15,1,p) + .02*kickEnv(u)})`;
    $('#colon').style.opacity = (Math.floor(u/BEAT)%2) ? .15 : 1;
    rise($('#clockSub'), u, .5);
    $$('#s1 .note').forEach((n,k) => { pop(n, u, 1 + k); ring(n.querySelector('.ring'), u, 1 + k); });
  },
  s2(u){
    rise($('#s2 .cap'), u, .25); rise($('#s2 .sub'), u, .75);
    $$('#s2 li').forEach((li,k) => {
      const a = .5 + k*BEAT, p = prog(u, a, a+.35);
      li.style.opacity = eout(clamp(p*2)); li.style.transform = `translateX(${(1-back(p))*60}px) scale(${lerp(.94,1,back(p))})`;
    });
    // overload stutter on beat 4.0
    const sp = prog(u, 4.0, 4.6), amp = Math.sin(sp*Math.PI) * 12;
    $('#s2 .list').style.transform = `translateX(${Math.sin(u*70)*amp}px) rotate(${Math.sin(u*55)*amp*.1}deg)`;
  },
  s2b(u, t){
    rise($('#l1'), u, 0, .4, 24); rise($('#l2'), u, 1.5, .4, 24);
    // build: text tightens as the roll speeds up, then blackout before the drop
    const b = prog(u, 2.0, 3.75);
    const jit = b*b*3;
    $('#s2b > div').style.transform = `scale(${1 + b*.06}) translate(${Math.sin(u*90)*jit}px,${Math.cos(u*77)*jit}px)`;
    $('#s2b > div').style.opacity = 1 - prog(u, 3.72, 3.8);
  },
  s3(u){
    $('#pine').style.transform = `scale(${1.1 - .06*prog(u,0,4) + .015*kickEnv(u)})`;
    const w = $('#bigWord'), wp = eout(prog(u,0,.25));
    w.style.opacity = clamp(wp*3); w.style.transform = `translate(-50%,-50%) scale(${lerp(1.4,1,wp) + .03*kickEnv(u)})`;
    const bin = eio(prog(u,1.0,1.3)), bout = eio(prog(u,2.0,2.25)), b = bin - bout;
    $('.band.top').style.transform = `translateY(${(b-1)*101}%)`;
    $('.band.bottom').style.transform = `translateY(${(1-b)*101}%)`;
    const off = u * 110;
    $('.band.top .track').style.transform = `translateX(${-1400 + off}px)`;
    $('.band.bottom .track').style.transform = `translateX(${-200 - off}px)`;
    $('#fill').style.opacity = eio(prog(u,2.0,2.25));
    const l = $('#lockup'), lp = prog(u,2.5,2.9), ls = back(lp);
    l.style.opacity = eout(clamp(lp*2.2));
    l.style.transform = `translate(-50%,-50%) scale(${lerp(.8,1,ls) + .012*kickEnv(u)})`;
  },
  s4(u){
    rise($('#s4 .cap'), u, .25); rise($('#s4 .sub'), u, .75);
    $$('#s4 li').forEach((li,k) => {
      const a = .5 + k*BEAT, p = prog(u, a, a+.35);
      li.style.opacity = eout(clamp(p*2)); li.style.transform = `translateX(${(1-back(p))*60}px)`;
      const tk = 3 + k*BEAT, q = prog(u, tk, tk+.2);
      const box = li.querySelector('.box'), tg = li.querySelector('.tag'), sv = box.querySelector('svg');
      box.style.background = q > 0 ? `rgba(6,84,66,${q})` : 'transparent';
      sv.style.opacity = q; sv.style.transform = `scale(${lerp(.3,1,back(q))})`;
      tg.style.opacity = q; tg.style.transform = `scale(${lerp(.6,1,back(prog(u,tk,tk+.3)))})`;
      ring(box.querySelector('.ring'), u, tk, .45);
      li.style.boxShadow = q > 0 ? `0 0 0 ${3*Math.sin(prog(u,tk,tk+.3)*Math.PI)}px var(--green)` : 'none';
    });
  },
  s5(u){
    rise($('#s5 .cap'), u, .25); rise($('#s5 .sub'), u, 1.0);
    const bill = $('#s5 .bill'), bp = prog(u,.5,.9);
    bill.style.opacity = eout(clamp(bp*1.8)); bill.style.transform = `translateY(${(1-back(bp))*50}px)`;
    const steps = Math.max(0, Math.min(6, Math.floor((u - 1.75)/.25) + 1));
    const n = 6 - steps, z = $('#zero'); z.textContent = n;
    const last = 1.75 + (steps-1)*.25, zp = steps > 0 ? prog(u, last, last + .2) : 1;
    const big = n === 0 ? Math.sin(prog(u,3.0,3.35)*Math.PI)*.6 : 0;
    z.style.transform = `scale(${1 + Math.sin(zp*Math.PI)*.25 + big})`;
    z.style.color = n === 0 ? 'var(--green)' : 'var(--ink)';
    const row = $('#s5 .row.total');
    row.style.background = n === 0 ? `rgba(6,84,66,${.1*(1-prog(u,3.3,3.9))+.04})` : 'transparent';
  },
  s6(u){
    rise($('#s6 h2'), u, .25); rise($('#s6 .lede'), u, .5);
    const A = $('#qA'), B = $('#qB');
    const aIn = eout(prog(u,.5,.8)), aOut = eio(prog(u,1.9,2.1));
    A.style.opacity = aIn * (1-aOut); A.style.transform = `translateX(${(1-aIn)*40 - aOut*60}px)`;
    const bIn = eout(prog(u,2.0,2.3));
    B.style.opacity = bIn; B.style.transform = `translateX(${(1-bIn)*60}px)`;
    const oA = $('#oA'), oB = $('#oB');
    oA.classList.toggle('on', u >= 1.5); oA.style.setProperty('--dot', back(prog(u,1.5,1.7)));
    oB.classList.toggle('on', u >= 3.0); oB.style.setProperty('--dot', back(prog(u,3.0,3.2)));
    oA.style.transform = `scale(${1 + .03*Math.sin(prog(u,1.5,1.75)*Math.PI)})`;
    oB.style.transform = `scale(${1 + .03*Math.sin(prog(u,3.0,3.25)*Math.PI)})`;
    const ra = oA.getBoundingClientRect(), rb = oB.getBoundingClientRect();
    const bdx = (1-bIn)*60;
    const pA = [ra.left + 42, ra.top + ra.height*.6], pB = [rb.left - bdx + 42, rb.top + rb.height*.6];
    const p0 = [1760, 1000];
    let x, y;
    if (u < 1.6) { const k = eio(prog(u,.6,1.4)); x = lerp(p0[0],pA[0],k); y = lerp(p0[1],pA[1],k); }
    else if (u < 3.0) { const k = eio(prog(u,2.3,2.9)); x = lerp(pA[0],pB[0],k); y = lerp(pA[1],pB[1],k); }
    else { x = pB[0]; y = pB[1]; }
    const press = Math.max(Math.sin(prog(u,1.42,1.58)*Math.PI), Math.sin(prog(u,2.92,3.08)*Math.PI));
    const c = $('#cursor'); c.style.opacity = eout(prog(u,.55,.7));
    c.style.transform = `translate(${x-8}px,${y-6}px) scale(${1 - press*.15})`;
    const r = $('#ripple');
    const second = u >= 2.5, rp = second ? prog(u,3.0,3.4) : prog(u,1.5,1.9), rc = second ? pB : pA;
    r.style.opacity = rp > 0 && rp < 1 ? (1-rp)*.9 : 0;
    r.style.transform = `translate(${rc[0]-45}px,${rc[1]-45}px) scale(${lerp(.3,1.4,eout(rp))})`;
  },
  s7(u, t){
    const m = $('#endMark'), mp = prog(u,0,.35);
    m.style.opacity = eout(clamp(mp*3));
    m.style.transform = `scale(${lerp(.4,1,back(mp)) + .05*kickEnv(t)})`;
    rise($('#endCap'), u, .5, .4, 34); rise($('#endSub'), u, 1.0);
    const b = $('#endBtn'), bp = prog(u,1.5,1.85);
    const press = Math.sin(prog(u,3.0,3.2)*Math.PI);
    b.style.opacity = eout(clamp(bp*1.8));
    b.style.transform = `translateY(${(1-back(bp))*30}px) scale(${1 - press*.07 + .015*kickEnv(t)})`;
    const g1 = prog(u,3.05,3.6), g2 = prog(u,4.0,4.8);
    const glow = Math.max((1-g1)*(g1>0), (1-g2)*(g2>0));
    b.style.boxShadow = `0 0 0 ${Math.max(eout(g1)*(g1<1), eout(g2)*(g2<1))*30}px rgba(242,181,68,${.5*glow})`;
    rise($('#foot'), u, 2.0, .4, 12);
  }
};
