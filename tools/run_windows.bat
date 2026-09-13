@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  訪問入浴 紹介動画の作成
echo ============================================
echo.
echo 作業フォルダ: %~dp0
echo.

if not exist "build_video.py" (
  echo [エラー] build_video.py が同じフォルダにありません。
  echo このファイルと build_video.py を同じ場所に置いてください。
  echo ダウンロード時に build_video ^(1^).py のような名前になっている場合は
  echo build_video.py に名前を変えてください。
  pause
  exit /b 1
)
if not exist "動画サンプル" (
  echo [エラ] このフォルダの中に「動画サンプル」フォルダがありません。
  pause
  exit /b 1
)

set PY=
where py >nul 2>&1 && set PY=py
if "%PY%"=="" ( where python >nul 2>&1 && set PY=python )
if "%PY%"=="" (
  echo [エラー] Python が見つかりません。
  echo https://www.python.org/downloads/ からインストールしてください。
  echo インストール時に「Add python.exe to PATH」に必ずチェックを入れてください。
  pause
  exit /b 1
)

echo 必要なライブラリを確認しています（初回のみ数分かかります）...
%PY% -m pip install --quiet --upgrade moviepy pillow numpy imageio-ffmpeg
if errorlevel 1 (
  echo [エラー] ライブラリの導入に失敗しました。
  pause
  exit /b 1
)

echo.
echo 動画を作成します。30〜60分ほどかかります。
echo このウィンドウは閉じないでください。
echo.
%PY% build_video.py --materials "動画サンプル" --bgm "bgm.mp3" --out "訪問入浴_紹介動画.mp4"

echo.
echo 終了しました。このフォルダの中を確認してください。
pause
