@echo off
chcp 65001 > nul
echo ========================================
echo Weather Alert Bot - MVP
echo ========================================
echo.

echo Choose what to start:
echo.
echo 1. API Server (Terminal 1)
echo 2. Telegram Bot (Terminal 2)
echo 3. Run Tests
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto api
if "%choice%"=="2" goto bot
if "%choice%"=="3" goto test
if "%choice%"=="4" exit

:api
echo.
echo Starting API Server...
echo Press Ctrl+C to stop
echo.
call venv\Scripts\activate
python main.py
goto end

:bot
echo.
echo Starting Telegram Bot...
echo Press Ctrl+C to stop
echo.
call venv\Scripts\activate
python bot_polling.py
goto end

:test
echo.
echo Running tests...
echo.
call venv\Scripts\activate
python test_bot.py
echo.
pause
goto end

:end
