#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""紹介動画用の穏やかなBGMを生成する。

外部のフリー素材を使わず合成するため、著作権の確認が不要。
    python3 make_bgm.py --seconds 400 --out bgm.wav
"""
import argparse, math
import numpy as np

SR = 44100

def midi_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)

def pad_voice(freq, dur, sr=SR, detune=0.12):
    """倍音を抑えた柔らかいパッド音。わずかにデチューンして厚みを出す"""
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    out = np.zeros_like(t)
    # 基音＋控えめな倍音
    for mult, amp in ((1.0, 1.0), (2.0, 0.22), (3.0, 0.08), (4.0, 0.04)):
        for d in (-detune, 0.0, detune):
            out += amp * np.sin(2 * np.pi * (freq * mult + d) * t)
    out /= 3 * 1.34
    # ゆっくりした音量の揺れ（うねり）
    lfo = 1.0 + 0.06 * np.sin(2 * np.pi * 0.07 * t + freq % 3)
    return out * lfo

def env_ad(n, attack, release, sr=SR):
    """長いアタックとリリースの包絡線。クリック音を防ぐ"""
    e = np.ones(n)
    a = min(int(sr * attack), n // 2)
    r = min(int(sr * release), n // 2)
    if a: e[:a] = np.linspace(0, 1, a) ** 2
    if r: e[-r:] = np.linspace(1, 0, r) ** 2
    return e

def bell(freq, dur, sr=SR):
    """まばらに置く鈴のような単音"""
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    y = (np.sin(2 * np.pi * freq * t)
         + 0.35 * np.sin(2 * np.pi * freq * 2 * t)
         + 0.12 * np.sin(2 * np.pi * freq * 3.01 * t))
    return y * np.exp(-t * 1.6) / 1.47

# 進行（--mood で切り替え）
#   calm   穏やかに寄り添う: Cmaj9 → Am7 → Fmaj7 → G6
#   bright 明るく前向き   : F → G → Em → Am（上向きに解決する王道進行）
MOODS = {
    "calm":   {"chords": [[48, 55, 64, 71], [45, 52, 60, 67], [41, 48, 57, 64], [43, 50, 59, 64]],
               "penta":  [72, 74, 76, 79, 81, 84], "dur": 12.0, "xf": 3.0,
               "bell": 0.16, "arp": 0.0},
    "bright": {"chords": [[53, 60, 69, 72], [55, 62, 71, 74], [52, 59, 67, 76], [57, 64, 72, 76]],
               "penta":  [76, 79, 81, 84, 86, 88], "dur": 8.0,  "xf": 2.0,
               "bell": 0.20, "arp": 0.13},
}
CHORDS = MOODS["calm"]["chords"]
PENTA = MOODS["calm"]["penta"]

def build(seconds, seed=7, mood="calm"):
    cfg = MOODS.get(mood, MOODS["calm"])
    chords, penta = cfg["chords"], cfg["penta"]
    rng = np.random.default_rng(seed)
    chord_dur, xf = cfg["dur"], cfg["xf"]
    step = chord_dur - xf
    total = int(SR * seconds)
    buf = np.zeros(total + int(SR * chord_dur))

    # パッド
    i, pos = 0, 0.0
    while pos < seconds:
        notes = chords[i % len(chords)]
        n = int(SR * chord_dur)
        seg = np.zeros(n)
        for m in notes:
            seg += pad_voice(midi_hz(m), chord_dur)
        seg /= len(notes)
        seg *= env_ad(n, xf, xf)
        s = int(SR * pos)
        buf[s:s + n] += seg
        pos += step
        i += 1

    # まばらなメロディ
    pos = 8.0
    while pos < seconds - 4:
        if rng.random() < 0.75:
            note = int(rng.choice(penta))
            d = 3.5
            n = int(SR * d)
            s = int(SR * pos)
            buf[s:s + n] += cfg["bell"] * bell(midi_hz(note), d)
        pos += float(rng.uniform(5.0, 9.0))

    # 明るい版：コード構成音を上へ流すアルペジオ
    if cfg["arp"] > 0:
        pos, i = 0.0, 0
        while pos < seconds - 1:
            notes = chords[int(pos // (chord_dur - xf)) % len(chords)]
            note = notes[i % len(notes)] + 12
            d = 0.9
            n = int(SR * d)
            st = int(SR * pos)
            if st + n <= len(buf):
                buf[st:st + n] += cfg["arp"] * bell(midi_hz(note), d)
            pos += 0.5
            i += 1

    buf = buf[:total]
    # 軽いステレオ（左右をわずかにずらす）
    delay = int(SR * 0.012)
    left = buf
    right = np.concatenate([np.zeros(delay), buf[:-delay]])
    stereo = np.stack([left, right], axis=1)
    # 全体の出入りをなめらかに
    stereo *= env_ad(total, 4.0, 6.0)[:, None]
    peak = np.max(np.abs(stereo))
    if peak > 0:
        stereo = stereo / peak * 0.85
    return stereo

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=400.0)
    ap.add_argument("--out", default="bgm.wav")
    ap.add_argument("--mood", default="calm", choices=list(MOODS),
                    help="calm=穏やか / bright=明るく前向き")
    a = ap.parse_args()
    audio = build(a.seconds, mood=a.mood)
    import wave
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("生成: %s（%s / %.1f秒 / ピーク %.2f）" % (a.out, a.mood, a.seconds, np.max(np.abs(audio))))

if __name__ == "__main__":
    main()
