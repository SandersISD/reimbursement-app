@echo off
REM Startup script for the Reimbursement Management System using UV (Windows)

echo 🚀 Starting Reimbursement Management System...

REM Check if uv is installed
where uv >nul 2>nul
if errorlevel 1 (
    echo ❌ UV is not installed. Please install it first:
    echo powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo Then restart your terminal and try again.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Please run this script from the project root directory ^(where app.py is located^)
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    uv venv
)

REM Install dependencies
echo 📥 Installing dependencies...
uv sync

REM Create uploads directory
echo 📁 Creating uploads directory...
if not exist "uploads" mkdir uploads

REM Initialize database
echo 🗄️ Initializing database...
uv run python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized successfully!')"

echo ✅ Setup complete!
echo.
echo 🌐 Starting the application...
echo 📱 Open your browser to: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the server
echo.

REM Run the application
uv run python app.py
