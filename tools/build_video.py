#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""訪問入浴介護 紹介動画ビルダー

素材動画があるチャプター3はフォルダから読み込み、それ以外は
テキスト・グラフィックのスライドを生成して1本の動画に結合する。

使い方:
    python3 build_video.py                       # 素材なし（Ch3はテキスト代替）
    python3 build_video.py --materials ~/Desktop/動画サンプル \
                           --bgm ~/Desktop/bgm.mp3 \
                           --out ~/Desktop/訪問入浴_紹介動画.mp4
"""
import argparse, os, sys, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30

# 配色（スライド・配布資料と統一）
NAVY   = (26, 82, 118)     # #1A5276
GREEN  = (29, 158, 117)    # #1D9E75
AMBER  = (243, 156, 18)    # #F39C12
GRAY   = (189, 195, 199)   # #BDC3C7
TEXT   = (28, 40, 51)      # #1C2833
SUB    = (86, 101, 115)    # #566573
WHITE  = (255, 255, 255)
MINT   = (126, 226, 188)
TINTG  = (232, 248, 245)   # #E8F8F5
LINE   = (225, 229, 232)

FONT_CANDIDATES = [
    os.path.expanduser("~/Desktop/NotoSansJP-Regular.ttf"),
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]

def find_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                ImageFont.truetype(p, 40)
                return p
            except Exception:
                continue
    sys.exit("日本語フォントが見つかりません。Noto Sans JP を ~/Desktop/NotoSansJP-Regular.ttf に置いてください。")

FONT_PATH = find_font()
_cache = {}
def F(size):
    if size not in _cache:
        _cache[size] = ImageFont.truetype(FONT_PATH, size)
    return _cache[size]

# ---------- 描画ヘルパー ----------
def canvas(bg):
    return Image.new("RGB", (W, H), bg)

def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]

def center_text(d, y, s, f, fill):
    d.text(((W - text_w(d, s, f)) / 2, y), s, font=f, fill=fill)

def wrap(d, s, f, maxw):
    """日本語は文字単位で折り返す"""
    lines, cur = [], ""
    for ch in s:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if text_w(d, cur + ch, f) > maxw and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

def block(d, lines, top, f, fill, lh=1.6, center=True, x=140):
    step = int(f.size * lh)
    for i, ln in enumerate(lines):
        y = top + i * step
        if center:
            center_text(d, y, ln, f, fill)
        else:
            d.text((x, y), ln, font=f, fill=fill)
    return top + len(lines) * step

def accent_bar(d, y, color=GREEN, w=120, h=6):
    d.rounded_rectangle([(W - w) / 2, y, (W + w) / 2, y + h], 3, fill=color)

# ---------- チャプター見出し ----------
def chapter_title(num, name, bg=NAVY, fg=WHITE):
    img = canvas(bg); d = ImageDraw.Draw(img)
    center_text(d, 430, num, F(34), MINT if bg == NAVY else GREEN)
    center_text(d, 500, name, F(84), fg)
    accent_bar(d, 640, MINT if bg == NAVY else GREEN)
    return img

# ---------- Chapter 1：課題提起 ----------
CH1_LINES = [
    "お風呂に入りたい。",
    "その当たり前の願いが、叶えられない方がいます。",
    "在宅での入浴は、単なる清潔ケアではありません。",
    "温かいお湯に浸かるその時間が、その人の生きる意欲を支えています。",
]

def ch1_frames():
    """1行ずつ積み上げて表示"""
    out = []
    for n in range(1, len(CH1_LINES) + 1):
        img = canvas(NAVY); d = ImageDraw.Draw(img)
        # 1行目だけ大きく
        y = 360
        center_text(d, y, CH1_LINES[0], F(78), WHITE)
        y += 150
        accent_bar(d, y, MINT); y += 60
        for s in CH1_LINES[1:n]:
            for ln in wrap(d, s, F(44), W - 400):
                center_text(d, y, ln, F(44), (214, 230, 240))
                y += 72
            y += 16
        out.append(img)
    return out

# ---------- Chapter 2：比較表 ----------
CMP_HEAD = ["項目", "訪問入浴", "デイ入浴", "清拭・部分浴"]
CMP_ROWS = [
    ("自宅で受けられる",     "o", "x", "o"),
    ("全身浴ができる",       "o", "o", "x"),
    ("看護師が同行",         "o", "t", "t"),
    ("重度・寝たきり対応",   "o", "t", "t"),
    ("移動・外出が不要",     "o", "x", "o"),
    ("バイタル・皮膚観察",   "o", "t", "x"),
    ("在宅チームへ情報共有", "o", "o", "o"),
]
MARK = {"o": ("✓", GREEN), "x": ("×", GRAY), "t": ("△", AMBER)}

def cmp_table(n_rows, highlight=False):
    """n_rows 行まで表示した比較表"""
    img = canvas(WHITE); d = ImageDraw.Draw(img)
    center_text(d, 70, "入浴支援サービスの比較", F(56), NAVY)

    tw, x0, y0 = 1500, 210, 200
    colw = [520, 340, 320, 320]
    rowh = 92
    # 訪問入浴列のハイライト帯
    hx = x0 + colw[0]
    d.rectangle([hx, y0, hx + colw[1], y0 + rowh * (len(CMP_ROWS) + 1)], fill=TINTG)
    # ヘッダー
    d.rectangle([x0, y0, x0 + tw, y0 + rowh], fill=NAVY)
    d.rectangle([hx, y0, hx + colw[1], y0 + rowh], fill=GREEN)
    cx = x0
    for i, h in enumerate(CMP_HEAD):
        f = F(36)
        d.text((cx + (colw[i] - text_w(d, h, f)) / 2, y0 + 26), h, font=f, fill=WHITE)
        cx += colw[i]
    # 行
    for r in range(n_rows):
        label, *marks = CMP_ROWS[r]
        ry = y0 + rowh * (r + 1)
        d.line([(x0, ry + rowh), (x0 + tw, ry + rowh)], fill=LINE, width=2)
        d.text((x0 + 28, ry + 26), label, font=F(34), fill=TEXT)
        cx = x0 + colw[0]
        for i, m in enumerate(marks):
            ch, col = MARK[m]
            f = F(46)
            d.text((cx + (colw[i + 1] - text_w(d, ch, f)) / 2, ry + 18), ch, font=f, fill=col)
            cx += colw[i + 1]
    # 凡例
    ly = y0 + rowh * (len(CMP_ROWS) + 1) + 34
    legend = [("✓", GREEN, "対応できる"), ("△", AMBER, "事業所・状態により異なる"), ("×", GRAY, "対応が難しい")]
    lx = x0 + 10
    for ch, col, note in legend:
        d.text((lx, ly), ch, font=F(30), fill=col); lx += 44
        d.text((lx, ly + 4), note, font=F(26), fill=SUB); lx += text_w(d, note, F(26)) + 60
    if highlight:
        d.rounded_rectangle([hx - 6, y0 - 6, hx + colw[1] + 6, y0 + rowh * (len(CMP_ROWS) + 1) + 6],
                            10, outline=GREEN, width=6)
    return img

def ch2_closing():
    img = canvas(WHITE); d = ImageDraw.Draw(img)
    center_text(d, 300, "自宅で・全身浴を・看護師付きで・重度でも", F(64), NAVY)
    accent_bar(d, 430); 
    center_text(d, 500, "この4条件を満たすのは、", F(56), TEXT)
    center_text(d, 600, "訪問入浴だけです。", F(76), GREEN)
    return img

# ---------- Chapter 3：サービスの実際（素材動画／字幕） ----------
CH3_SUBS = [
    "スタッフが到着すると、まず専用浴槽を自宅へ搬入します。",
    "入浴前に、看護師がバイタルサインを確認します。",
    "温かいお湯に体が包まれる瞬間、多くの方が安堵した表情を浮かべます。",
    "「気持ちいい」その一言が、私たちの一番の報酬です。",
]

def subtitle_overlay(text):
    """映像に重ねる字幕帯（RGBA）"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = F(44)
    lines = wrap(d, text, f, W - 300)
    bh = 40 + len(lines) * 66
    d.rectangle([0, H - bh - 60, W, H - 60], fill=(0, 0, 0, 153))
    y = H - bh - 40
    for ln in lines:
        center_text(d, y, ln, f, WHITE); y += 66
    return img

