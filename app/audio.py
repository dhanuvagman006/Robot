import asyncio
from fractions import Fraction
from typing import Optional

import numpy as np

try:
    import sounddevice as sd
except Exception:  # pragma: no cover
    sd = None

# Import aiortc/av here; if unavailable, raise only when used
try:  # type: ignore
    import av  # type: ignore
    from aiortc import MediaStreamTrack  # type: ignore
except Exception:  # pragma: no cover
    av = None  # type: ignore
    MediaStreamTrack = object  # type: ignore


class MicrophoneAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self, sample_rate: int = 48000, channels: int = 1, blocksize: int = 960, loop: Optional[asyncio.AbstractEventLoop] = None):
        super().__init__()
        self.sample_rate = int(sample_rate)
        self.channels = int(channels)
        self.blocksize = int(blocksize)
        self._queue = asyncio.Queue(maxsize=10)
        self._ts = 0
        self._stream = None
        self._loop = loop

        if sd:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                blocksize=self.blocksize,
                callback=self._on_audio,
            )
            self._stream.start()

    def _on_audio(self, indata, frames, time, status):  # sounddevice callback (threaded)
        try:
            # Copy to avoid referencing ring buffer memory
            chunk = np.array(indata, copy=True)
            # Drop if queue is full to avoid backpressure
            if self._loop is not None:
                if not self._queue.full():
                    # Thread-safe schedule into asyncio loop
                    self._loop.call_soon_threadsafe(self._queue.put_nowait, chunk)
        except Exception:
            pass

    async def recv(self):
        # If no sounddevice available, generate silence
        if self._stream is None:
            await asyncio.sleep(self.block_duration)
            data = np.zeros((self.blocksize, self.channels), dtype=np.int16)
        else:
            try:
                data = await asyncio.wait_for(self._queue.get(), timeout=self.block_duration * 4)
            except asyncio.TimeoutError:
                data = np.zeros((self.blocksize, self.channels), dtype=np.int16)
            except asyncio.CancelledError:
                raise

        if av is None:
            # Should not happen if /rtc/offer was reachable; but guard anyway
            raise RuntimeError("PyAV not installed")
        frame = av.AudioFrame.from_ndarray(data, format="s16", layout="mono" if self.channels == 1 else "stereo")
        frame.sample_rate = self.sample_rate
        frame.pts = self._ts
        frame.time_base = Fraction(1, self.sample_rate)
        self._ts += data.shape[0]
        return frame

    @property
    def block_duration(self) -> float:
        return float(self.blocksize) / float(self.sample_rate)

    async def stop(self) -> None:  # called by aiortc
        try:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
        finally:
            await super().stop()
