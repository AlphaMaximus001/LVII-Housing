# Soundtrack for the Maaef Collective video: 120 BPM, D minor (Dm - Bb - F - C).
# Times match the timeline in composition.html (beat = 0.5s, bar = 2s).
import numpy as np, wave
from scipy.signal import butter, sosfilt

SR = 44100; DUR = 30.0; N = int(SR * DUR)
BEAT = .5; BAR = 2.0
rng = np.random.default_rng(5)
L = np.zeros(N); R = np.zeros(N); PL = np.zeros(N); PR = np.zeros(N)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def T(n): return np.arange(n) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def add(sig, t0, g=1.0, pan=0.0, pump=False):
    i = int(round(t0 * SR))
    if i >= N: return
    j = min(N, i + len(sig)); s = sig[:j - i] * g
    l, r = np.sqrt((1 - pan) / 2) * 1.414, np.sqrt((1 + pan) / 2) * 1.414
    if pump: PL[i:j] += s * l; PR[i:j] += s * r
    else: L[i:j] += s * l; R[i:j] += s * r

drums = lambda t: 3.5 <= t < 28
clapz = lambda t: 8 <= t < 28
full  = lambda t: 11 <= t < 28
CH = [(50, [62, 65, 69, 72]), (46, [62, 65, 70, 74]), (53, [60, 65, 69, 72]), (48, [60, 64, 67, 72])]
chord = lambda t: CH[int(t // BAR) % 4]

def kick():
    n = int(.4 * SR); t = T(n); f = 46 + 90 * np.exp(-t / .028)
    return np.tanh(1.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .16))
def hat(d=.05, dec=.012):
    n = int(d * SR); return hp(rng.standard_normal(n), 8000, 4) * np.exp(-T(n) / dec)
def clap():
    n = int(.2 * SR); t = T(n); x = hp(lp(rng.standard_normal(n), 6000), 1200)
    return x * (sum(np.exp(-np.maximum(t - d, 0) / .008) * (t >= d) for d in (0, .01, .02)) + .5 * np.exp(-t / .06))
def pad(m, dur):
    n = int(dur * SR); t = T(n)
    s = sum(np.sin(2 * np.pi * hz(m) * k * t * (1 + .0015 * (k % 2))) / k ** 1.4 for k in range(1, 6))
    return s * np.minimum(1, t / .25) * np.minimum(1, (dur - t) / .3)
def pluck(m, dur=.4, bright=1.0):
    n = int(dur * SR); t = T(n); f = hz(m)
    s = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * (6 + 9 * k / bright)) / k for k in range(1, 6))
    return s * np.minimum(1, t / .002)
K, H, OH, CL = kick(), hat(), hat(.18, .05), clap()

kicks = []
for i in range(int(DUR / BEAT)):
    t = i * BEAT
    if drums(t):
        add(K, t, .7); kicks.append(t)
        add(OH, t + BEAT / 2, .07 if full(t) else .05, .25)
        if full(t): add(H, t + BEAT / 4, .03, -.3); add(H, t + 3 * BEAT / 4, .03, -.3)
        if clapz(t) and i % 2 == 1: add(CL, t, .22, .05)
add(K, 28, .75)

# pads: whole track, filtered darker in the intro
for b in range(int(28 / BAR)):
    t0 = b * BAR
    for k, m in enumerate(chord(t0)[1]):
        s = pad(m, BAR + .05)
        add(lp(s, 900 if t0 < 3.5 else (1600 if not full(t0) else 2400)), t0, .03, (k - 1.5) * .25, True)
# bass: offbeat eighths, root and octave
for i in range(int(DUR / (BEAT / 2))):
    t = i * BEAT / 2
    if not drums(t) or i % 2 == 0: continue
    m = chord(t)[0] - 12 + (12 if (i // 2) % 2 else 0)
    n = int(.22 * SR); tt = T(n)
    s = np.tanh(1.8 * np.sin(2 * np.pi * hz(m) * tt)) * np.minimum(1, tt / .004) * np.exp(-tt / .1)
    add(lp(s, 800), t, .2, 0, True)
# pluck arpeggio over the arms and the crew
ARP = [0, 2, 1, 3, 2, 1, 3, 2]
for i in range(int(DUR / (BEAT / 2))):
    t = i * BEAT / 2
    if full(t):
        m = chord(t)[1][ARP[i % 8]] + 12
        add(pluck(m, .35, .8), t, .03, .35 if i % 2 else -.35)
# final chord
for k, m in enumerate([38, 50, 57, 62, 65, 69, 74]):
    n = int(2.0 * SR); t = T(n)
    s = sum(np.sin(2 * np.pi * hz(m) * j * t) / j ** 1.5 for j in range(1, 4)) * np.exp(-t / .9) * np.minimum(1, t / .004)
    add(s, 28 + k * .01, .06 if m > 45 else .12, (k - 3) * .12)

# sidechain
g = np.ones(N); tt = T(N)
for kt in kicks:
    i = int(kt * SR); j = min(N, i + int(.45 * SR))
    g[i:j] = np.minimum(g[i:j], 1 - .55 * np.exp(-(tt[i:j] - kt) / .09))
L += PL * g; R += PR * g

# ---- SFX (tonal, in key, mixed under)
def note(m, t0, gn=.05, pan=0): add(pluck(m, .6, 1.4), t0, gn, pan)
def thump(t0, gn=.3):
    n = int(.35 * SR); t = T(n)
    add(np.sin(2 * np.pi * (50 + 40 * np.exp(-t / .03)) * t) * np.exp(-t / .12), t0, gn)
def sweep(t0, d=.4, gn=.04):   # tonal swoosh for the page wipes
    n = int(d * SR); t = T(n); p = t / d
    f = 300 + 1500 * p ** 2
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * p) ** 2, t0, gn)
# cover: MAAEF letters on half-beats, tag, location
for k, m in enumerate([62, 65, 69, 72, 74]): note(m, .25 + k * .25, .06, (k - 2) * .15)
thump(1.75, .35); note(81, 2.25, .03)
# page wipes
for t0 in (3.5, 8, 11, 14, 17, 20, 23, 27): sweep(t0 - .05)
# who: "ONE THING." lands
thump(5.75, .3)
# currencies on beats
for k, m in enumerate([74, 77, 81, 86]): note(m, 8.5 + k * .5, .05, .2)
# crew cards on beats
for k, m in enumerate([69, 72, 77, 81]): note(m, 24 + k * .5, .05, -.2)
# close: M underline, mark
note(86, 28.0, .04); thump(28.5, .25)

def verb(x):
    ir_n = int(1.3 * SR); ir = lp(rng.standard_normal(ir_n), 4000) * np.exp(-T(ir_n) / .32); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + ir_n; F = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + .14 * verb(L); R = R + .14 * verb(R)
mix = np.stack([L, R]); mix = np.tanh(mix * 1.2) / 1.2
mix *= .89 / np.abs(mix).max()
fi = int(.02 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(.8 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
w = wave.open('audio.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix.T * 32767).astype(np.int16).tobytes()); w.close()
for s in range(0, 30, 3):
    seg = mix[:, s * SR:(s + 3) * SR]; print(s, round(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9), 1))
