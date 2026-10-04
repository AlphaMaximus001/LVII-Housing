# Cozy, upbeat soundtrack for the 30s LVII video: 100 BPM, F major.
# Fmaj7 - Dm7 - Bbmaj7 - C, one chord per bar (2.4s). Times match timeline.js.
import numpy as np, wave
from scipy.signal import butter, sosfilt

SR = 44100; DUR = 30.0; N = int(SR * DUR)
BEAT = 0.6; BAR = 2.4
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N); PL = np.zeros(N); PR = np.zeros(N)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def T(n): return np.arange(n) / SR
def lp(x, fc, o=2): return sosfilt(butter(o, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, 'high', fs=SR, output='sos'), x)
def add(sig, t0, g=1.0, pan=0.0, pump=False):
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0: return
    j = min(N, i + len(sig)); s = sig[:j - i] * g
    l, r = np.sqrt((1 - pan) / 2) * 1.414, np.sqrt((1 + pan) / 2) * 1.414
    if pump: PL[i:j] += s * l; PR[i:j] += s * r
    else: L[i:j] += s * l; R[i:j] += s * r

# sections
groove   = lambda t: (0 <= t < 8.4) or (12 <= t < 28.8)
full     = lambda t: 12 <= t < 28.8
CH = [(41, [53, 57, 60, 64]), (38, [50, 57, 60, 65]), (34, [50, 53, 57, 62]), (36, [52, 55, 60, 62])]
chord = lambda t: CH[int(t // BAR) % 4]

# ---- instruments
def rhodes(m, dur, vel=1.0):
    n = int(dur * SR); t = T(n); f = hz(m)
    body = np.sin(2 * np.pi * f * t) + .22 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .6)
    tine = .18 * np.sin(2 * np.pi * 7.1 * f * t) * np.exp(-t / .05)
    env = np.minimum(1, t / .008) * np.exp(-t / 1.6)
    return (body + tine) * env * (1 + .12 * np.sin(2 * np.pi * 4.2 * t)) * vel
def kalimba(m, dur=.9):
    n = int(dur * SR); t = T(n); f = hz(m)
    s = np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 3.02 * f * t) * np.exp(-t / .05) + .1 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t / .02)
    return s * np.minimum(1, t / .002) * np.exp(-t / .28)
def kick():
    n = int(.35 * SR); t = T(n)
    f = 52 + 70 * np.exp(-t / .03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .13)
def rim():
    n = int(.08 * SR); t = T(n)
    return (np.sin(2 * np.pi * 1700 * t) * .5 + hp(rng.standard_normal(n), 2500) * .5) * np.exp(-t / .012)
def clap():
    n = int(.22 * SR); t = T(n); x = hp(lp(rng.standard_normal(n), 5000), 1100)
    e = sum(np.exp(-np.maximum(t - d, 0) / .01) * (t >= d) for d in (0, .012, .024)) + .5 * np.exp(-t / .07)
    return x * e
def shaker():
    n = int(.09 * SR); t = T(n)
    return hp(rng.standard_normal(n), 5000, 4) * np.minimum(1, t / .015) * np.exp(-t / .03)
K, RIM, CL, SH = kick(), rim(), clap(), shaker()

kick_times = []
for i in range(int(DUR / (BEAT / 2))):
    t = i * BEAT / 2; on_beat = i % 2 == 0; beat_i = i // 2
    if on_beat and groove(t):
        add(K, t, .55 if full(t) else .42); kick_times.append(t)
        if beat_i % 2 == 1: add(CL if full(t) else RIM, t, .2 if full(t) else .14, .1)
    if groove(t) or (10.2 <= t < 12):
        add(SH, t, (.07 if not on_beat else .045) * (1 if groove(t) else .6), .35)
add(K, 28.8, .5)

# Rhodes: chord on the downbeat + a soft push on the "and" of beat 2
for b in range(int(28.8 / BAR)):
    t0 = b * BAR; root, notes = chord(t0)
    for k, m in enumerate(notes):
        add(rhodes(m, 2.6), t0 + k * .012, .07, ((k % 2) * 2 - 1) * .25, True)
        if groove(t0): add(rhodes(m, 1.0, .6), t0 + 1.5 * BEAT, .045, ((k % 2) * 2 - 1) * .25, True)
# bass: warm root with a little walk
for i in range(int(DUR / BEAT)):
    t = i * BEAT
    if not groove(t) or t >= 28.8: continue
    root = chord(t)[0]; step = i % 4
    m = root + [0, 0, 7, 12][step] if full(t) else root
    n = int(.5 * SR); tt = T(n)
    s = (np.sin(2 * np.pi * hz(m) * tt) + .3 * np.sin(2 * np.pi * 2 * hz(m) * tt)) * np.minimum(1, tt / .01) * np.exp(-tt / .3)
    add(lp(s, 700), t, .22, 0, True)