def ch3_placeholder():
    """素材が無い場合の代替スライド"""
    out = []
    for n in range(1, len(CH3_SUBS) + 1):
        img = canvas(NAVY); d = ImageDraw.Draw(img)
        center_text(d, 180, "CHAPTER 3", F(32), MINT)
        center_text(d, 250, "サービスの実際", F(72), WHITE)
        accent_bar(d, 380, MINT)
        y = 470
        for s in CH3_SUBS[:n]:
            for ln in wrap(d, s, F(42), W - 400):
                center_text(d, y, ln, F(42), (214, 230, 240)); y += 66
            y += 20
        out.append(img)
    return out

# ---------- Chapter 4：看護師の視点 ----------
CH4_ITEMS = [
    "褥瘡の早期発見",
    "浮腫・皮膚トラブルのアセスメント",
    "体重変化・栄養状態の把握",
    "主治医・訪問看護師・ケアマネジャーへのタイムリーな情報共有",
]

def ch4_frames():
    out = []
    for n in range(0, len(CH4_ITEMS) + 2):
        img = canvas(NAVY); d = ImageDraw.Draw(img)
        center_text(d, 160, "訪問入浴における看護師の役割", F(66), WHITE)
        accent_bar(d, 290, MINT)
        y = 380
        for s in CH4_ITEMS[:min(n, len(CH4_ITEMS))]:
            d.ellipse([330, y + 18, 352, y + 40], fill=MINT)
            for i, ln in enumerate(wrap(d, s, F(40), W - 660)):
                d.text((390, y), ln, font=F(40), fill=(224, 238, 246)); y += 62
            y += 26
        if n > len(CH4_ITEMS):
            d.rounded_rectangle([240, 830, W - 240, 960], 12, fill=(20, 64, 92))
            center_text(d, 868, "入浴は、全身をくまなく観察できる医療的接触の場です。", F(44), MINT)
        out.append(img)
    return out

