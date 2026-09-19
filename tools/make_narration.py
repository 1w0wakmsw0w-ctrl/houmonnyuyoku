#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ナレーション原稿から AI 音声（日本語）を作る。

Microsoft の音声合成を使う。無料で、登録も鍵も不要。
インターネットにつながったPCで動く。

    pip install edge-tts
    python make_narration.py

「読み上げ.txt」の1行が1つの音声になる。
出力は ナレーション/ フォルダに 01_.mp3、02_.mp3 … と、
それらを無音でつないだ narration.mp3。
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

def read_lines(path):
    if not os.path.exists(path):
        sys.exit("原稿が見つかりません: %s" % path)
    out = []
    for raw in io.open(path, encoding="utf-8-sig"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
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
    a = ap.parse_args()

    voice = VOICES.get(a.voice, a.voice)
    lines = read_lines(a.script)
    os.makedirs(a.outdir, exist_ok=True)
    print("声: %s ／ 速さ %s ／ %d行" % (voice, a.rate, len(lines)))

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

    print("1行ずつの音声は %s/ にあります。" % a.outdir)
    print("DaVinci Resolve に読み込んで、場面に合わせて置いてください。")

if __name__ == "__main__":
    main()
