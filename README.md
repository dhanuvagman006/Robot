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

## Setup
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run

```powershell
# From the repo root
$env:FLASK_APP="app.app"; python -m flask run --host 0.0.0.0 --port 5000
```

Then open http://localhost:5000 in your browser.

Alternatively, run directly:

```powershell
python -m app.app
```

## Troubleshooting
- Black image or cannot open camera: try different indices (0, 1, 2...) using the input on the page.
- Device busy: close other apps using the camera.
- Performance: lower JPEG quality or FPS in `app/camera.py` (e.g., quality=70, fps=15).
- If you get DLL load errors for OpenCV on Windows, try installing `opencv-contrib-python` or ensure your Python bitness matches (64-bit Python on 64-bit Windows).

## Notes
- The MJPEG approach is simple and widely compatible, but not the most bandwidth efficient. For better efficiency, consider WebRTC or HLS with a media server. This app keeps dependencies minimal and works offline.
