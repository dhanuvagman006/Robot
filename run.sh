#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run.sh               # defaults HOST=127.0.0.1 PORT=5050
#   HOST=0.0.0.0 PORT=8000 ./run.sh
#   ./run.sh 0.0.0.0 8000  # host and port as positional args

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/app/.venv"

HOST_DEFAULT="127.0.0.1"
PORT_DEFAULT="5050"

HOST="${1:-${HOST:-$HOST_DEFAULT}}"
PORT="${2:-${PORT:-$PORT_DEFAULT}}"

# Create venv if missing
if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
  echo "[run.sh] Creating virtual environment at app/.venv ..."
  python3 -m venv "$VENV_DIR"
fi

# Activate venv
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Install dependencies if Flask is missing
if ! python -m pip show flask >/dev/null 2>&1; then
  echo "[run.sh] Installing dependencies ..."
  pip install -r "$ROOT_DIR/requirements.txt"
fi

export HOST
export PORT

exec python -m app.app
$env:FLASK_APP="app.app"; D:\Robot\app\.venv\Scripts\python.exe -m flask run --host 127.0.0.1 --port 5050
