@echo off
setlocal

REM Activates venv and runs the app on 127.0.0.1:5050 by default
if not exist app\.venv\Scripts\activate.bat (
  echo Creating virtual environment...
  py -3 -m venv app\.venv 2>nul || python -m venv app\.venv
)

call app\.venv\Scripts\activate.bat

REM Install deps if Flask is missing
pip show flask >nul 2>&1 || pip install -r requirements.txt

set HOST=127.0.0.1
set PORT=5050
python -m app.app

endlocal
