# Funky soundtrack for the Maaef four-wings video: 120 BPM, D Dorian vamp (Dm7 | G9).
# 16th = 0.125s, beat = 0.5s, bar = 2s. Times match composition.html.
import numpy as np, wave
from scipy.signal import butter, sosfilt

SR = 44100; DUR = 75.0; N = int(SR * DUR)
S16 = .125; BEAT = .5; BAR = 2.0
rng = np.random.default_rng(9)
L = np.zeros(N); R = np.zeros(N); PL = np.zeros(N); PR = np.zeros(N)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def T(n): return np.arange(n) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def add(sig, t0, g=1.0, pan=0.0, pump=False):
    i = int(round(t0 * SR))
    if i >= N or i < 0: return
    j = min(N, i + len(sig)); s = sig[:j - i] * g
    l, r = np.sqrt((1 - pan) / 2) * 1.414, np.sqrt((1 + pan) / 2) * 1.414
    if pump: PL[i:j] += s * l; PR[i:j] += s * r
    else: L[i:j] += s * l; R[i:j] += s * r

drums  = lambda t: (2 <= t < 20) or (24 <= t < 56) or (63 <= t < 73)
groove = lambda t: (0 <= t < 73)
full   = lambda t: (24 <= t < 56) or (66 <= t < 73)
CH = [(38, [60, 65, 69, 72]), (43, [59, 65, 69, 74])]   # Dm7, G9 (no root)
chord = lambda t: CH[int(t // BAR) % 2]

# ---- instruments
def kick():
    n = int(.32 * SR); t = T(n); f = 50 + 120 * np.exp(-t / .022)
    return np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .12))
def snare():
    n = int(.22 * SR); t = T(n)
    body = np.sin(2 * np.pi * 200 * t) * np.exp(-t / .04)
    return body * .6 + hp(lp(rng.standard_normal(n), 7000), 1500) * np.exp(-t / .07)
def clap():
    n = int(.2 * SR); t = T(n); x = hp(lp(rng.standard_normal(n), 6000), 1200)
    return x * (sum(np.exp(-np.maximum(t - d, 0) / .008) * (t >= d) for d in (0, .01, .02)) + .5 * np.exp(-t / .06))
def hat(open_=False):
    n = int((.2 if open_ else .04) * SR)
    return hp(rng.standard_normal(n), 8000, 4) * np.exp(-T(n) / (.06 if open_ else .01))
def slap(m, dur=.2, pop=False):
    n = int(dur * SR); t = T(n); f = hz(m)
    s = np.tanh(2.2 * (np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .05)))
    if pop: s += .6 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / .02)
    return s * np.minimum(1, t / .002) * np.exp(-t / (dur * .55))
def clav(m, dur=.16, wah=1.0):
    n = int(dur * SR); t = T(n); f = hz(m)
    s = sum(np.sin(2 * np.pi * f * h * t) * (1 / h) * np.exp(-t * (8 + h * 6 / wah)) for h in range(1, 11))
    return s * np.minimum(1, t / .001)
def brass(m, dur=.35):
    n = int(dur * SR); t = T(n); f = hz(m)
    env = np.minimum(1, t / .012) * np.exp(-t / .18)
    bright = np.minimum(1, t / .03)
    s = sum(np.sin(2 * np.pi * f * h * t * (1 + .002 * h)) / h * (bright if h > 2 else 1) for h in range(1, 9))
    return s * env
K, SN, CL, H, OH = kick(), snare(), clap(), hat(), hat(True)

# drums: syncopated funk kick, snare+clap on 2 & 4, 16th hats with accents
KICK16 = [0, 3, 6, 10, 11]
kicks = []
for b in range(int(DUR / BAR)):
    t0 = b * BAR
    for half in (0, 1):
        tb = t0 + half * 1.0
        if drums(tb):
            for p in KICK16:
                tk = tb + p * S16
                if p in (10, 11) and half == 0: continue
                add(K, tk, .62 if p == 0 else .45); kicks.append(tk)
            add(SN, tb + .5, .22); add(CL, tb + .5, .14, .1)
    for s in range(16):
        t = t0 + s * S16
        if drums(t) or (56 <= t < 63) or (16 <= t < 24):
            acc = .05 if s % 4 == 2 else .028
            add(OH if s == 14 else H, t, acc * (1.4 if s == 14 else 1), .3)
