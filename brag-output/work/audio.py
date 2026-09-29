# Soundtrack for the LVII brag video: 120 BPM house, C major (C G Am F).
# Every SFX time below matches a beat in composition.html.
import numpy as np, wave
from scipy.signal import lfilter, butter, sosfilt

SR = 44100; DUR = 40.0; N = int(SR * DUR)
BEAT = 0.5; BAR = 2.0
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
MUS_L = np.zeros(N); MUS_R = np.zeros(N)   # pumped (sidechained) bus

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def T(n): return np.arange(n) / SR
def add(sig, t0, g=1.0, pan=0.0, bus='main'):
    i = int(round(t0 * SR));
    if i >= N: return
    j = min(N, i + len(sig)); s = sig[:j - i] * g
    l, r = np.sqrt((1 - pan) / 2) * 1.414, np.sqrt((1 + pan) / 2) * 1.414
    if bus == 'pump': MUS_L[i:j] += s * l; MUS_R[i:j] += s * r
    else: L[i:j] += s * l; R[i:j] += s * r
def lp(x, fc, order=2): return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)

# ---- song sections
def kick_on(t):   return (0 <= t < 12) or (16 <= t < 38)
def full(t):      return (16 <= t < 32) or (34 <= t < 38)
def clap_on(t):   return (6 <= t < 12) or (16 <= t < 33) or (34 <= t < 38)
CH = [(48, [60, 64, 67, 72]), (43, [59, 62, 67, 71]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]  # C G Am F
def chord(t): return CH[int(t // BAR) % 4]

# ---- drums
def kick():
    n = int(.4 * SR); t = T(n)
    f = 48 + 110 * np.exp(-t / .025); ph = 2 * np.pi * np.cumsum(f) / SR
    click = rng.standard_normal(n) * np.exp(-t / .002) * .3
    return np.tanh(1.6 * np.sin(ph) * np.exp(-t / .16)) + click
def clap():
    n = int(.25 * SR); t = T(n); x = rng.standard_normal(n)
    e = sum(np.exp(-np.maximum(t - d, 0) / .008) * (t >= d) for d in (0, .01, .02)) + .6 * np.exp(-t / .08)
    return hp(lp(x, 4000), 900) * e
def hat(d=.04, dec=.012):
    n = int(d * SR); return hp(rng.standard_normal(n), 7000, 4) * np.exp(-T(n) / dec)
def snare():
    n = int(.18 * SR); t = T(n)
    return (hp(rng.standard_normal(n), 1500) * .8 + np.sin(2 * np.pi * 190 * t) * .5) * np.exp(-t / .05)
K, C, H, OH, S = kick(), clap(), hat(), hat(.2, .06), snare()

kick_times = []
for i in range(int(DUR / BEAT)):
    t = i * BEAT
    if kick_on(t):
        add(K, t, .75 if t >= 6 else .55); kick_times.append(t)
    if clap_on(t) and i % 2 == 1: add(C, t, .32)
    if (t >= 6 and t < 12) or full(t): add(OH, t + BEAT / 2, .09, .25)     # offbeat open hat
    if kick_on(t):
        for k in (1, 3): add(H, t + k * BEAT / 4, .05 if full(t) else .035, -.3)
# final hit
add(K, 38, .8); add(C, 38, .3)

# builds: snare rolls accelerating into the drops
def roll(a, b, g0, g1):
    t = a; step = BEAT / 2
    while t < b - 1e-6:
        p = (t - a) / (b - a); add(S, t, g0 + (g1 - g0) * p, 0)
        if p > .5: step = BEAT / 4
        if p > .8: step = BEAT / 8
        t += step
roll(14.0, 15.75, .08, .3)
roll(33.0, 33.875, .06, .25)
def riser(a, b, g):
    n = int((b - a) * SR); t = T(n); p = t / (b - a)
    x = rng.standard_normal(n)
    # sweep by blending progressively brighter noise
    y = lp(x, 600) * (1 - p) + hp(x, 2000) * p
    add(y * p ** 2, a, g)
riser(12.5, 15.75, .22); riser(32.5, 33.9, .16)
def impact(t0, g):
    n = int(2.2 * SR); t = T(n)
    boom = np.sin(2 * np.pi * (38 + 40 * np.exp(-t / .05)) * t) * np.exp(-t / .6)
    crash = hp(rng.standard_normal(n), 3000) * np.exp(-t / .7) * .35
    add(boom + crash, t0, g)
impact(16, .55); impact(34, .5)

# ---- music (pumped bus)
# pads: filtered in the intro/breakdown, open in drops
for b in range(int(38 / BAR)):
    t0 = b * BAR; root, notes = chord(t0)
    for m in notes:
        n = int(2.05 * SR); t = T(n)
        s = sum(np.sin(2 * np.pi * hz(m) * k * t + k) / k for k in range(1, 6)) * np.minimum(1, t / .02) * np.exp(-t / 3)
        s = lp(s, 2600 if full(t0) else (1200 if t0 < 12 else 700))
        add(s, t0, .035, ((m % 5) - 2) * .2, 'pump')
# stab chords on the off-beats in drops (the "upbeat" hook)
for i in range(int(DUR / BEAT)):
    t = i * BEAT + BEAT / 2
    if full(t) or (6 <= t < 12):
        for m in chord(t)[1]:
            n = int(.2 * SR); tt = T(n)
            s = (np.sin(2 * np.pi * hz(m + 12) * tt) + .5 * np.sin(2 * np.pi * hz(m + 12) * 2 * tt)) * np.exp(-tt / .07)
            add(s, t, .03 if full(t) else .02, .3 if m % 2 else -.3)
# bass: octave-bouncing eighths
for i in range(int(DUR / (BEAT / 2))):
    t = i * BEAT / 2
    if (6 <= t < 12) or full(t):
        root = chord(t)[0] - 12 + (12 if i % 2 else 0)
        n = int(.24 * SR); tt = T(n)
        s = np.tanh(2 * np.sin(2 * np.pi * hz(root) * tt)) * np.exp(-tt / .12) * np.minimum(1, tt / .004)
        add(lp(s, 900), t, .18, 0, 'pump')
# lead hook in the drops: one bar motif per chord (eighth-note steps, chord tones)
MOTIF = [(0, 2), (3, 1), (4, 2), (6, 3), (7, 1)]   # (eighth index, chord note index)
for b in range(int(38 / BAR)):
    t0 = b * BAR
    if not (16 <= t0 < 32 or 34 <= t0 < 38): continue
    notes = chord(t0)[1]
    for k, (e, ni) in enumerate(MOTIF):
        m = notes[ni] + 12; n = int(.35 * SR); tt = T(n)
        s = sum(np.sin(2 * np.pi * hz(m) * h * tt) / h ** 1.3 for h in range(1, 5)) * np.exp(-tt / .14) * np.minimum(1, tt / .003)
        add(s, t0 + e * BEAT / 2, .032, .2 if k % 2 else -.2)
# final chord ring
for m in [48, 55, 60, 64, 67, 74, 79]:
    n = int(2.2 * SR); t = T(n)
    s = sum(np.sin(2 * np.pi * hz(m) * k * t) / k ** 1.5 for k in range(1, 4)) * np.exp(-t / 1.1) * np.minimum(1, t / .005)
    add(s, 38, .05, ((m % 5) - 2) * .2)

# sidechain pump on the music bus
g = np.ones(N); tt = T(N)
for kt in kick_times:
    i = int(kt * SR); j = min(N, i + int(.45 * SR))
    g[i:j] = np.minimum(g[i:j], 1 - .7 * np.exp(-(tt[i:j] - kt) / .09))
L += MUS_L * g; R += MUS_R * g

# ---- SFX, in key (C major pentatonic)
def blip(m, t0, gn=.08, pan=0):
    n = int(.3 * SR); t = T(n)
    s = (np.sin(2 * np.pi * hz(m) * t) + .25 * np.sin(2 * np.pi * hz(m) * 2 * t)) * np.exp(-t / .08) * np.minimum(1, t / .002)
    add(s, t0, gn, pan)
def pop(t0, gn=.12, pan=0):   # bubbly pitch-drop pop
    n = int(.09 * SR); t = T(n); f = 900 * np.exp(-t / .02) + 300
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .03), t0, gn, pan)
def click(t0, gn=.12):
    n = int(.03 * SR); add(lp(rng.standard_normal(n), 3500) * np.exp(-T(n) / .004), t0, gn)
def whoosh(t0, d, gn):
    n = int(d * SR); t = T(n); x = rng.standard_normal(n); p = t / d
    add((lp(x, 1500) * (1 - p) + hp(x, 1500) * p) * np.sin(np.pi * p) ** 2, t0, gn)

# S1 notifications on beats 1-4
for k, m in enumerate([76, 79, 84, 88]): pop(1 + k, .1, .3); blip(m, 1 + k, .06, .3)
blip(72, 0, .05); click(0, .1)
# S2 chores, one per beat
for k in range(6): pop(6.5 + k * .5, .1, .3)
for k in range(3): add(S, 10 + k * .125, .1)   # overload stutter
# S2b text hits
blip(60, 12, .07); blip(67, 13.5, .06)
# S3 bands + lockup
whoosh(16.85, .4, .12); whoosh(17.85, .4, .1); pop(18.5, .14); blip(84, 18.5, .06)
# S4 items + rising ticks
for k in range(5): pop(20.5 + k * .5, .08, .3)
for k, m in enumerate([72, 74, 76, 79, 81]): blip(m + 12, 23 + k * .5, .07, .3)
# S5 bill + count + chime
pop(26.5, .12)
for k in range(6): click(27.75 + k * .25, .08)
for m in [84, 88, 91]: blip(m, 29, .05)
# S6 clicks
click(31.5, .18); pop(31.5, .08); whoosh(31.85, .3, .05); click(33, .18); pop(33, .08)
# S7 pops + button press
pop(34.5, .1); pop(35.5, .1); click(37, .14); blip(91, 37, .05)

# ---- master
def verb(x):
    ir_n = int(1.4 * SR); ir = lp(rng.standard_normal(ir_n), 3000) * np.exp(-T(ir_n) / .35); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + ir_n; F = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + .12 * verb(L); R = R + .12 * verb(R)
mix = np.stack([L, R]); mix = np.tanh(mix * 1.2) / 1.2
mix *= .9 / np.abs(mix).max()
fo = int(1.2 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
pcm = (mix.T * 32767).astype(np.int16)
w = wave.open('audio.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
for s in range(0, 40, 4):
    seg = mix[:, s * SR:(s + 4) * SR]; print(s, round(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9), 1))
