# Mix: voice chain (presence, air, compression) + music ducked 9 dB under the voice.
import numpy as np, soundfile as sf, wave
from scipy.signal import butter, sosfilt
SR = 44100
vo, _ = sf.read('voice_raw.wav')
hp = lambda x, f: sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, a, b: sosfilt(butter(2, [a, b], 'band', fs=SR, output='sos'), x)
vo = hp(vo, 110)
vo = vo + .35 * bp(vo, 2200, 5500) + .15 * hp(vo, 8000)
env = np.sqrt(np.convolve(vo ** 2, np.ones(441) / 441, 'same')) + 1e-6
vo = np.tanh(vo * np.minimum(1, (.12 / env) ** .45) * 2.2) / 2.2
w = wave.open('audio.wav'); mus = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float64) / 32767
n = min(len(mus), len(vo)); mus, vo = mus[:n], vo[:n]
act = np.convolve((np.abs(vo) > .015).astype(float), np.ones(int(.25 * SR)) / int(.25 * SR), 'same') > .02
att = np.zeros(n); g = 0.0; up, dn = 64 / (.05 * SR), 64 / (.3 * SR)
for i in range(0, n, 64):
    g = min(1.0, g + up) if act[i] else max(0.0, g - dn); att[i:i + 64] = g
duck = 1 - att * (1 - 10 ** (-9 / 20))
vo_n = vo / np.abs(vo).max()
mix = mus * duck[:, None] * .85 + vo_n[:, None] * .62
mix *= .9 / np.abs(mix).max()
out = wave.open('audio_vo.wav', 'wb'); out.setnchannels(2); out.setsampwidth(2); out.setframerate(SR)
out.writeframes((mix * 32767).astype(np.int16).tobytes()); out.close()
sf.write('voiceover_only.wav', vo_n * .9, SR)
print('mixed', round(n / SR, 2), 's')
