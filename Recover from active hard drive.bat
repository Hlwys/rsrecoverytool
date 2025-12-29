@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs -WorkingDirectory '%SCRIPT_DIR%'"
    exit /b
)

cd /d "%SCRIPT_DIR%"

:: Change the following to replace DRIVE LETTER with for example C: or F:
python search.py DRIVE LETTER
python extract.py DRIVE LETTER output.txt

endlocal
cmd /k