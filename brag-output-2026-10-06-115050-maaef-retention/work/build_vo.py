# Voice-first edit builder for the Maaef four-wings video.
#  1. Synthesises every VO line (Kokoro af_heart, energetic treatment; "Maaef" = Maa-ef /mˈɑːɛf/).
#  2. Lays the lines end to end with tight breaths (no dead air).
#  3. Places the scene cuts as J-cuts, L-cuts or straight cuts on the spoken word, snapped to 16ths of the 120 BPM grid.
#  4. Estimates when each word is spoken, so on-screen elements land with the voice.
# Writes: voice.wav, timeline.json (for the music), cues.js (for the composition).
import sys, json, numpy as np, soundfile as sf
from scipy.signal import resample_poly
from kokoro_onnx import Kokoro

MODEL_DIR = sys.argv[1]
VOICE, SPEED, LIFT = 'af_heart', 1.06, 1.04          # LIFT = +4% pitch for brightness (same as before)
NAME_PH = 'mˈɑːɛf'                                    # Maaef, pronounced "Maa-ef" (client's pick)
SR_OUT = 44100
LINES = [  # (cue key, scene, text)
    ('cover',  'cover', "Maaef. The Sovereign Collective."),
    ('who1',   'who',   "A collective that refuses to be one thing."),
    ('who2',   'who',   "Consultants, makers, storytellers and hosts, under one roof."),
    ('cur1',   'cur',   "We trade in four currencies:"),
    ('cur2',   'cur',   "attention, precision, trust, and time."),
    ('over',   'over',  "A Lucknow-based group of four distinct but connected businesses."),
    ('w0n',    'w0',    "Enterprises."),
    ('w0l',    'w0',    "We find where an institution leaks, fix how it runs, and supply what it needs."),
    ('w0w',    'w0',    "Diagnose, then deliver."),
    ('w1n',    'w1',    "Studios."),
    ('w1l',    'w1',    "If it can be printed, produced, or put in a box, we make it!"),
    ('w1w',    'w1',    "Small test batches, or bulk runs."),
    ('w2n',    'w2',    "Media House."),
    ('w2l',    'w2',    "Artists disguised as a media house. We make the scroll stop!"),
    ('w2w',    'w2',    "Planned before it's shot."),
    ('w3n',    'w3',    "Afterhours."),
    ('w3l',    'w3',    "Where a brand stops talking, and starts hosting!"),
    ('w3w',    'w3',    "Community, not crowds."),
    ('crew1',  'crew',  "Choose your crew."),
    ('crew2',  'crew',  "Pick one arm, pair two, or bring the whole collective!"),
    ('loop1',  'loop',  "Every arm stands on its own."),
    ('loop2',  'loop',  "What one creates, the next amplifies."),
    ('close1', 'close', "The more the merrier."),
    ('close2', 'close', "We're all about M!"),
    ('close3', 'close', "Maaef. A Sovereign Collective."),
]
# how each scene change is cut: 'J' (next line starts before the picture cuts),
# 'L' (current line finishes over the next picture), 'W' (straight cut on the first spoken word)
CUTS = {'who': 'L', 'cur': 'J', 'over': 'J', 'w0': 'W', 'w1': 'J', 'w2': 'L', 'w3': 'J', 'crew': 'L', 'loop': 'J', 'close': 'L'}
GAP_IN, GAP_AFTER_NAME, GAP_SCENE = .2, .12, .3     # breaths: inside a scene, after a wing name, between scenes
LEAD = .45                                            # first word at 0.45s (the star is already moving)
TAIL = 1.7                                            # hold on the final lockup
MIN = {'cover': 2.6, 'who': 5.0, 'cur': 3.4, 'over': 3.3, 'w0': 4.6, 'w1': 4.6, 'w2': 4.6, 'w3': 4.6, 'crew': 3.9, 'loop': 3.3}  # minimum seconds on screen

k = Kokoro(f'{MODEL_DIR}/kokoro-fp16.onnx', f'{MODEL_DIR}/voices.bin')
ph = lambda s: k.tokenizer.phonemize(s, 'en-us') if s.strip() else ''
def to_phonemes(text):
    parts = text.split('Maaef')
    return NAME_PH.join(ph(p) for p in parts).strip()

