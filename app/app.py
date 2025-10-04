from flask import Flask, Response, render_template, request, jsonify
import os
import asyncio
import threading
from concurrent.futures import TimeoutError as FuturesTimeout
from .camera import Camera

app = Flask(__name__)

# Single global camera instance
camera = Camera(0)
# Lazy-created microphone track for WebRTC audio (initialized in /rtc/offer)
mic_track = None

# Background asyncio loop for aiortc
_rtc_loop = None
_rtc_thread = None
_peers = set()


def _ensure_rtc_loop():
    global _rtc_loop, _rtc_thread
    if _rtc_loop is not None:
        return _rtc_loop
    loop = asyncio.new_event_loop()

    def _runner():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    t = threading.Thread(target=_runner, daemon=True)
    t.start()
    _rtc_loop = loop
    _rtc_thread = t
    return loop


def _run_on_rtc_loop(coro):
    loop = _ensure_rtc_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop)

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
    try:
        old.stop()
    except Exception:
        pass
    return jsonify({"ok": True, "src": src})

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


@app.route('/rtc/offer', methods=['POST'])
def rtc_offer():
    # Import aiortc lazily so the app still works without aiortc until AV is enabled
    from aiortc import RTCPeerConnection
    from aiortc.contrib.media import MediaBlackhole
    from aiortc import RTCSessionDescription
    # Import our tracks lazily
    from .audio import MicrophoneAudioTrack
    from .webrtc import CameraVideoTrack

    global mic_track
    if mic_track is None:
        mic_track = MicrophoneAudioTrack()

    offer = request.get_json(force=True, silent=False)
    if not offer or 'sdp' not in offer or 'type' not in offer:
        return jsonify({"ok": False, "error": "Invalid offer"}), 400

    async def handle_offer(offer_dict):
        pc = RTCPeerConnection()
        _peers.add(pc)

        # We don't consume incoming media; sink to Blackhole if remote sends anything
        media_sink = MediaBlackhole()

        @pc.on("track")
        async def on_track(track):
            await media_sink.start()

            @track.on("ended")
            async def on_ended():
                await media_sink.stop()

        # Add microphone and camera tracks to send AV to the browser
        pc.addTrack(mic_track)
        pc.addTrack(CameraVideoTrack(camera))

        # Apply remote offer and generate answer
        rd = RTCSessionDescription(sdp=offer_dict['sdp'], type=offer_dict['type'])
        await pc.setRemoteDescription(rd)
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        # Give a brief moment for ICE candidates to gather
        await asyncio.sleep(0.2)
        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    fut = _run_on_rtc_loop(handle_offer(offer))
    try:
        result = fut.result(timeout=10)
    except FuturesTimeout:
        return jsonify({"ok": False, "error": "RTC offer handling timed out"}), 504
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
    return jsonify(result)


if __name__ == '__main__':
    # Configure via env: HOST and PORT; default to localhost:5050 for Windows friendliness
    host = os.environ.get('HOST', '127.0.0.1')
    try:
        port = int(os.environ.get('PORT', '5050'))
    except ValueError:
        port = 5050
    app.run(host=host, port=port, debug=False, threaded=True)