# ---------- Chapter 5：利用者・家族の声 ----------
CH5_VOICES = [
    ("「毎週のお風呂が楽しみで、それだけで気持ちが前向きになります」", "— 80代・要介護5 ご利用者"),
    ("「一人では絶対に無理でした。プロに任せることで、私も安心して介護できるようになりました」", "— 70代・ご家族"),
]

def ch5_frames():
    out = []
    for n in range(1, len(CH5_VOICES) + 1):
        img = canvas(WHITE); d = ImageDraw.Draw(img)
        center_text(d, 90, "ご利用者・ご家族の声", F(52), NAVY)
        accent_bar(d, 190)
        y = 360
        for quote, who in CH5_VOICES[:n]:
            lines = wrap(d, quote, F(44), W - 520)
            bh = len(lines) * 72 + 120
            d.rounded_rectangle([220, y - 30, W - 220, y + bh - 60], 14, fill=(244, 248, 250))
            d.rounded_rectangle([220, y - 30, 232, y + bh - 60], 6, fill=GREEN)
            yy = y + 10
            for ln in lines:
                d.text((280, yy), ln, font=F(44), fill=TEXT); yy += 72
            wf = F(32)
            d.text((W - 260 - text_w(d, who, wf), yy + 8), who, font=wf, fill=SUB)
            y += bh + 60
        out.append(img)
    return out

# ---------- Chapter 6：連携のご案内 ----------
ORG, TEL = "アップルハート八幡西訪問入浴センター", "093-695-7766"

def ch6_frames():
    a = canvas(NAVY); d = ImageDraw.Draw(a)
    center_text(d, 380, "「この方、訪問入浴どうかな」と思ったとき、", F(56), WHITE)
    center_text(d, 500, "ぜひお気軽にご相談ください。", F(64), MINT)

    b = canvas(NAVY); d = ImageDraw.Draw(b)
    center_text(d, 200, ORG, F(56), WHITE)
    d.rounded_rectangle([560, 320, W - 560, 430], 10, fill=GREEN)
    center_text(d, 344, "TEL  " + TEL, F(58), WHITE)
    y = 540
    for s in ["私たちは、在宅医療チームの一員として",
              "皆さんと一緒に利用者さんの暮らしを支えたいと考えています。"]:
        center_text(d, y, s, F(46), (214, 230, 240)); y += 80
    return [a, b]

# ---------- タイムライン ----------
# (画像生成関数, 表示秒数) の列。秒数を変えれば尺を調整できる。
def timeline(materials_dir):
    seq = []   # [(PIL.Image, duration)]
    # Ch1：課題提起（約60秒）
    for img, d in zip(ch1_frames(), [12, 14, 16, 18]):
        seq.append((img, d))
    # Ch2：比較・差別化（約120秒）
    seq.append((cmp_table(0), 3))
    for r in range(1, len(CMP_ROWS) + 1):
        seq.append((cmp_table(r), 2.5))
    seq.append((cmp_table(7), 35))
    seq.append((cmp_table(7, highlight=True), 35))
    seq.append((ch2_closing(), 25))
    return seq

def timeline_tail():
    seq = []
    # Ch4：看護師の視点（約60秒）
    for img, d in zip(ch4_frames(), [6, 9, 9, 9, 9, 18]):
        seq.append((img, d))
    # Ch5：利用者・家族の声（約30秒）
    for img, d in zip(ch5_frames(), [13, 17]):
        seq.append((img, d))
    # Ch6：連携のご案内（約30秒）
    for img, d in zip(ch6_frames(), [13, 17]):
        seq.append((img, d))
    return seq

VIDEO_EXT = (".mp4", ".mov", ".m4v", ".avi", ".mts", ".MP4", ".MOV", ".M4V", ".AVI", ".MTS")

def list_materials(d):
    if not d or not os.path.isdir(d):
        return []
    files = []
    for e in VIDEO_EXT:
        files += glob.glob(os.path.join(d, "*" + e))
    return sorted(set(files))

