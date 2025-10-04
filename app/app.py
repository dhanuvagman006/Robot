from flask import Flask, Response, render_template, request, jsonify
import os
from .camera import Camera

app = Flask(__name__)

# Single global camera instance
camera = Camera(0)

@app.route('/')
def index():
    return render_template('index.html')


def mjpeg_generator():
    boundary = b'--frame'
    while True:
        frame_bytes = camera.get_jpeg()
        if frame_bytes is None:
            # If no frame yet, skip a beat to avoid hot loop
            import time
            time.sleep(0.01)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/stream')
def stream():
    return Response(mjpeg_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/switch')
def switch():
    global camera
    try:
        src = int(request.args.get('src', '0'))
    except ValueError:
        return jsonify({"ok": False, "error": "src must be an integer"}), 400

    # Swap camera safely
    old = camera
    camera = Camera(src)

@app.route('/message', methods=['POST'])
def message():
    # Accept JSON {"text": "..."} and print to server terminal
    try:
        data = request.get_json(force=True, silent=False)
    except Exception as e:
        return jsonify({"ok": False, "error": "Invalid JSON"}), 400

    text = (data or {}).get('text')
    if not isinstance(text, str) or not text.strip():
        return jsonify({"ok": False, "error": "Missing 'text'"}), 400

    msg = text.strip()
    print(f"[CLIENT MESSAGE] {msg}")
    # Also flush stdout to ensure it appears immediately in terminals
    try:
        import sys
        sys.stdout.flush()
    except Exception:
        pass
    return jsonify({"ok": True})


@app.route('/command', methods=['POST'])
def command():
    try:
        data = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"ok": False, "error": "Invalid JSON"}), 400

    cmd = (data or {}).get('cmd')
    allowed = {"Front", "Back", "Left", "Right", "Stop", "Handshake"}
    if cmd not in allowed:
        return jsonify({"ok": False, "error": "Invalid cmd"}), 400

    print(f"[COMMAND] {cmd}")
    try:
        import sys
        sys.stdout.flush()
    except Exception:
        pass
    return jsonify({"ok": True, "cmd": cmd})
    try:
        old.stop()
    except Exception:
        pass
    return jsonify({"ok": True, "src": src})


if __name__ == '__main__':
    # Configure via env: HOST and PORT; default to localhost:5050 for Windows friendliness
    host = os.environ.get('HOST', '127.0.0.1')
    try:
        port = int(os.environ.get('PORT', '5050'))
    except ValueError:
        port = 5050
    app.run(host=host, port=port, debug=False, threaded=True)
