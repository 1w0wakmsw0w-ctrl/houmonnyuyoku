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
import argparse, io, os, sys, glob, re
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
    "その当たり前の願いが、叶えられない日々が続いている方がいます。",
    "在宅での入浴は、単なる清潔ケアではありません。",
    "温かいお湯に浸かるその時間が、その人の生きる意欲を支えています。",
]
CH1_HOLD = 6           # 1文あたりの表示秒数（読み終えてから次が出るまでの間）
CH1_USE_VIDEO_BG = False   # True にすると冒頭の背景に映像を敷く
CH1_BG_PREFER = ["洗髪", "浴槽完成", "洗体", "玄関前訪問"]   # 背景に使う映像の優先順

def ch1_overlay(n):
    """背景映像の上に重ねる文字（RGBA）。暗幕＋テキスト。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(10, 32, 48, 175))        # 文字を読ませるための暗幕
    y = 380
    f_big, f_sub = F(76), F(46)
    for i, s in enumerate(CH1_LINES[:n]):
        f = f_big if i == 0 else f_sub
        for ln in wrap(d, s, f, W - 360):
            center_text(d, y, ln, f, WHITE if i == 0 else (219, 233, 242))
            y += int(f.size * 1.5)
        if i == 0:
            accent_bar(d, y + 10, MINT); y += 70
        else:
            y += 20
    return img

def ch1_frames():
    """背景映像が無いときの代替（単色背景）"""
    out = []
    for n in range(1, len(CH1_LINES) + 1):
        base = Image.new("RGBA", (W, H), NAVY + (255,))
        out.append(Image.alpha_composite(base, ch1_overlay(n)).convert("RGB"))
    return out

def build_ch1(materials, xfade=0.4):
    """素材があれば映像を背景に、無ければ単色スライドでChapter1を作る"""
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
    from moviepy.video.fx import CrossFadeIn
    pick = None
    for kw in CH1_BG_PREFER:
        hit = [m for m in materials if kw in os.path.basename(m)]
        if hit:
            pick = hit[0]; break
    if not pick:
        return None
    try:
        v = VideoFileClip(pick).without_audio()
    except Exception as ex:
        print("  背景映像の読み込み失敗: %s" % ex); return None
    need = CH1_HOLD * len(CH1_LINES)
    v = v.resized(width=W)
    if v.h < H:
        v = v.resized(height=H)
    if (v.w, v.h) != (W, H):
        v = v.cropped(width=W, height=H, x_center=v.w / 2, y_center=v.h / 2)
    if v.duration < need:                                     # 足りなければ繰り返す
        v = concatenate_videoclips([v] * (int(need // v.duration) + 1))
    v = v.subclipped(0, need)
    print("   Chapter1の背景: %s" % os.path.basename(pick))
    segs = []
    for i in range(len(CH1_LINES)):
        seg = v.subclipped(i * CH1_HOLD, (i + 1) * CH1_HOLD)
        ov = ImageClip(np.array(ch1_overlay(i + 1)), transparent=True).with_duration(seg.duration)
        c = CompositeVideoClip([seg, ov]).with_duration(seg.duration)
        segs.append(c if i == 0 else c.with_effects([CrossFadeIn(xfade)]))
    return concatenate_videoclips(segs, padding=-xfade, method="compose")

# ---------- Chapter 3：訪問の始まりと感染対策（素材動画／字幕） ----------
# 素材はファイル名の昇順に並べ、下の順で字幕を割り当てる。
# 1本のクリップに複数の字幕を置く場合はリストで指定（尺を等分する）。
# 素材のファイル名に含まれる語で字幕を決める。
#   (キーワード, [字幕...], 頭を飛ばす割合, 使う最大秒数)
CH3_RULES = [
    # 具体的な語を先に置く（「背部洗体」が「洗体」に先取りされないように）
    ("玄関前訪問",     ["訪問入浴は、スタッフ3名でご自宅にお伺いするところから始まります。"], 0.0, 12),
    ("入室",           ["ご挨拶をして、その日の体調をうかがいます。"],                     0.0, 12),
    ("前半ダメ",       ["浴槽の準備を進めます。"],                                        0.5, 16),
    ("浴槽完成",       ["外回りで給湯の準備をし、専用浴槽を組み立てます。",
                        "準備が整うまで、およそ15分です。"],                              0.0, 28),
        ("洗髪",           ["お湯に体を預けたまま、洗髪を行います。",
                        "首まで湯に浸かった、いちばん心地よい時間です。"],                 0.0, 34),
    ("洗顔",           ["お顔も、蒸したタオルでやさしく拭きます。"],                       0.0, 18),
    ("背部",           ["姿勢を変えながら、背中まで洗い流します。",
                        "ご自宅の浴槽では届かないところまで、しっかりと。"],               0.0, 32),
    ("洗体",           ["全身をていねいに洗います。",
                        "3名で支えるので、ご本人にもご家族にも負担がかかりません。"],     0.0, 32),
    ("防護服でのケア", ["防護具を着けたまま、通常どおりのケアを行います。"],               0.0, 12),
    ("防護服",         ["ご利用者やご家族に感染の疑いがある場合は、防護具を着用します。"],  0.0, 12),
    ("片付け",         ["入浴後はベッドへお戻しし、機材を片付けて元どおりにします。",
                        "お部屋は、お伺いする前の状態に戻してお返しします。"],             0.0, 28),
]
CH3_FALLBACK = "訪問入浴介護の実際の様子です。"

# 通しで撮った固定カメラの記録。各シーンの素材と内容が重複するため使わない
CH3_EXCLUDE = ["キッチン", "前半ダメ"]   # 頭元はシーン.txtで位置指定して使う

def write_srt(scenes, out_path):
    """シーン.txt から字幕ファイル（.srt）を書き出す。
    DaVinci Resolve などの編集ソフトに読み込んでテロップにできる。"""
    def ts(sec):
        h = int(sec // 3600); m = int(sec % 3600 // 60)
        s2 = int(sec % 60); ms = int(round((sec - int(sec)) * 1000))
        return "%02d:%02d:%02d,%03d" % (h, m, s2, ms)
    marks = []
    for v in scenes.values():
        marks.extend(v)
    marks.sort()
    with io.open(out_path, "w", encoding="utf-8") as f:
        for i, (start, text, length) in enumerate(marks, 1):
            f.write("%d\n%s --> %s\n%s\n\n" % (i, ts(start), ts(start + length), text))
    return len(marks)

def contact_sheet(path, out_path, every=30, cols=5, thumb_w=384):
    """動画を一定間隔で切り出し、時刻入りの一覧画像を作る。
    どの時間に何が映っているかを見ながら シーン.txt を書くために使う。"""
    from moviepy import VideoFileClip
    v = VideoFileClip(path)
    times = list(np.arange(0, v.duration, every))
    if not times:
        times = [0.0]
    shots = []
    for t in times:
        try:
            frame = v.get_frame(min(t, max(0, v.duration - 0.1)))
        except Exception:
            continue
        im = Image.fromarray(frame)
        im = im.resize((thumb_w, int(thumb_w * im.height / im.width)))
        d = ImageDraw.Draw(im)
        label = "%d:%02d" % (int(t) // 60, int(t) % 60)
        f = F(28)
        w = text_w(d, label, f)
        d.rectangle([0, 0, w + 16, 40], fill=(0, 0, 0))
        d.text((8, 4), label, font=f, fill=WHITE)
        shots.append(im)
    v.close()
    if not shots:
        return None
    tw, th = shots[0].size
    rows = (len(shots) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * rows), WHITE)
    for i, im in enumerate(shots):
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(out_path, quality=85)
    return out_path, len(shots), v.duration

def parse_scenes(materials_dir):
    """素材フォルダの「シーン.txt」を読む。書式は次のとおり。

        [キッチン側]          ← 角かっこの中にファイル名の一部
        # これはコメント行
        2:10  専用浴槽を組み立て、お湯を引きます。
        8:30  お湯に体を預けたまま、洗髪を行います。   15   ← 末尾の数字は使う秒数

    戻り値: {ファイル名の一部: [(開始秒, 字幕, 長さ秒), ...]}
    ファイルが無ければ空の辞書。
    """
    path = os.path.join(materials_dir or "", "シーン.txt")
    if not os.path.exists(path):
        return {}
    scenes, key, overlay_keys = {}, None, set()
    for raw in io.open(path, encoding="utf-8-sig"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith("//") or line.startswith("※"):
            continue                                   # コメント行
        m_ov = re.match(r"^[\[［]{2}(.+?)[\]］]{2}$", line)      # [[名前]] = 全編に載せる
        if m_ov:
            key = m_ov.group(1).strip()
            overlay_keys.add(key)
            scenes.setdefault(key, [])
            continue
        m_key = re.match(r"^[\[［](.+?)[\]］]$", line)            # [名前] = 切り出してつなぐ
        if m_key:
            key = m_key.group(1).strip()
            scenes.setdefault(key, [])
            continue
        m = re.match(r"^(\d+):(\d+(?:\.\d+)?)\s+(.+?)(?:\s+(\d+))?$", line)
        if not m or key is None:
            print("  シーン.txt の読めない行: %s" % line)
            continue
        start = int(m.group(1)) * 60 + float(m.group(2))
        scenes[key].append((start, m.group(3).strip(), int(m.group(4) or 12)))
    for k in scenes:
        scenes[k].sort()
    return scenes, overlay_keys

def rule_for(filename):
    """ファイル名に合う字幕・開始位置・最大秒数を返す"""
    for kw, subs, skip, cap in CH3_RULES:
        if kw in filename:
            return subs, skip, cap
    return [CH3_FALLBACK], 0.0, 12

def ch3_title():
    img = canvas(NAVY); d = ImageDraw.Draw(img)
    center_text(d, 400, "CHAPTER 3", F(34), MINT)
    center_text(d, 470, "訪問のはじまり", F(78), WHITE)
    accent_bar(d, 620, MINT)
    return img

def ch3_flow():
    """この後の流れ（15分×3区分）を示すスライド"""
    img = canvas(WHITE); d = ImageDraw.Draw(img)
    center_text(d, 90, "サービス提供時間は45分以内", F(56), NAVY)
    accent_bar(d, 195)
    steps = [("準備・設置", "浴槽の搬入・組立\nバイタル確認と入浴可否の判断"),
             ("入　浴",     "全身浴・洗髪\n入浴中の全身観察"),
             ("片付け・記録", "更衣・保湿ケア／機材の撤収\n記録と関係職種への連絡")]
    bw, gap = 500, 60
    x0 = (W - (bw * 3 + gap * 2)) // 2
    for i, (title, body) in enumerate(steps):
        x = x0 + i * (bw + gap)
        d.rounded_rectangle([x, 290, x + bw, 700], 14, fill=TINTG if i == 1 else (244, 248, 250))
        d.rounded_rectangle([x + bw / 2 - 70, 330, x + bw / 2 + 70, 388], 8, fill=GREEN if i == 1 else NAVY)
        f = F(38)
        d.text((x + bw / 2 - text_w(d, "15分", f) / 2, 340), "15分", font=f, fill=WHITE)
        f = F(48)
        d.text((x + bw / 2 - text_w(d, title, f) / 2, 430), title, font=f, fill=NAVY)
        y = 520
        for ln in body.split("\n"):
            f = F(30)
            d.text((x + bw / 2 - text_w(d, ln, f) / 2, y), ln, font=f, fill=SUB); y += 48
        if i < 2:
            f = F(44)
            d.text((x + bw + gap / 2 - text_w(d, "→", f) / 2, 466), "→", font=f, fill=GRAY)
    center_text(d, 780, "この後、浴槽の設置から入浴、片付けまでを45分以内で行います。", F(38), TEXT)
    return img

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
    subs = [t for _, ts, _, _ in CH3_RULES for t in ts][:6]
    out = []
    for n in range(1, len(subs) + 1):
        img = canvas(NAVY); d = ImageDraw.Draw(img)
        center_text(d, 180, "CHAPTER 3", F(32), MINT)
        center_text(d, 250, "訪問のはじまり", F(72), WHITE)
        accent_bar(d, 380, MINT)
        y = 470
        for t in subs[:n]:
            for ln in wrap(d, t, F(42), W - 400):
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
    """Chapter1の代替（背景映像が使えない場合）"""
    return [(img, CH1_HOLD) for img in ch1_frames()]

def timeline_tail():
    seq = []
    # Ch3：看護師の視点（約60秒）
    for img, d in zip(ch4_frames(), [4, 5, 5, 5, 5, 10]):
        seq.append((img, d))
    return seq

VIDEO_EXT = (".mp4", ".mov", ".m4v", ".avi", ".mts", ".MP4", ".MOV", ".M4V", ".AVI", ".MTS")

def natural_key(path):
    """「2」「10」を数字として並べる（文字列順だと 10 が 2 より前に来るため）"""
    name = os.path.basename(path)
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]

def list_materials(d):
    if not d or not os.path.isdir(d):
        return []
    files = []
    for e in VIDEO_EXT:
        files += glob.glob(os.path.join(d, "*" + e))
    return sorted(set(files), key=natural_key)

def build_ch3(materials, xfade=0.5, mute=True, scenes=None, overlay_keys=None, only_scenes=False):
    """素材動画からChapter3を構成。素材が無ければ None を返す。
    字幕・使う範囲は CH3_RULES（ファイル名のキーワード）で決める。"""
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
    from moviepy.video.fx import CrossFadeIn
    if not materials:
        return None, []
    from moviepy import VideoFileClip as _VFC
    scenes = scenes or {}
    overlay_keys = overlay_keys or set()
    segments, used = [], []

    # [[名前]] … 編集済みの動画を通して流し、指定時刻にテロップだけ載せる
    for key in list(overlay_keys):
        hit = [p for p in materials if key in os.path.basename(p)]
        if not hit:
            print("   シーン.txt の「%s」に合う動画が見つかりません" % key); continue
        path = hit[0]; name = os.path.basename(path)
        try:
            v = _VFC(path)
        except Exception as ex:
            print("  読み込み失敗: %s (%s)" % (name, ex)); continue
        if mute:
            v = v.without_audio()
        v = v.resized(width=W)
        if v.h < H:
            v = v.resized(height=H)
        if (v.w, v.h) != (W, H):
            v = v.cropped(width=W, height=H, x_center=v.w / 2, y_center=v.h / 2)
        layers = [v]
        for start, text, length in scenes.get(key, []):
            if start >= v.duration:
                print("   指定が動画の長さを超えています: %.0f秒" % start); continue
            layers.append(ImageClip(np.array(subtitle_overlay(text)), transparent=True)
                          .with_duration(min(length, v.duration - start)).with_start(start))
            print("   %6.1f秒から %2d秒  %s" % (start, length, text[:26]))
        segments.append(CompositeVideoClip(layers).with_duration(v.duration))
        used.append((name, round(v.duration, 1)))
        print("   %s を通して使用（%d:%02d / テロップ%d本）"
              % (name, int(v.duration) // 60, int(v.duration) % 60, len(scenes.get(key, []))))

    # [名前] … 指定した場面だけを切り出してつなぐ
    for key, marks in scenes.items():
        if key in overlay_keys:
            continue
        hit = [p for p in materials if key in os.path.basename(p)]
        if not hit:
            print("   シーン.txt の「%s」に合う動画が見つかりません" % key)
            continue
        path = hit[0]; name = os.path.basename(path)
        try:
            v = _VFC(path)
        except Exception as ex:
            print("  読み込み失敗: %s (%s)" % (name, ex)); continue
        if mute:
            v = v.without_audio()
        v = v.resized(width=W)
        if v.h < H:
            v = v.resized(height=H)
        if (v.w, v.h) != (W, H):
            v = v.cropped(width=W, height=H, x_center=v.w / 2, y_center=v.h / 2)
        for start, text, length in marks:
            if start >= v.duration:
                print("   指定が動画の長さを超えています: %s %.0f秒" % (name, start)); continue
            seg = v.subclipped(start, min(start + length, v.duration))
            ov = ImageClip(np.array(subtitle_overlay(text)), transparent=True).with_duration(seg.duration)
            segments.append(CompositeVideoClip([seg, ov]).with_duration(seg.duration))
            print("   %-18s %6.1f秒から %2.0f秒  %s" % (name[:18], start, seg.duration, text[:24]))
        used.append((name, sum(m[2] for m in marks)))

    for path in materials:
        name = os.path.basename(path)
        if scenes and any(k in name for k in scenes):
            continue                      # シーン指定済みなので重ねて使わない
        if only_scenes:
            continue                      # --only-scenes：指定したものだけ使う
        if any(k in name for k in CH3_EXCLUDE):
            print("   除外（通しの記録映像）: %s" % name)
            continue
        try:
            v = VideoFileClip(path)
        except Exception as ex:
            print("  読み込み失敗: %s (%s)" % (name, ex))
            continue
        subs, skip, cap = rule_for(name)
        start = v.duration * skip
        end = min(start + cap, v.duration)
        if end - start < 1.0:
            print("  短すぎるため除外: %s" % name)
            continue
        v = v.subclipped(start, end)
        if mute:
            v = v.without_audio()
        v = v.resized(width=W)
        if v.h < H:
            v = v.resized(height=H)
        if (v.w, v.h) != (W, H):
            v = v.cropped(width=W, height=H, x_center=v.w / 2, y_center=v.h / 2)
        part = v.duration / len(subs)
        for j, text in enumerate(subs):
            seg = v.subclipped(j * part, min((j + 1) * part, v.duration))
            ov = ImageClip(np.array(subtitle_overlay(text)), transparent=True).with_duration(seg.duration)
            segments.append(CompositeVideoClip([seg, ov]).with_duration(seg.duration))
        used.append((name, round(v.duration, 1)))
        print("   %-34s %4.1f秒  %s" % (name[:34], v.duration, subs[0][:22]))
    if not segments:
        return None, []
    segments = [c if i == 0 else c.with_effects([CrossFadeIn(xfade)])
                for i, c in enumerate(segments)]
    return concatenate_videoclips(segments, padding=-xfade, method="compose"), used

def find_audio(path, stem, search_dirs):
    """指定パスに無ければ、同じ場所で stem.* を探す。
    Windowsで拡張子が隠れていると bgm.mp3.mp3 になりがちなので、その救済も兼ねる。"""
    if path and os.path.exists(path):
        return path
    exts = (".mp3", ".m4a", ".wav", ".aac", ".mp4", ".mp3.mp3")
    for d in search_dirs:
        if not d or not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            low = f.lower()
            if low.startswith(stem) and low.endswith(exts):
                found = os.path.join(d, f)
                print("   %s を %s として使います" % (f, stem))
                return found
    return None

def add_audio(video, bgm_path, narration_path=None, bgm_volume=0.22):
    """BGMとナレーションを重ねる。ナレーションがある場合はBGMを下げる。"""
    from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips
    tracks, has_bgm, has_nar = [], False, False
    if video.audio:
        tracks.append(video.audio)

    if narration_path and os.path.exists(narration_path):
        nar = AudioFileClip(narration_path)
        if nar.duration > video.duration:
            nar = nar.subclipped(0, video.duration)
        tracks.append(nar)
        has_nar = True
        bgm_volume = min(bgm_volume, 0.10)   # 声を邪魔しない音量まで下げる

    if bgm_path and os.path.exists(bgm_path):
        a = AudioFileClip(bgm_path)
        if a.duration < video.duration:                  # 尺が足りなければ繰り返す
            n = int(video.duration // a.duration) + 1
            a = concatenate_audioclips([AudioFileClip(bgm_path) for _ in range(n)])
        tracks.append(a.subclipped(0, video.duration).with_volume_scaled(bgm_volume))
        has_bgm = True

    if tracks:
        video = video.with_audio(tracks[0] if len(tracks) == 1 else CompositeAudioClip(tracks))
    return video, has_bgm, has_nar

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--materials", default=os.path.expanduser("~/Desktop/動画サンプル"))
    ap.add_argument("--bgm", default=os.path.expanduser("~/Desktop/bgm.mp3"))
    ap.add_argument("--no-bgm", action="store_true", help="BGMを付けない")
    ap.add_argument("--srt", action="store_true",
                    help="動画を作らず、字幕ファイル（.srt）だけを書き出す")
    ap.add_argument("--only-scenes", action="store_true",
                    help="シーン.txt に書いた動画だけを使う")
    ap.add_argument("--narration", default="narration.mp3",
                    help="ナレーションの音声ファイル。あれば重ね、BGMを自動で下げる")
    ap.add_argument("--out", default=os.path.expanduser("~/Desktop/訪問入浴_紹介動画.mp4"))
    ap.add_argument("--preview", action="store_true", help="各スライド1秒の確認用短尺")
    ap.add_argument("--thumbs", action="store_true",
                    help="動画を作らず、素材の内容一覧（時刻入り）を書き出す")
    ap.add_argument("--every", type=int, default=0,
                    help="一覧画像の間隔（秒）。0なら長さに応じて自動（1本あたり約12枚）")
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

    if args.srt:
        sc, _ = parse_scenes(args.materials)
        if not sc:
            print("シーン.txt が見つかりません（動画サンプルフォルダに置いてください）"); return
        out = os.path.join(os.path.dirname(os.path.abspath(args.out)) or ".", "テロップ.srt")
        n = write_srt(sc, out)
        print("字幕ファイルを書き出しました: %s（%d本）" % (out, n))
        print("DaVinci Resolve の「ファイル → 書き出し／読み込み → 字幕」から読み込めます。")
        return

    if args.thumbs:
        if not materials:
            print("素材が見つかりません。")
            return
        for m in materials:
            base = os.path.splitext(os.path.basename(m))[0]
            out = os.path.join(args.materials, base + "_一覧.jpg")
            print("  %s を確認中…" % os.path.basename(m))
            ev = args.every
            if ev <= 0:
                from moviepy import VideoFileClip as _V
                _v = _V(m); ev = max(2, int(_v.duration / 12) or 2); _v.close()
            r = contact_sheet(m, out, every=ev)
            if r:
                print("   → %s（%d枚 / 全体 %d:%02d）"
                      % (os.path.basename(out), r[1], int(r[2]) // 60, int(r[2]) % 60))
        print("\n一覧画像を素材フォルダに書き出しました。")
        print("画像を見ながら シーン.txt に時間を書いてください。")
        return

    def to_clips(seq):
        cs = []
        for img, dur in seq:
            d = 1.0 if args.preview else dur
            cs.append(ImageClip(np.array(img)).with_duration(d))
        return cs

    print("Chapter 1 を生成中…")
    ch1 = None if (args.preview or not CH1_USE_VIDEO_BG) else build_ch1(materials, XF)
    clips = [ch1] if ch1 is not None else to_clips(timeline(args.materials))

    print("Chapter 3 を生成中…")
    scenes, overlay_keys = parse_scenes(args.materials)
    if scenes:
        print("  シーン.txt を読み込みました（%d本 / %d カット）"
              % (len(scenes), sum(len(v) for v in scenes.values())))
    if overlay_keys:
        print("  全編に載せる指定: %s" % "、".join(sorted(overlay_keys)))
    ch3, used = build_ch3(materials, XF, scenes=scenes, overlay_keys=overlay_keys,
                          only_scenes=args.only_scenes or bool(overlay_keys))
    # チャプター見出しは出さず、冒頭から実写へそのままつなぐ
    if ch3 is None:
        used = []
        clips += to_clips([(i, 1.0 if args.preview else 24) for i in ch3_placeholder()])
    else:
        clips.append(ch3)
    clips += to_clips([(ch3_flow(), 22)])

    print("Chapter 4・5・6 を生成中…")
    clips += to_clips(timeline_tail())

    clips = [c if i == 0 else c.with_effects([CrossFadeIn(XF)]) for i, c in enumerate(clips)]
    video = concatenate_videoclips(clips, padding=-XF, method="compose")

    here = os.path.dirname(os.path.abspath(args.out)) or "."
    dirs = [here, os.path.dirname(os.path.abspath(__file__)), args.materials]
    bgm = None if args.no_bgm else find_audio(args.bgm, "bgm", dirs)
    nar = find_audio(args.narration, "narration", dirs)
    if args.no_bgm:
        print("   BGMなしで作成します（--no-bgm）")
    elif not bgm:
        print("   BGMのファイルが見つかりません（bgm.mp3 をこのフォルダに置いてください）")
    video, has_bgm, has_nar = add_audio(video, bgm, nar)
    print("BGM: %s" % ("あり（%s）" % os.path.basename(bgm) if has_bgm else "なし"))
    print("ナレーション: %s" % ("あり（%s）" % os.path.basename(nar) if has_nar else "なし"))

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
    print("ナレーション: %s" % ("あり" if has_nar else "なし"))
    print("出力        : %s" % args.out)

if __name__ == "__main__":
    main()
