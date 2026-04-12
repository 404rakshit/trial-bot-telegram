@echo off
echo ========================================
echo Weather Alert Bot - MVP Setup
echo ========================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure Python 3.8+ is installed
    pause
    exit /b 1
)
echo ✅ Virtual environment created
echo.

echo [2/4] Activating virtual environment...
call venv\Scripts\activate
echo ✅ Virtual environment activated
echo.

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

echo [4/4] Checking .env file...
if exist .env (
    echo ✅ .env file found
) else (
    echo ⚠️  .env file not found!
    echo Creating template .env file...
    (
        echo # Telegram Bot Configuration
        echo TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
        echo.
        echo # OpenWeatherMap API
        echo OPENWEATHER_API_KEY=your_api_key_here
        echo.
        echo # Application Settings
        echo DEBUG=True
        echo ENV=development
    ) > .env
    echo ✅ Created .env template
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and add your API keys!
    echo   - Get Telegram token: Message @BotFather on Telegram
    echo   - Get Weather API key: https://openweathermap.org/api
    echo.
)

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your API keys
echo 2. Run: python seed_templates.py
echo 3. Run: python main.py
echo 4. In another terminal: python app\bot_polling.py
echo.
echo See README_MVP.md for detailed instructions
echo.
pause
