# -*- coding: utf-8 -*-
"""読み上げ.txt から、番号つきの確認用原稿を作る。

    python 確認用原稿を作る.py

「ナレーション原稿_確認用.txt」ができる。番号で修正箇所を伝えるためのもの。
"""
import io, os, re, sys

HEAD = re.compile(r"^#\s*=+\s*([^=].*?)\s*=+\s*$")
TIME = re.compile(r"^(\d{1,2}):([0-5]?\d)(?:\.(\d))?[\s　]+(.+)$")

def main():
    src_path = sys.argv[1] if len(sys.argv) > 1 else "読み上げ.txt"
    if not os.path.exists(src_path):
        sys.exit("原稿が見つかりません: %s" % src_path)
    src = io.open(src_path, encoding="utf-8-sig").read().split("\n")

    body, n = [], 0
    for line in src:
        t = line.strip()
        if not t:
            continue
        h = HEAD.match(t)
        if h:
            body += ["", "", "■ " + h.group(1), "  " + "─" * 62]
            continue
        if t.startswith("#"):
            continue
        m = TIME.match(t)
        if m:
            n += 1
            sec = int(m.group(1)) * 60 + int(m.group(2))
            body.append("  %2d)  %d:%02d   %s" % (n, sec // 60, sec % 60, m.group(4).strip()))

    out = ["=" * 72,
           "  ナレーション原稿　確認用　（全%d行）" % n,
           "=" * 72, "",
           "  直したいところは【番号】で教えてください。", "",
           "    例）12番を「全身を、やさしく洗います。」に変更",
           "        23番は削除",
           "        18番のあとに「○○○○」を追加",
           "        30番、声が映像より早いので2秒うしろにずらして", "",
           "  ・左の数字＝行番号　／　その右＝読み始める時刻",
           "  ・時刻は作るときに自動調整されるので、多少のずれは気にしなくて大丈夫です", "",
           "=" * 72] + body + ["", "=" * 72]

    io.open("ナレーション原稿_確認用.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("ナレーション原稿_確認用.txt を作りました（%d行）" % n)

if __name__ == "__main__":
    main()