def build_ch3(materials, xfade=0.5):
    """素材動画があればChapter3を構成。無ければ None"""
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
    from moviepy.video.fx import CrossFadeIn, Resize
    if not materials:
        return None, []
    target, used = 120.0, []
    per = max(6.0, target / len(materials))
    clips = []
    for i, path in enumerate(materials):
        try:
            v = VideoFileClip(path)
        except Exception as ex:
            print("  読み込み失敗: %s (%s)" % (os.path.basename(path), ex))
            continue
        take = min(per, v.duration)
        v = v.subclipped(0, take).resized(width=W)
        if v.h < H:
            v = v.resized(height=H)
        v = v.cropped(width=W, height=H, x_center=v.w / 2, y_center=v.h / 2)
        sub = CH3_SUBS[i % len(CH3_SUBS)]
        ov = ImageClip(np.array(subtitle_overlay(sub)), transparent=True).with_duration(v.duration)
        clips.append(CompositeVideoClip([v, ov]).with_duration(v.duration))
        used.append((os.path.basename(path), round(take, 1)))
    if not clips:
        return None, []
    clips = [c if i == 0 else c.with_effects([CrossFadeIn(xfade)]) for i, c in enumerate(clips)]
    return concatenate_videoclips(clips, padding=-xfade, method="compose"), used

def add_bgm(video, bgm_path, volume=0.22):
    from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips
    if not bgm_path or not os.path.exists(bgm_path):
        return video, False
    a = AudioFileClip(bgm_path)
    if a.duration < video.duration:                      # 尺が足りなければ繰り返す
        n = int(video.duration // a.duration) + 1
        a = concatenate_audioclips([AudioFileClip(bgm_path) for _ in range(n)])
    a = a.subclipped(0, video.duration).with_volume_scaled(volume)
    video = video.with_audio(CompositeAudioClip([video.audio, a]) if video.audio else a)
    return video, True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--materials", default=os.path.expanduser("~/Desktop/動画サンプル"))
    ap.add_argument("--bgm", default=os.path.expanduser("~/Desktop/bgm.mp3"))
    ap.add_argument("--out", default=os.path.expanduser("~/Desktop/訪問入浴_紹介動画.mp4"))
    ap.add_argument("--preview", action="store_true", help="各スライド1秒の確認用短尺")
    args = ap.parse_args()

    from moviepy import ImageClip, concatenate_videoclips
    from moviepy.video.fx import CrossFadeIn
    XF = 0.4

    print("フォント: %s" % FONT_PATH)
    materials = list_materials(args.materials)
    print("素材フォルダ: %s" % args.materials)
    print("  検出した動画: %d件%s" % (len(materials),
          "" if materials else "（Chapter3はテキストスライドで代替します）"))
    for m in materials:
        print("   - %s" % os.path.basename(m))

    def to_clips(seq):
        cs = []
        for img, dur in seq:
            d = 1.0 if args.preview else dur
            cs.append(ImageClip(np.array(img)).with_duration(d))
        return cs

    print("Chapter 1・2 を生成中…")
    clips = to_clips(timeline(args.materials))

    print("Chapter 3 を生成中…")
    ch3, used = build_ch3(materials, XF)
    if ch3 is None:
        used = []
        clips += to_clips([(i, 1.0 if args.preview else 30) for i in ch3_placeholder()])
    else:
        clips.append(ch3)

    print("Chapter 4・5・6 を生成中…")
    clips += to_clips(timeline_tail())

    clips = [c if i == 0 else c.with_effects([CrossFadeIn(XF)]) for i, c in enumerate(clips)]
    video = concatenate_videoclips(clips, padding=-XF, method="compose")

    video, has_bgm = add_bgm(video, args.bgm)
    print("BGM: %s" % ("あり（%s）" % os.path.basename(args.bgm) if has_bgm else "なし"))

    total = video.duration
    print("書き出し中… 予定尺 %d:%02d → %s" % (int(total // 60), int(total % 60), args.out))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    video.write_videofile(args.out, fps=FPS, codec="libx264", audio_codec="aac",
                          preset="medium", threads=os.cpu_count() or 4, logger="bar")

    print("\n===== 完了 =====")
    print("総尺        : %d分%02d秒" % (int(total // 60), int(total % 60)))
    print("解像度/fps  : %dx%d / %dfps" % (W, H, FPS))
    print("使用した素材: %s" % (", ".join("%s(%ss)" % u for u in used) if used else "なし（全チャプターを生成スライドで構成）"))
    print("BGM         : %s" % ("あり" if has_bgm else "なし"))
    print("出力        : %s" % args.out)

if __name__ == "__main__":
    main()
