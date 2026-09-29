import numpy as np, wave
SR=44100; DUR=20.0; N=int(SR*DUR)
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
BEAT=0.5
def hz(m): return 440*2**((m-69)/12)
def env(n,a,d,s=0.0,rel=None):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-t/d)*(1-s)+s
    return e
def add(sig,t0,g=1.0,pan=0.0):
    i=int(t0*SR); j=min(N,i+len(sig)); 
    if i>=N: return
    s=sig[:j-i]*g
    L[i:j]+=s*np.sqrt((1-pan)/2)*1.414/1.414; R[i:j]+=s*np.sqrt((1+pan)/2)
def tone(f,dur,a=.005,d=.3,harm=((1,1),),vib=0):
    n=int(dur*SR); t=np.arange(n)/SR
    s=sum(amp*np.sin(2*np.pi*f*h*t) for h,amp in harm)
    return s*env(n,a,d)
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); acc=0.0
    for i in range(len(x)): acc+= a*(x[i]-acc); y[i]=acc
    return y

# --- chords: Am F C G (2s each), 120bpm
prog=[(57,[57,60,64,67]),(53,[53,57,60,64]),(48,[48,55,60,64]),(55,[55,59,62,67])]
def bar(t): return int(t//2)%4

# pad (Rhodes-ish: sine + soft 2nd harmonic, tremolo)
for b in range(10):
    t0=b*2.0
    if t0>=17.5: break
    root,ch=prog[b%4]
    for m in ch:
        n=int(2.1*SR); t=np.arange(n)/SR
        s=(np.sin(2*np.pi*hz(m+12)*t)+.25*np.sin(2*np.pi*hz(m+12)*2*t))*np.exp(-t/1.6)*(1-np.exp(-t/.01))
        s*= (1+.15*np.sin(2*np.pi*4*t))
        g=.05 if t0<6 else .06
        add(s,t0,g,pan=((m%4)-1.5)*.2)
# final chord C add9 ring
for m in [48,55,60,64,67,74]:
    n=int(2.6*SR); t=np.arange(n)/SR
    s=(np.sin(2*np.pi*hz(m+12)*t)+.2*np.sin(2*np.pi*hz(m+12)*2*t))*np.exp(-t/1.4)*(1-np.exp(-t/.01))
    add(s,17.5,.065,pan=((m%5)-2)*.15)

# kick
def kick():
    n=int(.35*SR); t=np.arange(n)/SR
    f=45+90*np.exp(-t/.03); ph=2*np.cumsum(np.pi*f)/SR
    return np.sin(ph)*np.exp(-t/.12)
K=kick()
for i in range(int(20/BEAT)):
    t=i*BEAT
    if 6.0<=t<17.5: add(K,t,.55)
    elif 3.5<=t<6.0 and i%2==0: add(K,t,.3)
add(K,17.5,.6)
# hats (offbeat), filtered noise
def hat(d=.05):
    n=int(d*SR); x=rng.standard_normal(n); x=x-lp(x,.5); return x*np.exp(-np.arange(n)/SR/.015)
H=hat()
for i in range(int(20/BEAT)):
    t=i*BEAT+BEAT/2
    if 3.5<=t<17.5: add(H,t,.05 if t>=6 else .03, pan=.3)
    if 6<=t<17.5: add(H,t-BEAT/4,.018,pan=-.3)
# bass
for i in range(int(20/BEAT)):
    t=i*BEAT
    if 6.0<=t<17.5:
        root=prog[bar(t)][0]-12
        n=int(.42*SR); tt=np.arange(n)/SR
        s=np.tanh(1.5*np.sin(2*np.pi*hz(root)*tt))*np.exp(-tt/.25)*(1-np.exp(-tt/.005))
        add(s,t+BEAT/2 if i%2 else t, .16)
add(np.sin(2*np.pi*hz(36)*np.arange(int(2.4*SR))/SR)*np.exp(-np.arange(int(2.4*SR))/SR/.9),17.5,.2)

# pluck arp in groove
arp=[0,2,1,3]
for i in range(int(20/(BEAT/2))):
    t=i*BEAT/2
    if 9.0<=t<17.5:
        ch=prog[bar(t)][1]; m=ch[arp[i%4]]+24
        add(tone(hz(m),.3,.002,.09,((1,1),(2,.3),(3,.1))),t,.028,pan=.4 if i%2 else -.4)

# --- SFX (in key)
def blip(m,g=.07,pan=0,t0=0): add(tone(hz(m),.25,.002,.06,((1,1),(2,.2))),t0,g,pan)
def click(t0,g=.12):
    n=int(.03*SR); x=rng.standard_normal(n); x=lp(x,.35)*np.exp(-np.arange(n)/SR/.004); add(x,t0,g)
def whoosh(t0,d,g=.1):
    n=int(d*SR); x=rng.standard_normal(n); t=np.arange(n)/SR
    e=np.sin(np.pi*t/d)**2; y=lp(x,.08)*e; add(y,t0,g)
# S1 clock tick-tock + note pops
for k in range(7): click(0.05+k*0.5, .05)
for k,m in enumerate([76,79,81,84]): blip(m,.075,pan=.35,t0=.55+k*.48+.05)
# S2 list items + thud
for k in range(6): click(3.5+.25+k*.17+.05,.08)
add(K,3.5+1.55,.35)
# S3 whoosh into bands, hit on reveal
whoosh(6.25,.55,.12); whoosh(7.25,.5,.09)
add(K,7.7,.5)
for m in [69,76]: add(tone(hz(m),1.2,.003,.5,((1,1),(2,.15))),7.72,.05)
# S4 ticks rising A C D E G
for k,m in enumerate([81,84,86,88,91]): blip(m,.06,pan=.35,t0=9+.8+k*.34)
# S5 counter ticks + chime
for k in range(6): click(12+.95+k*.8/6,.06)
for m in [84,88,91]: add(tone(hz(m),1.0,.003,.4,((1,1),(2,.1))),12+1.75,.035)
# S6 clicks
click(15+.92,.16); click(15+2.0,.16); whoosh(15+1.12,.35,.05)
# S7 button press
click(17.5+1.6,.12); blip(88,.05,0,17.5+1.62)

# reverb (FFT convolution with decaying noise)
ir_n=int(1.6*SR); ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR/.45); ir=lp(ir,.25); ir/=np.sqrt((ir**2).sum())
def conv(x):
    m=len(x)+ir_n; F=1<<(m-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x,F)*np.fft.rfft(ir,F),F)[:len(x)]
L=L+.18*conv(L); R=R+.18*conv(R)
# master: gentle comp/limit, fade out
mix=np.stack([L,R])
mix=np.tanh(mix*1.4)/1.4
mix*= .89/np.abs(mix).max()
fo=int(.5*SR); mix[:,-fo:]*=np.linspace(1,0,fo)
fi=int(.02*SR); mix[:,:fi]*=np.linspace(0,1,fi)
pcm=(mix.T*32767).astype(np.int16)
w=wave.open('audio.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes()); w.close()
print('ok')