def synth(text):
    p = to_phonemes(text)
    for j in range(10):     # the fp16 model sometimes returns silence; nudge the speed and retry
        a, sr = k.create(p, voice=VOICE, speed=SPEED + .006 * j * (-1) ** j, lang='en-us', is_phonemes=True)
        a = np.nan_to_num(a)
        if len(a) and np.abs(a).max() > .05: break
    idx = np.where(np.abs(a) > .006)[0]
    a = a[max(0, idx[0] - 120): idx[-1] + 600]          # tight trim: speech plus a short natural tail
    return resample_poly(a, 1767, 1000)                 # 24 kHz -> 44.1 kHz with +4% pitch lift

def word_onsets(text, dur):
    # estimate word timings from each word's phoneme count (good to ~0.1s for a single sentence)
    words = text.replace('—', ' ').split()
    lens = [max(1, len(to_phonemes(w))) for w in words]
    tot = sum(lens) + .6 * (len(words) - 1)
    out, acc = [], 0.0
    for w, n in zip(words, lens):
        out.append([w.strip('.,:!?').lower(), round(acc / tot * dur, 3)]); acc += n + .6
    return out

clips, t, prev_scene = [], LEAD, None
for key, scene, text in LINES:
    a = synth(text)
    if prev_scene is not None:
        t += GAP_SCENE if scene != prev_scene else (GAP_AFTER_NAME if key.endswith('l') and key[0] == 'w' else GAP_IN)
    dur = len(a) / SR_OUT
    clips.append(dict(key=key, scene=scene, text=text, s=round(t, 3), e=round(t + dur, 3), audio=a))
    t += dur; prev_scene = scene
TOTAL = round(t + TAIL, 2)

snap = lambda x: round(x * 8) / 8                      # 16th notes at 120 BPM
scenes, order = [], []
for c in clips:
    if c['scene'] not in order: order.append(c['scene'])
starts = {'cover': 0.0}
for sc in order[1:]:
    prev = order[order.index(sc) - 1]
    first = next(c for c in clips if c['scene'] == sc)
    prev_last = [c for c in clips if c['scene'] == prev][-1]
    kind = CUTS[sc]
    cut = first['s'] + .35 if kind == 'J' else prev_last['e'] - .3 if kind == 'L' else first['s'] - .06
    cut = snap(max(cut, starts[prev] + MIN[prev]))
    # never let the voice run more than 0.35s ahead of its picture: if the hold pushed the cut, push the rest of the voice too
    lag = cut - first['s'] - .35
    if lag > 0:
        for c in clips:
            if c['s'] >= first['s']: c['s'] = round(c['s'] + lag, 3); c['e'] = round(c['e'] + lag, 3)
    starts[sc] = cut
TOTAL = round(clips[-1]['e'] + TAIL, 2)
for i, sc in enumerate(order):
    end = starts[order[i + 1]] if i + 1 < len(order) else TOTAL
    scenes.append([sc, starts[sc], round(end, 3), CUTS.get(sc, '-')])

cues = {c['key']: dict(s=c['s'], e=c['e'], w=[[w, round(c['s'] + o, 3)] for w, o in word_onsets(c['text'], c['e'] - c['s'])]) for c in clips}
voice = np.zeros(int(TOTAL * SR_OUT) + SR_OUT)
for c in clips:
    i = int(c['s'] * SR_OUT); voice[i:i + len(c['audio'])] += c['audio']
voice = voice[:int(TOTAL * SR_OUT)]
sf.write('voice_raw.wav', voice, SR_OUT)
json.dump(dict(total=TOTAL, scenes=scenes, cues=cues), open('timeline.json', 'w'), indent=1)
open('cues.js', 'w').write('window.TL = ' + json.dumps(dict(total=TOTAL, scenes=scenes, cues=cues)) + ';\n')

for sc, a, b, kind in scenes:
    lines = [c for c in clips if c['scene'] == sc]
    print(f'{sc:6s} {a:6.2f}–{b:6.2f} ({b - a:4.1f}s) cut-in:{kind}  ' + ' | '.join(f"{c['s']:.2f}-{c['e']:.2f} {c['text'][:38]}" for c in lines))
gaps = [round(clips[i + 1]['s'] - clips[i]['e'], 2) for i in range(len(clips) - 1)]
print('total', TOTAL, 's; longest silence between lines', max(gaps), 's')
