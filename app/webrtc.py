import asyncio
from typing import Optional

import numpy as np

try:
    import av  # type: ignore
except Exception:  # pragma: no cover
    av = None  # type: ignore

from aiortc import VideoStreamTrack  # type: ignore


class CameraVideoTrack(VideoStreamTrack):
    def __init__(self, camera, fps: int = 30):
        super().__init__()
        self.camera = camera
        self.fps = fps

    async def recv(self):
        # Pull latest frame from camera; if none, wait a short time
        frame = self.camera.get_bgr()
        if frame is None:
            await asyncio.sleep(1.0 / max(self.fps, 1))
            frame = self.camera.get_bgr()
            if frame is None:
                # generate black frame to keep pipeline alive
                frame = np.zeros((480, 640, 3), dtype=np.uint8)

        if av is None:
            raise RuntimeError("PyAV not installed")

        av_frame = av.VideoFrame.from_ndarray(frame, format='bgr24')
        pts, time_base = await self.next_timestamp()
        av_frame.pts = pts
        av_frame.time_base = time_base
        return av_frame
