@echo off
REM Blue Prism OpenAI Bridge Startup Script
REM
REM Usage:
REM   start.bat          - Start in development mode (Flask dev server)
REM   start.bat prod     - Start in production mode (Waitress)
REM
REM First time setup:
REM   1. python -m venv venv
REM   2. venv\Scripts\activate
REM   3. pip install -r requirements.txt
REM   4. Copy config.env.template to config.env
REM   5. Edit config.env with your OpenAI API key
REM   6. Run start.bat

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment. Is Python installed?
        pause
        exit /b 1
    )
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    call venv\Scripts\activate.bat
)

REM Check if config.env exists
if not exist "config.env" (
    echo ERROR: config.env not found!
    echo Please copy config.env.template to config.env and add your OpenAI API key.
    pause
    exit /b 1
)

REM Check for production mode
if "%1"=="prod" (
    echo Starting Blue Prism OpenAI Bridge in PRODUCTION mode...
    echo Server will run on http://127.0.0.1:5050
    echo Press Ctrl+C to stop.
    python -m waitress --host=127.0.0.1 --port=5050 app:app
) else (
    echo Starting Blue Prism OpenAI Bridge in DEVELOPMENT mode...
    echo Server will run on http://127.0.0.1:5050
    echo Press Ctrl+C to stop.
    python app.py
)
