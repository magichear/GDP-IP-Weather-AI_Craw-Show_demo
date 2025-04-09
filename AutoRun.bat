@echo off
REM Set script path
set SCRIPT_PATH=Main.py

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo Error: Script file not found. Please check the SCRIPT_PATH setting.
    pause
    exit /b 1
)

REM Start the script
echo Starting the program...
python "%SCRIPT_PATH%"

REM Wait for user input before exiting
echo Program has exited.
pause