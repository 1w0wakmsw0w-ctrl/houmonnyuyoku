#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ナレーション原稿から AI 音声（日本語）を作る。

Microsoft の音声合成を使う。無料で、登録も鍵も不要。
インターネットにつながったPCで動く。

    pip install edge-tts
    python make_narration.py

「読み上げ.txt」の1行が1つの音声になる。
行頭に「1:23　本文」のように時刻を書くと、その時刻に配置した
動画尺ぴったりの1本（narration_timed.mp3）も作る。
出力は ナレーション/ フォルダに 01_.mp3、02_.mp3 … と、
それらをつないだ narration.mp3（＋時刻指定があれば narration_timed.mp3）。
"""
import argparse, asyncio, io, os, re, sys

# 日本語の声。--voice で変えられる
VOICES = {
    "ななみ": "ja-JP-NanamiNeural",    # 女性・落ち着いた標準。既定
    "けいた": "ja-JP-KeitaNeural",     # 男性・落ち着いた
    "あおい": "ja-JP-AoiNeural",       # 女性・やや明るい
    "だいち": "ja-JP-DaichiNeural",    # 男性・やや明るい
    "まゆ":   "ja-JP-MayuNeural",      # 女性・やわらかい
    "しおり": "ja-JP-ShioriNeural",    # 女性・落ち着いた
}

TIME_RE = re.compile(r"^(\d{1,2}):([0-5]?\d)(?:\.(\d))?[\s\u3000]+(.+)$")

def parse_time(s):
    """「7:06」「7分6秒」「426」→ 秒。読めなければ None"""
    s = s.strip()
    m = re.match(r"^(\d{1,2}):([0-5]?\d)$", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m = re.match(r"^(\d{1,2})分([0-5]?\d)秒?$", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    try:
        return float(s)
    except ValueError:
        return None

def read_lines(path):
    """[(開始秒 or None, 本文), …] を返す"""
    if not os.path.exists(path):
        sys.exit("原稿が見つかりません: %s" % path)
    out = []
    for raw in io.open(path, encoding="utf-8-sig"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = TIME_RE.match(line)
        if m:
            t = int(m.group(1)) * 60 + int(m.group(2))
            if m.group(3):
                t += int(m.group(3)) / 10.0
            out.append((t, m.group(4).strip()))
        else:
            out.append((None, line))
    return out

async def synth(text, voice, rate, pitch, out_path):
    import edge_tts
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", default="読み上げ.txt")
    ap.add_argument("--outdir", default="ナレーション")
    ap.add_argument("--voice", default="ななみ",
                    help="／".join(VOICES) + " または ja-JP-… の正式名")
    ap.add_argument("--rate", default="-8%", help="話す速さ。例 -15%% でゆっくり")
    ap.add_argument("--pitch", default="+0Hz", help="声の高さ。例 -20Hz で低く")
    ap.add_argument("--gap", type=float, default=1.2, help="つないだ音声の行間（秒）")
    ap.add_argument("--length", default="", help="動画の長さ。例 7:06（時刻指定があるとき使う）")
    a = ap.parse_args()

    voice = VOICES.get(a.voice, a.voice)
    items = read_lines(a.script)
    lines = [t for _, t in items]
    starts = [s for s, _ in items]
    timed = [s for s in starts if s is not None]
    os.makedirs(a.outdir, exist_ok=True)
    print("声: %s ／ 速さ %s ／ %d行" % (voice, a.rate, len(lines)))
    if timed:
        print("時刻の指定: %d行" % len(timed))

    made = []
    for i, text in enumerate(lines, 1):
        name = "%02d_%s.mp3" % (i, re.sub(r"[^\wぁ-んァ-ン一-龥]", "", text)[:12])
        path = os.path.join(a.outdir, name)
        try:
            asyncio.run(synth(text, voice, a.rate, a.pitch, path))
        except Exception as ex:
            sys.exit("音声の生成に失敗しました: %s\n"
                     "インターネットにつながっているか確認してください。" % ex)
        made.append(path)
        print("  %2d/%d  %s" % (i, len(lines), text[:34]))

    # 1本につないだものも作る（行間に無音を入れる）
    try:
        from moviepy import AudioFileClip, concatenate_audioclips, AudioClip
        import numpy as np
        clips = []
        for p in made:
            clips.append(AudioFileClip(p))
            clips.append(AudioClip(lambda t: np.zeros((len(np.atleast_1d(t)), 2)),
                                   duration=a.gap, fps=44100))
        joined = concatenate_audioclips(clips[:-1])
        out = os.path.join(a.outdir, "narration.mp3")
        joined.write_audiofile(out, logger=None)
        print("\nつないだ音声: %s（%d分%02d秒）"
              % (out, int(joined.duration) // 60, int(joined.duration) % 60))
    except Exception as ex:
        print("\n（つなぎ合わせは省略しました: %s）" % ex)

    # 時刻の指定があれば、動画尺ぴったりの1本も作る
    if timed:
        build_timed(made, starts, a, made_dir=a.outdir)

    print("1行ずつの音声は %s/ にあります。" % a.outdir)
    print("DaVinci Resolve に読み込んで、場面に合わせて置いてください。")


def mmss(sec):
    return "%d:%02d" % (int(sec) // 60, int(sec) % 60)

def build_timed(made, starts, a, made_dir):
    """時刻どおりに並べた1本を作る。重なりがあれば知らせる。"""
    try:
        from moviepy import AudioFileClip, CompositeAudioClip
    except Exception as ex:
        print("（時刻どおりの1本は作れませんでした: %s）" % ex)
        return

    clips, spans = [], []
    for path, st in zip(made, starts):
        if st is None:
            continue
        c = AudioFileClip(path)
        spans.append((st, st + c.duration, os.path.basename(path)))
        clips.append(c.with_start(st))
    if not clips:
        return

    spans.sort()
    over = []
    for (s1, e1, n1), (s2, _, n2) in zip(spans, spans[1:]):
        if e1 > s2 + 0.05:
            over.append((n1, e1 - s2, mmss(s2)))

    need = max(e for _, e, _ in spans)
    length = parse_time(a.length) if a.length else None
    total = max(length or 0, need)

    out = os.path.join(made_dir, "narration_timed.mp3")
    CompositeAudioClip(clips).with_duration(total).write_audiofile(out, fps=44100, logger=None)

    speech = sum(e - s for s, e, _ in spans)
    print("\n時刻どおりに並べた1本: %s（%s）" % (out, mmss(total)))
    print("  しゃべっている時間: %s ／ 全体の %d%%" % (mmss(speech), round(speech / total * 100)))
    if over:
        print("\n[注意] 次の行が、その次の行に重なっています。")
        print("       読み上げ.txt の時刻を後ろにずらすか、文を短くしてください。")
        for n, sec, at in over[:12]:
            print("   %s  → %.1f秒ぶん（%s のあたり）" % (n, sec, at))
    else:
        print("  重なりはありません。")
    print("\nDaVinci では narration_timed.mp3 を 0:00 に置くだけで合います。")

if __name__ == "__main__":
    main()
