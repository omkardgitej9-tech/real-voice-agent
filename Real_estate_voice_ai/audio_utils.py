import pyaudio
import numpy as np
from typing import Optional, Generator
from utils.logger import logger

class AudioStream:
    def __init__(self, rate: int = 16000, chunk: int = 512, channels: int = 1):
        self.FORMAT   = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE     = rate
        self.CHUNK    = chunk

        self.audio         = pyaudio.PyAudio()
        self.input_stream  = None
        self.output_stream = None
        self.is_recording  = False

    def list_devices(self):
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            logger.info(f"{i}: {info['name']} - {info['maxInputChannels']} in, {info['maxOutputChannels']} out")

    def start_input_stream(self, device_index: Optional[int] = None):
        if self.input_stream is not None:
            self.stop_input_stream()
        try:
            self.input_stream = self.audio.open(
                format             = self.FORMAT,
                channels           = self.CHANNELS,
                rate               = self.RATE,
                input              = True,
                input_device_index = device_index,
                frames_per_buffer  = self.CHUNK,
            )
        except Exception:
            # fallback to default device
            self.input_stream = self.audio.open(
                format            = self.FORMAT,
                channels          = self.CHANNELS,
                rate              = self.RATE,
                input             = True,
                frames_per_buffer = self.CHUNK,
            )
        self.is_recording = True
        logger.info(f"🎙 Input stream started (rate={self.RATE}Hz)")

    def stop_input_stream(self):
        if self.input_stream:
            try:
                self.input_stream.stop_stream()
                self.input_stream.close()
            except Exception as e:
                logger.error(f"Error closing input stream: {e}")
            self.input_stream = None
        self.is_recording = False
        logger.info("🛑 Input stream stopped")

    def read_chunk(self) -> np.ndarray:
        if self.input_stream is None:
            raise RuntimeError("Input stream not started.")
        if not self.is_recording:
            return np.zeros(self.CHUNK, dtype=np.int16)
        try:
            data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
            return np.frombuffer(data, dtype=np.int16)
        except Exception as e:
            logger.error(f"Audio read error: {e}")
            return np.zeros(self.CHUNK, dtype=np.int16)

    def generate_chunks(self) -> Generator[np.ndarray, None, None]:
        if self.input_stream is None:
            self.start_input_stream()
        while self.is_recording:
            yield self.read_chunk()

    def play_audio_chunk(self, audio_chunk: np.ndarray):
        if audio_chunk is None or len(audio_chunk) == 0:
            return
        try:
            if self.output_stream is None:
                self.output_stream = self.audio.open(
                    format            = self.FORMAT,
                    channels          = self.CHANNELS,
                    rate              = self.RATE,
                    output            = True,
                    frames_per_buffer = self.CHUNK,
                )
                logger.info("🔊 Output stream opened")
            self.output_stream.write(audio_chunk.tobytes())
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
            self.output_stream = None  # reset so it reopens next time

    def flush_output(self):
        pass  # no-op — stop/start causes crashes on Windows

    def close(self):
        self.stop_input_stream()
        if self.output_stream:
            try:
                self.output_stream.stop_stream()
                self.output_stream.close()
            except Exception as e:
                logger.error(f"Error closing output stream: {e}")
            self.output_stream = None
        self.audio.terminate()
        logger.info("🔚 Audio system terminated")