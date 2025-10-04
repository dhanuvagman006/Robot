from flask import Flask, Response, render_template, request, jsonify
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
    try:
        old.stop()
    except Exception:
        pass
    return jsonify({"ok": True, "src": src})


if __name__ == '__main__':
    # Use 0.0.0.0 to allow LAN access; debug False for camera stability
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
