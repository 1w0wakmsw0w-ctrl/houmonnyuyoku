@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  訪問入浴 紹介動画の作成
echo ============================================
echo.

rem Python を探す（py ランチャー優先）
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
echo 動画を作成します。20〜40分ほどかかります。
echo このウィンドウは閉じないでください。
echo.
%PY% build_video.py ^
  --materials "%USERPROFILE%\Desktop\動画サンプル" ^
  --bgm "%USERPROFILE%\Desktop\bgm.mp3" ^
  --out "%USERPROFILE%\Desktop\訪問入浴_紹介動画.mp4"

echo.
echo 終了しました。デスクトップを確認してください。
pause
