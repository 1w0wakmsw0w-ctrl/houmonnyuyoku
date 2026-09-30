#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""動画から静止画を切り出し、顔が映っていないものを選り分ける。

    pip install moviepy pillow numpy imageio-ffmpeg opencv-python==4.10.0.84
    python 写真を切り出す.py --video 訪問入浴_紹介動画.mp4

「写真」フォルダに
    顔なし/    … 顔が見つからなかったコマ
    要確認/    … 顔が写っている可能性のあるコマ
    一覧.jpg   … 顔なしを並べた確認用の画像
ができる。

※ 顔の自動判定は完全ではありません。マスク・横顔・後ろ姿は
   見落とすことがあります。提供する前に必ず1枚ずつ目で確認してください。
"""
import argparse, glob, os, re, sys

def parse_time(s):
    s = s.strip()
    m = re.match(r"^(\d{1,2}):([0-5]?\d)(?:\.(\d+))?$", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)) + (float("0." + m.group(3)) if m.group(3) else 0)
    return float(s)

def load_detectors():
    """顔検出器を用意する。使えなければ None を返す。"""
    try:
        import cv2
    except ImportError:
        print("（opencv が入っていないため、顔の判定はしません）")
        return None
    here = os.path.dirname(os.path.abspath(__file__))
    dirs = [os.path.join(here, "顔データ"), here,
            getattr(getattr(cv2, "data", None), "haarcascades", "")]
    names = ["haarcascade_frontalface_default.xml",
             "haarcascade_profileface.xml"]
    found = []
    for n in names:
        for d in dirs:
            path = os.path.join(d, n) if d else ""
            if path and os.path.exists(path):
                c = cv2.CascadeClassifier(path)
                if not c.empty():
                    found.append(c)
                    break
    if not found:
        print("（顔の学習データが見つからないため、判定はしません）")
        print("  「顔データ」フォルダを、このファイルと同じ場所に置いてください。")
        return None
    print("顔の判定: 有効（正面・横顔）")
    return (cv2, found)

def has_face(det, frame_rgb):
    cv2, cascades = det
    import numpy as np
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.equalizeHist(gray)
    h = gray.shape[0]
    scale = 720.0 / h if h > 720 else 1.0
    if scale != 1.0:
        gray = cv2.resize(gray, None, fx=scale, fy=scale)
    for c in cascades:
        for g in (gray, cv2.flip(gray, 1)):     # 左右どちらの横顔も見る
            if len(c.detectMultiScale(g, scaleFactor=1.08, minNeighbors=4,
                                      minSize=(28, 28))) > 0:
                return True
    return False

def sharpness(det, frame_rgb):
    """ぼけ具合。大きいほどくっきり。判定できなければ None"""
    if not det:
        return None
    cv2, _ = det
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())

def contact_sheet(paths, out_path, cols=4, thumb_w=480):
    from PIL import Image, ImageDraw
    if not paths:
        return
    ims = []
    for p in paths:
        im = Image.open(p)
        im.thumbnail((thumb_w, thumb_w * 10))
        ims.append((os.path.basename(p), im))
    w = ims[0][1].width
    h = max(im.height for _, im in ims)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 26)), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(ims):
        x, y = (i % cols) * w, (i // cols) * (h + 26)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + h + 6), name, fill=(0, 0, 0))
    sheet.save(out_path, quality=88)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="", help="切り出す動画。省略すると自動で探す")
    ap.add_argument("--every", type=float, default=2.0, help="何秒ごとに切り出すか")
    ap.add_argument("--at", default="", help="時刻を指定して切り出す。例 1:23,2:45")
    ap.add_argument("--outdir", default="写真")
    ap.add_argument("--min-sharp", type=float, default=60.0,
                    help="これより ぼけたコマは捨てる（0で無効）")
    ap.add_argument("--no-detect", action="store_true", help="顔の判定をしない")
    a = ap.parse_args()

    path = a.video
    if not path:
        cands = [p for e in (".mp4", ".mov", ".MP4", ".MOV")
                 for p in glob.glob("*" + e)]
        if not cands:
            sys.exit("動画が見つかりません。--video でファイル名を指定してください。")
        path = max(cands, key=os.path.getsize)
        print("動画: %s（自動で選びました）" % path)
    if not os.path.exists(path):
        sys.exit("動画が見つかりません: %s" % path)

    from moviepy import VideoFileClip
    from PIL import Image
    clip = VideoFileClip(path)
    dur = clip.duration
    print("長さ %d分%02d秒 ／ %dx%d" % (dur // 60, dur % 60, clip.w, clip.h))

    if a.at:
        times = [parse_time(t) for t in a.at.replace("、", ",").split(",") if t.strip()]
    else:
        times = [t for t in frange(1.0, dur - 0.5, a.every)]
    print("切り出す枚数: %d枚" % len(times))

    det = None if a.no_detect else load_detectors()
    ok_dir = os.path.join(a.outdir, "顔なし")
    ng_dir = os.path.join(a.outdir, "要確認")
    os.makedirs(ok_dir, exist_ok=True)
    os.makedirs(ng_dir, exist_ok=True)

    ok, ng, blur = [], 0, 0
    for i, t in enumerate(times, 1):
        if t >= dur:
            continue
        frame = clip.get_frame(t)
        s = sharpness(det, frame)
        if s is not None and a.min_sharp and s < a.min_sharp:
            blur += 1
            continue
        name = "%02d分%02d秒.jpg" % (int(t) // 60, int(t) % 60)
        if det and has_face(det, frame):
            Image.fromarray(frame).save(os.path.join(ng_dir, name), quality=92)
            ng += 1
        else:
            p = os.path.join(ok_dir, name)
            Image.fromarray(frame).save(p, quality=95)
            ok.append(p)
        if i % 20 == 0:
            print("  %d/%d …" % (i, len(times)))
    clip.close()

    if ok:
        contact_sheet(ok[:60], os.path.join(a.outdir, "一覧.jpg"))

    print("\n===== 完了 =====")
    print("顔なし  : %d枚  → %s" % (len(ok), ok_dir))
    print("要確認  : %d枚  → %s" % (ng, ng_dir))
    if blur:
        print("ぼけ    : %d枚（捨てました）" % blur)
    if ok:
        print("一覧    : %s" % os.path.join(a.outdir, "一覧.jpg"))
    print("\n※ 自動の判定は完全ではありません。マスク・横顔・後ろ姿は")
    print("   見落とすことがあります。提供する前に必ず1枚ずつ確認してください。")

def frange(start, stop, step):
    t = start
    while t < stop:
        yield t
        t += step

if __name__ == "__main__":
    main()
