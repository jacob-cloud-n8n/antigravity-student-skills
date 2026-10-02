#!/usr/bin/env python3
"""配樂範本——純程式合成（numpy），讀 render.py 匯出的時間軸 JSON，音效落在畫面事件的同一格。
用法：python3 music.py <timeline.json> <out.wav>（render.py --music 會自動呼叫）
做法：先寫「段落表」（哪一秒是什麼情緒），再把每個畫面事件對上一個音效；最重的一擊只給全片轉折點。
音色是正弦波合成，陽春但無授權問題；要更好的音色見 SKILL.md「工具」節。

"""
import os, sys, json, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
SR = 48000
BEAT = 0.5
DUR = T["DUR"]
N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(n): return np.arange(n) / SR


def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N or i0 < 0: return
    sig = sig[: N - i0] * gain
    L[i0:i0 + len(sig)] += sig * (1 - max(0, pan))
    R[i0:i0 + len(sig)] += sig * (1 + min(0, pan))


def env(n, a=0.005, d=0.3): t = tt(n); return np.minimum(t / a, 1) * np.exp(-t / d)


def pluck(m, dur=0.45, d=0.16):
    n = int(dur * SR); t = tt(n); f = hz(m)
    return (np.sin(2*np.pi*f*t) + 0.35*np.sin(4*np.pi*f*t) + 0.1*np.sin(6*np.pi*f*t)) * env(n, 0.003, d)


def pad(ms, dur, a=0.5, rel=0.5):
    n = int(dur * SR); t = tt(n)
    s = sum(np.sin(2*np.pi*hz(m)*t) + 0.5*np.sin(2*np.pi*hz(m)*1.004*t) for m in ms) / len(ms)
    return s * np.clip(np.minimum(t / a, (dur - t) / rel), 0, 1)


def kick(boom=1.0):
    n = int(0.45 * SR); t = tt(n)
    f = 42 + 100 * np.exp(-t / 0.035)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t / (0.12 * boom))


def noise(dur, d, hp=True):
    n = int(dur * SR); s = rng.standard_normal(n)
    if hp: s = np.diff(s, prepend=0)
    return s * env(n, 0.001, d)


def tick(): return noise(0.04, 0.008) * 0.8 + pluck(96, 0.04, 0.01) * 0.3
def bell(m, dur=1.6, d=0.6):
    n = int(dur * SR); t = tt(n); f = hz(m)
    return (np.sin(2*np.pi*f*t) + 0.4*np.sin(2*np.pi*f*2.76*t)*np.exp(-t/0.2)) * env(n, 0.002, d)


def bass(m, dur):
    n = int(dur * SR); t = tt(n)
    return np.tanh(1.6*np.sin(2*np.pi*hz(m)*t)) * np.minimum(t/0.01, 1) * np.exp(-t/(dur*0.8))


def glide(m0, m1, dur):
    n = int(dur * SR); t = tt(n); f = hz(m0) * (hz(m1)/hz(m0)) ** (t/dur)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.clip(np.minimum(t/0.02, (dur-t)/0.1), 0, 1)


def sweep(dur):       # 掃描：帶通雜訊由低到高
    n = int(dur * SR); s = rng.standard_normal(n); out = np.zeros(n); y = 0.0
    for i in range(n):
        a = 0.02 + 0.5 * i / n; y += a * (s[i] - y); out[i] = y
    return (out - np.convolve(out, np.ones(20)/20, 'same')) * np.sin(np.pi * tt(n) / dur)


def riser(dur):
    n = int(dur * SR); t = tt(n)
    return (rng.standard_normal(n) * 0.5 + glide(50, 74, dur)) * (t / dur) ** 2


def groove(t0, t1, root, chord, full=True, arp=True, kgain=0.55):
    nb = int(round((t1 - t0) / BEAT))
    for b in range(nb):
        tb = t0 + b * BEAT
        if full or b % 2 == 0: add(kick(), tb, kgain)
        if full: add(noise(0.05, 0.015), tb + BEAT/2, 0.05, pan=0.4)
        add(bass(root - 12, BEAT * 0.9), tb, 0.15 if b % 2 == 0 else 0.09)
        if arp:
            for e in range(2):
                add(pluck(chord[(b*2 + e) % 3] + 12, 0.35), tb + e*BEAT/2, 0.07, pan=0.25 if e else -0.25)


# ---------- 範例段落（依你的 TIMELINE 改寫）----------
# 開場：小調墊底＋每拍一聲滴答
add(pad([50, 57, 62], 4.0), 0, 0.2)
for k in range(8): add(tick(), k * BEAT, 0.3)
# 主體：每個事件一記鐘聲＋律動
for i, t0 in enumerate(T.get("items", [])):
    add(bell(74 + 2 * i), t0, 0.14)
    groove(t0, t0 + 4, 50, [62, 65, 69])
# 轉折：全片最重一擊
if "gate" in T:
    add(kick(3.0), T["gate"], 1.0); add(noise(0.6, 0.18, hp=False), T["gate"], 0.25)
# 行動呼籲
if "cta" in T:
    add(kick(2.0), T["cta"], 0.8); add(bell(77, 2.5, 0.9), T["cta"], 0.18)

fade = np.ones(N); fade[-SR:] = np.linspace(1, 0, SR)
mix = np.stack([L, R], 1) * fade[:, None]
mix = mix / np.abs(mix).max() * 10 ** (-1 / 20)
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print(f"OK {OUT}｜{DUR} 秒")
