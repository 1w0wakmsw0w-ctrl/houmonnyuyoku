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
    ap.add_argument("--min-gap", dest="min_gap", type=float, default=0.35,
                    help="文と文のあいだに最低限あける秒数")
    ap.add_argument("--no-autofit", action="store_true",
                    help="重なりを自動で直さない（時刻を書いたとおりに置く）")
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
    """時刻どおりに並べた1本を作る。重なりは実際の長さを見て自動で直す。"""
    try:
        from moviepy import AudioFileClip, CompositeAudioClip
    except Exception as ex:
        print("（時刻どおりの1本は作れませんでした: %s）" % ex)
        return

    entries = []   # [開始秒, クリップ, 名前, 長さ]
    for path, st in zip(made, starts):
        if st is None:
            continue
        c = AudioFileClip(path)
        entries.append([float(st), c, os.path.basename(path), c.duration])
    if not entries:
        return
    entries.sort(key=lambda e: e[0])

    # 重なりの自動解消（前に余裕があれば前倒し、なければ後ろへずらす）
    moved = []
    if not a.no_autofit:
        orig = [e[0] for e in entries]
        for i in range(1, len(entries)):
            short = (entries[i - 1][0] + entries[i - 1][3] + a.min_gap) - entries[i][0]
            if short <= 0:
                continue
            prev_end = (entries[i - 2][0] + entries[i - 2][3] + a.min_gap) if i >= 2 else 0.0
            back = max(0.0, min(short, entries[i - 1][0] - prev_end))
            if back:
                entries[i - 1][0] -= back
                short -= back
            if short > 0.02:
                entries[i][0] += short
        for e, o in zip(entries, orig):
            if abs(e[0] - o) > 0.02:
                moved.append((e[2], e[0] - o, mmss(e[0])))

    over = []
    for x, y in zip(entries, entries[1:]):
        if x[0] + x[3] > y[0] + 0.05:
            over.append((x[2], x[0] + x[3] - y[0], mmss(y[0])))

    need = max(e[0] + e[3] for e in entries)
    length = parse_time(a.length) if a.length else None
    total = max(length or 0, need)

    out = os.path.join(made_dir, "narration_timed.mp3")
    clips = [e[1].with_start(e[0]) for e in entries]
    CompositeAudioClip(clips).with_duration(total).write_audiofile(out, fps=44100, logger=None)

    speech = sum(e[3] for e in entries)
    print("\n時刻どおりに並べた1本: %s（%s）" % (out, mmss(total)))
    print("  しゃべっている時間: %s ／ 全体の %d%%" % (mmss(speech), round(speech / total * 100)))
    if moved:
        print("  重なりは自動で直しました: %d か所（最大 %.1f 秒ずらしました）"
              % (len(moved), max(abs(d) for _, d, _ in moved)))
    if over:
        print("\n[注意] まだ重なっている行があります。文を短くしてください。")
        for n, sec, at in over[:12]:
            print("   %s  → %.1f秒ぶん（%s のあたり）" % (n, sec, at))
    else:
        print("  重なりはありません。")
    if length and need > length + 0.5:
        print("  [注意] 最後の文が動画より %.1f 秒はみ出します。" % (need - length))

    try:
        with io.open(os.path.join(made_dir, "調整後の時刻.txt"), "w", encoding="utf-8") as f:
            for e in entries:
                f.write("%-7s %-7s %s\n" % (mmss(e[0]), mmss(e[0] + e[3]), e[2]))
    except Exception:
        pass

    print("\nDaVinci では narration_timed.mp3 を 0:00 に置くだけで合います。")


if __name__ == "__main__":
    main()
