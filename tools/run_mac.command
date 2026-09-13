#!/bin/bash
cd "$(dirname "$0")"
echo "============================================"
echo " 訪問入浴 紹介動画の作成"
echo "============================================"
echo
echo "作業フォルダ: $(pwd)"
echo

pause_exit() { echo; read -n 1 -s -r -p "何かキーを押すと閉じます"; exit "$1"; }

[ -f build_video.py ] || { echo "[エラー] build_video.py が同じフォルダにありません。"; pause_exit 1; }
[ -d 動画サンプル ]  || { echo "[エラー] このフォルダの中に「動画サンプル」フォルダがありません。"; pause_exit 1; }
command -v python3 >/dev/null 2>&1 || {
  echo "[エラー] Python3 が見つかりません。"
  echo "https://www.python.org/downloads/ からインストールしてください。"; pause_exit 1; }

echo "必要なライブラリを確認しています（初回のみ数分かかります）..."
python3 -m pip install --quiet --upgrade moviepy pillow numpy imageio-ffmpeg || {
  echo "[エラー] ライブラリの導入に失敗しました。"; pause_exit 1; }

echo
echo "動画を作成します。30〜60分ほどかかります。"
echo "このウィンドウは閉じないでください。"
echo
python3 build_video.py --materials "動画サンプル" --bgm "bgm.mp3" --out "訪問入浴_紹介動画.mp4"

echo
echo "終了しました。このフォルダの中を確認してください。"
pause_exit 0
