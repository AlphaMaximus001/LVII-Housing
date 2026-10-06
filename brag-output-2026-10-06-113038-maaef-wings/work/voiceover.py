# Energetic voiceover: Kokoro-82M, af_heart. Copy from 'Maaef Incorporated — The Collective' + Brand Bible.
# "Maaef" is pronounced Maa-Yuf, so the script spells it "Maayuf" (espeak: mˈɑːjʌf).
# Energy: brisker delivery, exclamation phrasing, a small pitch lift (+4%), punchier vocal chain.
import sys, numpy as np, soundfile as sf, wave
from scipy.signal import resample_poly, butter, sosfilt
from kokoro_onnx import Kokoro

MODEL_DIR = sys.argv[1]
VOICE, SPEED, LIFT = 'af_heart', 1.06, 1.04       # LIFT raises pitch (and pace) by 4%
LINES = [  # (start s, must end by s, text)
    (0.80,  4.60, "Maayuf. The Sovereign Collective."),
    (6.40,  9.70, "A collective that refuses to be one thing."),
    (9.90, 13.70, "Consultants, makers, storytellers and hosts, under one roof."),
    (14.30, 16.30, "We trade in four currencies:"),
    (16.40, 19.70, "attention, precision, trust, and time."),
    (20.30, 23.70, "A Lucknow-based group of four distinct but connected businesses."),
    (24.50, 25.95, "Enterprises."),
    (26.00, 31.50, "We find where an institution leaks, fix how it runs, and supply what it needs."),
    (32.50, 33.95, "Studios."),
    (34.00, 39.50, "If it can be printed, produced, or put in a box, we make it!"),
    (40.50, 41.95, "Media House."),
    (42.00, 47.50, "Artists disguised as a media house. We make the scroll stop!"),
    (48.50, 49.95, "Afterhours."),
    (50.00, 55.50, "Where a brand stops talking, and starts hosting!"),
    (56.40, 58.00, "Choose your crew."),
    (58.10, 62.50, "Pick one arm, pair two, or bring the whole collective!"),
    (63.30, 65.20, "Every arm stands on its own."),
    (65.30, 67.80, "What one creates, the next amplifies."),
    (68.30, 69.90, "The more the merrier."),
    (70.00, 71.80, "We're all about M!"),
    (72.10, 74.80, "Maayuf. A Sovereign Collective."),
]
k = Kokoro(f'{MODEL_DIR}/kokoro-fp16.onnx', f'{MODEL_DIR}/voices.bin')
SR = 44100; DUR = 75.0
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
        if dur <= (t1 - t0) or speed >= 1.2: break
        speed = min(1.2, speed * dur / (t1 - t0) * 1.02)
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
