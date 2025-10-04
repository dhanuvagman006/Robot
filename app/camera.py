import cv2
import threading
import time


class Camera:
    def __init__(self, src=0, width=None, height=None, fps=30):
        self.src = src
        self.width = width
        self.height = height
        self.fps = fps

        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None

        self._start()

    def _start(self):
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.fps:
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        target_delay = 1.0 / max(self.fps or 30, 1)
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            # Optional: flip frame horizontally (mirror)
            # frame = cv2.flip(frame, 1)

            # Encode to JPEG once; store encoded bytes to minimize work per client
            ret, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if ret:
                with self.lock:
                    self.frame = buf.tobytes()
            time.sleep(target_delay)

    def get_jpeg(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()

    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass
