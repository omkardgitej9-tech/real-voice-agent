from piper import PiperVoice
from pathlib import Path
from typing import Optional, Callable
import numpy as np
from configs import settings
from utils.logger import logger
from utils.audio_utils import resample


class Synthesizer:

    def __init__(self, model_path: Optional[str] = None):

        model_file = Path(model_path) if model_path else Path(settings.PIPER_VOICE)

        if not model_file.exists():
            raise FileNotFoundError(
                f"Voice model not found at: {model_file}"
            )

        self.voice = PiperVoice.load(str(model_file))

        self.voice.config.length_scale = 0.8

        self.sample_rate = self.voice.config.sample_rate
        self._stop_flag = False

    def stop(self) -> None:
        self._stop_flag = True

    def synthesize_stream(self, text: str, chunk_callback: Callable[[np.ndarray], None]) -> None:
       
        if not text or not text.strip():
            return

        self._stop_flag = False

        try:
            for chunk in self.voice.synthesize(text):

                if self._stop_flag:
                    break

                chunk_np = chunk.audio_int16_array

                if not isinstance(chunk_np, np.ndarray):
                    chunk_np = np.asarray(chunk_np, dtype=np.int16)

                # audio.py handles resampling to device rate
                # pass raw TTS audio as-is but normalize to int16
                if not isinstance(chunk_np, np.ndarray):
                    chunk_np = np.asarray(chunk_np, dtype=np.int16)

                chunk_callback(chunk_np)

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")