add(K, 73, .7); add(SN, 73, .2)
for tb in [56 + i for i in range(7)]: add(CL, tb + .5, .14, .1)

# slap bass riff (root-relative 16th pattern)
RIFF = [(0, 0, 1, False), (3, 12, .7, True), (5, 0, .5, False), (7, 12, .8, True),
        (8, 0, .9, False), (10, 10, .7, False), (11, 12, .7, True), (13, 7, .6, False), (14, 10, .8, False), (15, 12, .6, True)]
for b in range(int(74 / BAR)):
    t0 = b * BAR
    for half in (0, 1):
        tb = t0 + half * 1.0
        if not groove(tb): continue
        root = chord(tb)[0]
        for p, iv, v, pop in RIFF:
            if p >= 8: continue
            add(lp(slap(root + iv, .22, pop), 2500), tb + p * S16, .2 * v, 0, True)
        for p, iv, v, pop in RIFF:
            if p < 8: continue
            add(lp(slap(root + iv, .22, pop), 2500), tb + (p - 8) * S16 + .5, .2 * v, 0, True)
# clav stabs on the off 16ths, wah opening in the full sections
CLAV16 = [2, 5, 9, 12, 14]
for b in range(int(74 / BAR)):
    t0 = b * BAR
    for half in (0, 1):
        tb = t0 + half
        if not ((6 <= tb < 73)): continue
        for p in CLAV16:
            t = tb + p * S16 / 2 * 2 if False else tb + (p % 8) * S16 + (.5 if p >= 8 else 0)
            for k, m in enumerate(chord(t)[1]):
                add(clav(m, .15, 1.6 if full(t) else .8), t, .028, .35 if k % 2 else -.15)
# brass stabs on the big moments
def stab(t0, g=.05, up=0):
    for k, m in enumerate(chord(t0)[1]): add(brass(m + up), t0, g, (k - 1.5) * .25)
for t0 in (24.0, 32.0, 40.0, 48.0, 68.0): stab(t0, .04)
for t0 in (70.25, 70.5): stab(t0, .045)
# final chord (Dm9) rings out
for k, m in enumerate([38, 50, 60, 64, 65, 69, 72]):
    add(brass(m, 1.6) if m > 45 else slap(m, 1.6), 73 + k * .01, .06 if m > 45 else .25, (k - 3) * .12)

# gentle pump on the music bus
g = np.ones(N); tt = T(N)
for kt in kicks:
    i = int(kt * SR); j = min(N, i + int(.3 * SR))
    g[i:j] = np.minimum(g[i:j], 1 - .35 * np.exp(-(tt[i:j] - kt) / .07))
L += PL * g; R += PR * g

# ---- SFX: only soft swishes into each scene change (nothing on individual words)
def swish(t0, d=.55, gn=.022):
    n = int(d * SR); t = T(n); p = t / d
    x = rng.standard_normal(n)
    x = lp(hp(x, 600), 5000)
    env = np.sin(np.pi * np.clip(p * 1.15, 0, 1)) ** 2
    add(x * env, t0 - d * .75, gn)
for t0 in (6, 14, 20, 24, 32, 40, 48, 56, 63, 68): swish(t0)
# gentle riser into the four wings
n = int(3.8 * SR); tt = T(n); p = tt / 3.8
xr = hp(rng.standard_normal(n), 800)
add((lp(xr, 1200) * (1 - p) + lp(xr, 6000) * p) * p ** 2.5, 20.2, .03)

def verb(x):
    ir_n = int(1.0 * SR); ir = lp(rng.standard_normal(ir_n), 4500) * np.exp(-T(ir_n) / .22); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + ir_n; F = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + .1 * verb(L); R = R + .1 * verb(R)
mix = np.stack([L, R]); mix = np.tanh(mix * 1.25) / 1.25
mix *= .89 / np.abs(mix).max()
fi = int(.01 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(.6 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
w = wave.open('audio.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix.T * 32767).astype(np.int16).tobytes()); w.close()
for s in range(0, 75, 5):
    seg = mix[:, s * SR:(s + 3) * SR]; print(s, round(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9), 1))
