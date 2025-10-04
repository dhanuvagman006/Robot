# Live Camera Stream (Flask + OpenCV)

A minimal Python web app that streams your camera to a webpage in real time using MJPEG. Tested on Windows with PowerShell.

## Features
- Live MJPEG stream at `/stream`
- Simple UI at `/` to view the stream
- Switch camera device index at runtime via `/switch?src=<n>`
- Threaded capture to keep UI responsive

## Prereqs
- Python 3.9+ (3.11 recommended)
- A webcam or video capture device

## Setup (Windows)
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run (Windows)

```powershell
# From the repo root
$env:FLASK_APP="app.app"; python -m flask run --host 0.0.0.0 --port 5000
```

Then open http://localhost:5000 in your browser.

Alternatively, run directly:

```powershell
python -m app.app
```

## Setup (Linux)
1. Ensure Python 3.9+ and venv are installed
	- Ubuntu/Debian: `sudo apt update && sudo apt install -y python3 python3-venv python3-pip`
2. Create and activate a venv, then install deps:

```bash
python3 -m venv app/.venv
source app/.venv/bin/activate
pip install -r requirements.txt
```

## Run (Linux)

```bash
# Option A: use the helper script (recommended)
chmod +x run.sh
./run.sh                   # defaults HOST=127.0.0.1 PORT=5050
HOST=0.0.0.0 PORT=8000 ./run.sh   # custom host/port

# Option B: directly run the module
export HOST=127.0.0.1 PORT=5050
python -m app.app
```

## Troubleshooting
- Black image or cannot open camera: try different indices (0, 1, 2...) using the input on the page.
- Device busy: close other apps using the camera.
- Performance: lower JPEG quality or FPS in `app/camera.py` (e.g., quality=70, fps=15).
- If you get DLL load errors for OpenCV on Windows, try installing `opencv-contrib-python` or ensure your Python bitness matches (64-bit Python on 64-bit Windows).
- On Linux, if the camera doesn’t open, ensure `v4l2` is available and your user has permission to access `/dev/video*` (you may need to add your user to the `video` group and re-login: `sudo usermod -aG video $USER`).

## Notes
- The MJPEG approach is simple and widely compatible, but not the most bandwidth efficient. For better efficiency, consider WebRTC or HLS with a media server. This app keeps dependencies minimal and works offline.