# kalimba melody in the full section (chord tones, gentle syncopation)
MOTIF = [(0, 3), (3, 2), (4, 1), (6, 2)]
for b in range(int(12 / BAR), int(28.8 / BAR)):
    t0 = b * BAR; notes = chord(t0)[1]
    for k, (e, ni) in enumerate(MOTIF):
        add(kalimba(notes[ni] + 12), t0 + e * BEAT / 2, .06, .25 if k % 2 else -.25)
# breakdown: warm swell into the reveal
n = int(3.6 * SR); t = T(n); p = t / 3.6
sw = sum(np.sin(2 * np.pi * hz(m) * t) for m in [53, 60, 65, 69]) * p ** 2
add(lp(sw, 1800), 8.4, .03)
# final chord rings out
for k, m in enumerate([41, 53, 57, 60, 64, 67, 72]):
    add(rhodes(m, 1.4 + 1.6), 28.8 + k * .015, .07 if m > 45 else .1, ((k % 2) * 2 - 1) * .2)

# gentle sidechain so the groove breathes
g = np.ones(N); tt = T(N)
for kt in kick_times:
    i = int(kt * SR); j = min(N, i + int(.5 * SR))
    g[i:j] = np.minimum(g[i:j], 1 - .35 * np.exp(-(tt[i:j] - kt) / .12))
L += PL * g; R += PR * g

# ---- SFX: soft, in key, tucked under the music
def note(m, t0, gn=.05, pan=.3): add(kalimba(m, .6), t0, gn, pan)
def tick(t0, gn=.05):
    n = int(.03 * SR); add(lp(rng.standard_normal(n), 3000) * np.exp(-T(n) / .006), t0, gn)
# S1: notifications (beats 1-4)
for k, m in enumerate([72, 76, 79, 77]): note(m, .6 * (k + 1), .055)
# S2: chores, half-beats
for k in range(6): tick(4.2 + .45 + k * .3, .045)
# S2b: lines
note(65, 8.5, .04, 0); note(69, 9.6, .04, 0)
# S3: reveal bloom + mark settle
for k, m in enumerate([77, 81, 84, 89]): note(m, 12 + k * .08, .035, (k - 1.5) * .2)
note(84, 14.15, .04, 0)
# S4: sorted ticks rising
for k, m in enumerate([77, 79, 81, 84, 86]): note(m, 15.6 + 1.8 + k * .3, .045)
# S5: bill + counter + zero
note(72, 20.1, .04)
for k in range(6): tick(19.8 + 1.2 + k * .15, .035)
for m in [81, 84, 89]: note(m, 22.2, .03, 0)
# S6: clicks
tick(23.4 + 1.2, .07); tick(23.4 + 2.4, .07)
# S7: button
tick(26.4 + 2.4, .06); note(89, 26.4 + 2.42, .035, 0)

# ---- very faint rain: individual droplets only, no hiss bed
def rain_channel(seed):
    r = np.random.default_rng(seed)
    imp = np.zeros(N)
    count = int(DUR * 220)
    pos = r.integers(0, N, count)
    imp[pos] = r.random(count) ** 3 * (r.random(count) < .97) + (r.random(count) < .03) * r.random(count) * 2.5
    out = np.zeros(N)
    for f in (2300, 3100, 4200, 5400):
        k = T(int(.012 * SR)); ker = np.sin(2 * np.pi * f * k) * np.exp(-k / .0025)
        part = np.zeros(N); sel = r.random(N) < .25
        part[sel] = imp[sel]
        out += np.convolve(part, ker)[:N]
    out = lp(hp(out, 900), 6500)
    return out / (np.sqrt((out ** 2).mean()) + 1e-12)
RAIN_GAIN = .0025
rl, rr = rain_channel(21), rain_channel(22)

def verb(x):
    ir_n = int(1.8 * SR); ir = lp(rng.standard_normal(ir_n), 3500) * np.exp(-T(ir_n) / .5); ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + ir_n; F = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
L = L + .2 * verb(L); R = R + .2 * verb(R)
mix = np.stack([lp(L, 9000), lp(R, 9000)])
mix = np.tanh(mix * 1.1) / 1.1
mix *= .88 / np.abs(mix).max()
mix[0] += rl * RAIN_GAIN; mix[1] += rr * RAIN_GAIN
mix *= min(1, .89 / np.abs(mix).max())
fi = int(.3 * SR); mix[:, :fi] *= np.linspace(0, 1, fi)
fo = int(1.0 * SR); mix[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
w = wave.open('audio.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix.T * 32767).astype(np.int16).tobytes()); w.close()
for s in range(0, 30, 3):
    seg = mix[:, s * SR:(s + 3) * SR]; print(s, round(20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9), 1))
