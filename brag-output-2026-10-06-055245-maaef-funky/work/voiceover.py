# Voiceover for the funky Maaef cut: Kokoro-82M (af_heart), every line from the collective PDF.
# Each line starts on the beat its visual lands and must finish before its window ends.
import sys, numpy as np, soundfile as sf, wave
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro

MODEL_DIR = sys.argv[1]          # folder with kokoro-fp16.onnx and voices.bin
VOICE, SPEED = 'af_heart', 1.05
LINES = [  # (start s, must end by s, text)
    (4.20,  6.70, "A collective that refuses to be one thing."),
    (6.75, 10.10, "Consultants, makers, storytellers and hosts, under one roof."),
    (10.20, 12.80, "Attention, precision, trust and time."),
    (13.35, 15.05, "Institutional consultancy."),
    (15.35, 17.05, "Things you can hold."),
    (17.35, 19.05, "Stories that travel."),
    (19.35, 21.05, "Rooms worth being in."),
    (21.25, 22.25, "Choose your crew."),
    (22.35, 25.15, "Pick one arm, pair two, or bring the whole collective."),
    (25.30, 26.80, "Every arm stands on its own."),
    (26.85, 29.05, "What one creates, the next amplifies."),
    (29.25, 30.15, "The more the merrier."),
    (30.20, 31.70, "We're all about M."),
]
k = Kokoro(f'{MODEL_DIR}/kokoro-fp16.onnx', f'{MODEL_DIR}/voices.bin')
SR = 44100; DUR = 34.0
vo = np.zeros(int(SR * DUR))

def trim(a, thr=.004):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(0, idx[0] - 240): idx[-1] + 2400] if len(idx) else a

for t0, t1, text in LINES:
    speed = SPEED
    for _ in range(6):
        a, sr = k.create(text, voice=VOICE, speed=speed, lang='en-us')
        a = trim(a); dur = len(a) / sr
        if dur <= (t1 - t0) or speed >= 1.2: break
        speed = min(1.2, speed * dur / (t1 - t0) * 1.02)
    a = resample_poly(a, 147, 80)                     # 24 kHz -> 44.1 kHz
    i = int(t0 * SR); vo[i:i + len(a)] += a[:len(vo) - i]
    print(f'{t0:6.2f}  {dur:4.2f}s / {t1 - t0:4.2f}s  speed {speed:.2f}  {text}')

# voice chain: gentle high-pass, a little presence, light compression
from scipy.signal import butter, sosfilt
vo = sosfilt(butter(2, 90, 'high', fs=SR, output='sos'), vo)
vo = vo + .25 * sosfilt(butter(2, [2500, 6000], 'band', fs=SR, output='sos'), vo)
vo = np.tanh(vo * 1.6) / 1.6

# music under it, ducked ~7 dB while the voice talks (smooth envelope)
w = wave.open('audio.wav'); mus = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float64) / 32767
mus = np.pad(mus, ((0, max(0, len(vo) - len(mus))), (0, 0)))[:len(vo)]
env = np.abs(vo) > .015
win = int(.25 * SR); act = np.convolve(env.astype(float), np.ones(win) / win, 'same') > .02
att = np.zeros(len(vo)); g = 0.0; up, dn = 1 / (.06 * SR), 1 / (.35 * SR)
for i in range(0, len(vo), 64):           # block-wise for speed
    target = 1.0 if act[i] else 0.0
    g = min(target, g + up * 64) if target > g else max(target, g - dn * 64)
    att[i:i + 64] = g
duck = 1 - att * (1 - 10 ** (-7 / 20))
mix = mus * duck[:, None] * .9 + vo[:, None] * .55
mix *= .9 / np.abs(mix).max()
out = wave.open('audio_vo.wav', 'wb'); out.setnchannels(2); out.setsampwidth(2); out.setframerate(SR)
out.writeframes((mix * 32767).astype(np.int16).tobytes()); out.close()
sf.write('voiceover_only.wav', vo / np.abs(vo).max() * .9, SR)
