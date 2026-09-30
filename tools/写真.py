# -*- coding: utf-8 -*-
# 動画から写真を切り出し、顔が映っていないものを分ける
import os, sys, cv2
from moviepy import VideoFileClip
from PIL import Image

VIDEO = sys.argv[1] if len(sys.argv) > 1 else "訪問入浴_紹介動画.mp4"
EVERY = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0

d = cv2.data.haarcascades
cascades = [cv2.CascadeClassifier(d + n) for n in
            ("haarcascade_frontalface_default.xml", "haarcascade_profileface.xml")]
cascades = [c for c in cascades if not c.empty()]

def has_face(rgb):
    g = cv2.equalizeHist(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
    g = cv2.resize(g, None, fx=720.0 / g.shape[0], fy=720.0 / g.shape[0])
    for c in cascades:
        for x in (g, cv2.flip(g, 1)):
            if len(c.detectMultiScale(x, 1.08, 4, minSize=(28, 28))):
                return True
    return False

os.makedirs("写真/顔なし", exist_ok=True)
os.makedirs("写真/要確認", exist_ok=True)
clip = VideoFileClip(VIDEO)
print("%s ／ %d分%02d秒 ／ %.0f秒ごと" % (VIDEO, clip.duration // 60, clip.duration % 60, EVERY))

ok = ng = 0
t = 1.0
while t < clip.duration - 0.5:
    f = clip.get_frame(t)
    if cv2.Laplacian(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var() > 60:
        base = os.path.splitext(os.path.basename(VIDEO))[0]
        name = "%s_%02d分%02d秒.jpg" % (base, int(t) // 60, int(t) % 60)
        if cascades and has_face(f):
            Image.fromarray(f).save("写真/要確認/" + name, quality=92); ng += 1
        else:
            Image.fromarray(f).save("写真/顔なし/" + name, quality=95); ok += 1
    t += EVERY
clip.close()
print("顔なし %d枚 ／ 要確認 %d枚" % (ok, ng))
print("※ マスクや横顔は見落とします。渡す前に1枚ずつ確認してください。")
