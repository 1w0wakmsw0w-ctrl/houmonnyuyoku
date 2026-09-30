@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  動画から写真を切り出す
echo ============================================
echo.
echo 動画を数秒ごとに静止画にして、顔が映っていないものを
echo 選り分けます。「写真」フォルダにできます。
echo.

if not exist "写真を切り出す.py" (
  echo [エラー] 写真を切り出す.py が同じフォルダにありません。
  pause & exit /b 1
)

set PY=
where py >nul 2>&1 && set PY=py
if "%PY%"=="" ( where python >nul 2>&1 && set PY=python )
if "%PY%"=="" (
  echo [エラー] Python が見つかりません。
  echo https://www.python.org/downloads/ からインストールしてください。
  pause & exit /b 1
)

echo どの動画から切り出しますか。
echo ファイル名を入力してください（そのまま Enter で、いちばん大きい動画）。
echo   例）訪問入浴_紹介動画.mp4
echo.
set VIDEO=
set /p VIDEO=ファイル名:
echo.
echo 何秒ごとに切り出しますか（そのまま Enter で 2秒ごと）。
set EVERY=2
set /p EVERY=秒数:
echo.

echo 必要なものを確認しています（初回のみ数分かかります）...
%PY% -m pip install --quiet --upgrade moviepy pillow numpy imageio-ffmpeg "opencv-python<5"
if errorlevel 1 ( echo [エラー] 導入に失敗しました。 & pause & exit /b 1 )

echo.
if "%VIDEO%"=="" (
  %PY% 写真を切り出す.py --every %EVERY%
) else (
  %PY% 写真を切り出す.py --video "%VIDEO%" --every %EVERY%
)
echo.
echo 「写真」フォルダの中の 一覧.jpg を開いて、使えそうな写真を選んでください。
pause
