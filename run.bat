@echo off
setlocal

REM Prefer Python 3.11 for WebRTC deps; fall back if unavailable
set "PREF_PY=C:\Users\dhanu\AppData\Local\Programs\Python\Python311\python.exe"
if not exist app\.venv\Scripts\python.exe (
  echo Creating virtual environment...
  if exist "%PREF_PY%" (
    "%PREF_PY%" -m venv app\.venv
  ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -m venv app\.venv
  ) else if exist "%ProgramFiles%\Python311\python.exe" (
    "%ProgramFiles%\Python311\python.exe" -m venv app\.venv
  ) else (
    where py >nul 2>&1 && (
      py -3.11 -m venv app\.venv 2>nul || py -3.10 -m venv app\.venv 2>nul || py -3 -m venv app\.venv
    ) || (
      python -m venv app\.venv
    )
  )
)

set VENV_PY=app\.venv\Scripts\python.exe
if not exist "%VENV_PY%" (
  echo ERROR: Virtual environment python not found at %VENV_PY%
  exit /b 1
)

call app\.venv\Scripts\activate.bat

echo Installing/updating dependencies...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Tip: If installation fails on Windows Python 3.13, install Python 3.11 x64 and delete app\.venv, then run this script again.
  exit /b 1
)

set HOST=127.0.0.1
set PORT=5050
"%VENV_PY%" -m app.app

endlocal
