@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  素材の内容一覧を作る
echo ============================================
echo.
echo 動画サンプルの中の各動画について、30秒ごとの静止画を
echo 並べた「〜_一覧.jpg」を作ります。
echo その画像を見ながら シーン.txt に時間を書いてください。
echo.

if not exist "build_video.py" (
  echo [エラー] build_video.py が同じフォルダにありません。
  pause & exit /b 1
)
if not exist "動画サンプル" (
  echo [エラー] このフォルダの中に「動画サンプル」フォルダがありません。
  pause & exit /b 1
)

set PY=
where py >nul 2>&1 && set PY=py
if "%PY%"=="" ( where python >nul 2>&1 && set PY=python )
if "%PY%"=="" (
  echo [エラー] Python が見つかりません。
  echo https://www.python.org/downloads/ からインストールしてください。
  echo インストール時に「Add python.exe to PATH」にチェックを入れてください。
  pause & exit /b 1
)

echo 必要なライブラリを確認しています（初回のみ数分かかります）...
%PY% -m pip install --quiet --upgrade moviepy pillow numpy imageio-ffmpeg
if errorlevel 1 ( echo [エラー] ライブラリの導入に失敗しました。 & pause & exit /b 1 )

echo.
%PY% build_video.py --thumbs --every 30 --materials "動画サンプル"
echo.
echo 「動画サンプル」フォルダを開いて、_一覧.jpg を確認してください。
pause
