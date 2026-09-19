@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo  ナレーション（AI音声）を作る
echo ============================================
echo.
echo 「読み上げ.txt」の1行ずつを音声にして、
echo 「ナレーション」フォルダに保存します。
echo.

if not exist "make_narration.py" (
  echo [エラー] make_narration.py が同じフォルダにありません。
  echo ダウンロード時に make_narration ^(1^).py のような名前になっている場合は
  echo make_narration.py に名前を変えてください。
  pause & exit /b 1
)
if not exist "読み上げ.txt" (
  echo [エラー] 読み上げ.txt が同じフォルダにありません。
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

echo 声を選んでください。
echo.
echo   1 … ななみ（女性・落ち着いた／おすすめ）
echo   2 … けいた（男性・落ち着いた）
echo   3 … あおい（女性・やや明るい）
echo   4 … だいち（男性・やや明るい）
echo.
set VOICE=ななみ
set /p SEL=番号を入力して Enter（そのまま Enter でななみ）:
if "%SEL%"=="2" set VOICE=けいた
if "%SEL%"=="3" set VOICE=あおい
if "%SEL%"=="4" set VOICE=だいち
echo.
echo 選んだ声: %VOICE%
echo.

echo 必要なものを確認しています（初回のみ数分かかります）...
%PY% -m pip install --quiet --upgrade edge-tts moviepy
if errorlevel 1 ( echo [エラー] 導入に失敗しました。 & pause & exit /b 1 )

echo.
%PY% make_narration.py --voice %VOICE%
echo.
echo 「ナレーション」フォルダを開いて、音声を確認してください。
echo 気に入らなければ、声を変えてもう一度実行できます。
pause
