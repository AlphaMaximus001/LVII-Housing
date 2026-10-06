# Voice "Maaef" three ways with the video's voice (Kokoro af_heart, same +4% lift).
# Each clip: the name, a pause, the name again, then "<name>. The Sovereign Collective."
import sys, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro
k = Kokoro(f'{sys.argv[1]}/kokoro-fp16.onnx', f'{sys.argv[1]}/voices.bin')
VARIANTS = [  # (file, as written by the client, phonemes)
    ('1_Maa-ef', 'Maa-ef: long "aa" (father) + "ef", stress on Maa', 'mˈɑːɛf'),
    ('2_Ma-ef',  'Ma-ef: short "ma" (mud) + "ef"',                   'mˈʌɛf'),
    ('3_Ma-eff', 'Ma-eff: short "ma" + stressed "EFF"',              'mʌˈɛf'),
]
def say(ph, speed=1.0):
    for j in range(8):   # the fp16 model sometimes returns silence; nudge and retry
        a, sr = k.create(ph, voice='af_heart', speed=speed + .007 * j, lang='en-us', is_phonemes=True)
        a = np.nan_to_num(a)
        if len(a) and np.abs(a).max() > .05: return a
    return a
rest = k.tokenizer.phonemize('The Sovereign Collective.', 'en-us')
gap = lambda s: np.zeros(int(24000 * s))
for name, desc, ph in VARIANTS:
    clip = np.concatenate([say(ph + '.'), gap(.6), say(ph + '.'), gap(.8), say(ph + '. ' + rest, 1.06)])
    clip = resample_poly(clip, 1767, 1000)           # same +4% lift as the video, 44.1 kHz
    sf.write(f'{name}.wav', clip / np.abs(clip).max() * .9, 44100)
    print(f'{name}.wav  {len(clip)/44100:.1f}s  {desc}  /{ph}/')
