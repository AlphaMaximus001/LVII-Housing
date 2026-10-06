# Energetic voiceover: Kokoro-82M, af_heart. Copy from the Maaef Brand Bible / brand kit.
# Energy: brisker delivery, exclamation phrasing, a small pitch lift (+4%), punchier vocal chain.
import sys, numpy as np, soundfile as sf, wave
from scipy.signal import resample_poly, butter, sosfilt
from kokoro_onnx import Kokoro

MODEL_DIR = sys.argv[1]
VOICE, SPEED, LIFT = 'af_heart', 1.12, 1.04       # LIFT raises pitch (and pace) by 4%
LINES = [  # (start s, must end by s, text)
    (0.35,  3.30, "We engineer attention!"),
    (3.70,  5.45, "Make people stop scrolling,"),
    (5.50,  7.90, "and actually pay attention!"),
    (8.20,  9.90, "Not just look good."),
    (10.00, 11.60, "Work!"),
    (12.20, 14.75, "Media House: video, design, web, and brand strategy!"),
    (14.75, 17.20, "Studios: bringing ideas to paper!"),
    (17.25, 19.70, "Afterhours: a space to meet, learn, and grow!"),
    (19.75, 22.25, "Enterprises: a registered supplier on GeM!"),
    (22.40, 24.35, "Ten copies, or ten thousand!"),
    (24.45, 25.95, "On time, and on spec!"),
    (26.45, 29.80, "Creative! Accurate! Inclusive! Bold! Reliable!"),
    (30.15, 31.65, "Good work comes from the same core:"),
    (31.70, 33.40, "showing up with intent!"),
]
k = Kokoro(f'{MODEL_DIR}/kokoro-fp16.onnx', f'{MODEL_DIR}/voices.bin')
SR = 44100; DUR = 35.0
vo = np.zeros(int(SR * DUR))
def trim(a, thr=.004):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(0, idx[0] - 240): idx[-1] + 2400] if len(idx) else a
for t0, t1, text in LINES:
    speed = SPEED
    for _ in range(6):
        for j in range(8):    # the fp16 model sometimes returns silence/NaN; nudge the speed and retry
            a, sr = k.create(text, voice=VOICE, speed=speed + .007 * j * (-1) ** j, lang='en-us')
            a = np.nan_to_num(a)
            if len(a) and np.abs(a).max() > .05: break
        a = trim(a); dur = len(a) / sr / LIFT
        if dur <= (t1 - t0) or speed >= 1.3: break
        speed = min(1.3, speed * dur / (t1 - t0) * 1.02)
    a = resample_poly(a, 1767, 1000)           # 24 kHz played at 44.1 kHz with +4% pitch
    i = int(t0 * SR); vo[i:i + len(a)] += a[:len(vo) - i]
    print(f'{t0:6.2f}  {dur:4.2f}s / {t1 - t0:4.2f}s  speed {speed:.2f}  {text}')

# punchier chain: high-pass, presence lift, air, then firm compression
hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
vo = hp(vo, 110)
vo = vo + .35 * bp(vo, 2200, 5500) + .15 * hp(vo, 8000)
env = np.sqrt(np.convolve(vo ** 2, np.ones(441) / 441, 'same')) + 1e-6
gain = np.minimum(1, (.12 / env) ** .45)          # ~2:1 above threshold
vo = np.tanh(vo * gain * 2.2) / 2.2

# music ducked ~9 dB under the voice
w = wave.open('audio.wav'); mus = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float64) / 32767
mus = np.pad(mus, ((0, max(0, len(vo) - len(mus))), (0, 0)))[:len(vo)]
act = np.convolve((np.abs(vo) > .015).astype(float), np.ones(int(.25 * SR)) / int(.25 * SR), 'same') > .02
att = np.zeros(len(vo)); g = 0.0; up, dn = 64 / (.05 * SR), 64 / (.3 * SR)
for i in range(0, len(vo), 64):
    g = min(1.0, g + up) if act[i] else max(0.0, g - dn); att[i:i + 64] = g
duck = 1 - att * (1 - 10 ** (-9 / 20))
vo_n = vo / np.abs(vo).max()
mix = mus * duck[:, None] * .85 + vo_n[:, None] * .62
mix *= .9 / np.abs(mix).max()
out = wave.open('audio_vo.wav', 'wb'); out.setnchannels(2); out.setsampwidth(2); out.setframerate(SR)
out.writeframes((mix * 32767).astype(np.int16).tobytes()); out.close()
sf.write('voiceover_only.wav', vo_n * .9, SR)
