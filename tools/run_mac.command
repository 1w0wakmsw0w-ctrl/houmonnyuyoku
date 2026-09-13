#!/bin/bash
cd "$(dirname "$0")"
echo "============================================"
echo " 訪問入浴 紹介動画の作成"
echo "============================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[エラー] Python3 が見つかりません。"
  echo "https://www.python.org/downloads/ からインストールしてください。"
  read -n 1 -s -r -p "何かキーを押すと閉じます"
  exit 1
fi

echo "必要なライブラリを確認しています（初回のみ数分かかります）..."
python3 -m pip install --quiet --upgrade moviepy pillow numpy imageio-ffmpeg || {
  echo "[エラー] ライブラリの導入に失敗しました。"
  read -n 1 -s -r -p "何かキーを押すと閉じます"
  exit 1
}

echo
echo "動画を作成します。20〜40分ほどかかります。"
echo "このウィンドウは閉じないでください。"
echo
python3 build_video.py \
  --materials "$HOME/Desktop/動画サンプル" \
  --bgm "$HOME/Desktop/bgm.mp3" \
  --out "$HOME/Desktop/訪問入浴_紹介動画.mp4"

echo
echo "終了しました。デスクトップを確認してください。"
read -n 1 -s -r -p "何かキーを押すと閉じます"
