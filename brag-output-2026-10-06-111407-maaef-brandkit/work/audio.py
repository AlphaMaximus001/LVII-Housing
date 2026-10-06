# Funky soundtrack for the Maaef brand-kit video: 120 BPM, D Dorian vamp (Dm7 | G9).
# 16th = 0.125s, beat = 0.5s, bar = 2s. Times match composition.html.
import numpy as np, wave
from scipy.signal import butter, sosfilt

SR = 44100; DUR = 35.0; N = int(SR * DUR)
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

drums  = lambda t: (0 <= t < 22) or (26 <= t < 33)
groove = lambda t: (0 <= t < 33)
full   = lambda t: (3.5 <= t < 22) or (26 <= t < 33)
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
        if drums(t) or (22 <= t < 26):
            acc = .05 if s % 4 == 2 else .028
            add(OH if s == 14 else H, t, acc * (1.4 if s == 14 else 1), .3)
add(K, 33, .7); add(SN, 33, .2)

# slap bass riff (root-relative 16th pattern)
RIFF = [(0, 0, 1, False), (3, 12, .7, True), (5, 0, .5, False), (7, 12, .8, True),
        (8, 0, .9, False), (10, 10, .7, False), (11, 12, .7, True), (13, 7, .6, False), (14, 10, .8, False), (15, 12, .6, True)]
for b in range(int(34 / BAR)):
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
for b in range(int(34 / BAR)):
    t0 = b * BAR
    for half in (0, 1):
        tb = t0 + half
        if not ((0 <= tb < 33)): continue
        for p in CLAV16:
            t = tb + p * S16 / 2 * 2 if False else tb + (p % 8) * S16 + (.5 if p >= 8 else 0)
            for k, m in enumerate(chord(t)[1]):
                add(clav(m, .15, 1.6 if full(t) else .8), t, .028, .35 if k % 2 else -.15)
# brass stabs on the big moments
def stab(t0, g=.05, up=0):
    for k, m in enumerate(chord(t0)[1]): add(brass(m + up), t0, g, (k - 1.5) * .25)
for t0 in (1.5, 5.5, 10.0, 12.0, 26.0): stab(t0)
for t0 in (32.5, 32.75): stab(t0, .055)
# final chord (Dm9) rings out
for k, m in enumerate([38, 50, 60, 64, 65, 69, 72]):
    add(brass(m, 1.6) if m > 45 else slap(m, 1.6), 33 + k * .01, .06 if m > 45 else .25, (k - 3) * .12)

# gentle pump on the music bus
g = np.ones(N); tt = T(N)
for kt in kicks:
    i = int(kt * SR); j = min(N, i + int(.3 * SR))
    g[i:j] = np.minimum(g[i:j], 1 - .35 * np.exp(-(tt[i:j] - kt) / .07))
L += PL * g; R += PR * g

# ---- SFX on the motion
def blip(m, t0, gn=.04, pan=0): add(clav(m, .18, 2.0), t0, gn, pan)
def tick(t0, gn=.05):
    n = int(.02 * SR); add(lp(rng.standard_normal(n), 4000) * np.exp(-T(n) / .004), t0, gn)
def zip_(t0, d=.24, gn=.05, up=True):   # tonal whip
    n = int(d * SR); t = T(n); p = t / d
    f = (250 + 1800 * p ** 2) if up else (2000 - 1700 * p)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * p) ** 2, t0, gn)
def typing(t0, chars, cps, gn=.018):
    for k in range(chars): tick(t0 + k / cps, gn * (.7 + .6 * ((k * 7) % 5) / 4))
# S1: star spin, headline sweep, highlight
zip_(0.0, .45, .04); blip(86, .5, .035); blip(81, 1.0, .035); zip_(1.5, .2, .04)
# whips between scenes
for t0 in (3.5, 8, 12, 22, 26, 30): zip_(t0 - .24, .3, .045)
# S2: feed scroll whoosh, hard stop on the beat, highlight
zip_(3.6, 1.8, .025, False); add(K, 5.5, .5); blip(74, 5.5, .05); zip_(6.4, .2, .035)
# S3: strike, WORK slam
zip_(9.5, .18, .05); add(K, 10.0, .6)
# S4: nodes light, dots run the wires, tags
for k in range(4):
    blip(74 + [0, 3, 5, 7][k], 12 + k * 2.5, .045)
    for s in range(4): tick(12 + k * 2.5 + .75 + s * .25, .05)
for k in range(3): zip_(12 + k * 2.5 + 1.9, .6, .025)
# S5: counter ticks, stamp
for k in range(12): tick(22.8 + k * (1.4 / 12), .05)
add(K, 24.5, .55); blip(81, 24.5, .04)
# S6: one value per beat
for k, m in enumerate([74, 77, 81, 84, 86]): blip(m, 26.5 + k * .5, .04, (k - 2) * .2)
# S7: logo in
blip(86, 32.5, .045)

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
for s in range(0, 35, 3):
    seg = mix[:, s * SR:(s + 3) * SR]; print(s, round(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9), 1))
