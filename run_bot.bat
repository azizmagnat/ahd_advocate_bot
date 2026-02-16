@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not found in PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo checking for 'py' launcher...
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo 'py' launcher is also not found.
        pause
        exit /b
    )
    echo Found 'py' launcher. Using 'py'.
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo Using Python: %PYTHON_CMD%
echo Installing dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b
)

echo Running migrations...
%PYTHON_CMD% -m alembic revision --autogenerate -m "Initial migration"
%PYTHON_CMD% -m alembic upgrade head
if %errorlevel% neq 0 (
    echo Failed to run migrations.
    pause
    exit /b
)

echo Starting bot...
%PYTHON_CMD% main.py
pause
