import numpy as np
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
from faster_whisper import WhisperModel
from typing import Optional
from configs import settings


class Transcriber:

    def __init__(
        self,
        model_size: str = "large.en",
        device: str = "cpu",
        compute_type: str = "int8",
        language: Optional[str] = None,
    ):
        self.model_size    = model_size
        self.device        = device
        self.compute_type  = compute_type
        self.language      = language

        self.model = WhisperModel(
            settings.WHISPER_MODEL,
            device=device,
            compute_type=compute_type
        )

    def transcribe_array(
        self,
        audio: np.ndarray,
        initial_prompt: Optional[str] = None,
        language: Optional[str] = None,
        live: bool = False,          # True = live mic chunk, False = batch file
    ) -> str:
        if audio.size == 0:
            return ""

        audio_float = audio.astype(np.float32) / 32768.0
        lang        = language if language is not None else self.language

        if live:
            # ── LIVE MIC MODE ─────────────────────────────────────────────────
            # Short chunks — disable vad_filter, relax thresholds so speech
            # is not incorrectly filtered out
            segments, _ = self.model.transcribe(
                audio_float,
                language                  = lang,
                initial_prompt            = initial_prompt,
                beam_size                 = 1,
                best_of                   = 1,
                condition_on_previous_text= False,   # no carry-over for live
                temperature               = 0.0,
                compression_ratio_threshold= 2.4,
                no_speech_threshold       = 0.6,     # relaxed — don't filter short speech
                log_prob_threshold        = -1.5,    # accept uncertain segments
                repetition_penalty        = 1.0,
                vad_filter                = False,   # OFF for live — VAD already done
            )
        else:
            # ── BATCH FILE MODE ───────────────────────────────────────────────
            # Long recordings — stricter settings to avoid hallucination
            segments, _ = self.model.transcribe(
                audio_float,
                language                  = lang,
                initial_prompt            = initial_prompt,
                beam_size                 = 1,
                best_of                   = 1,
                condition_on_previous_text= True,
                temperature               = 0.0,
                compression_ratio_threshold= 2.4,
                no_speech_threshold       = 0.3,
                log_prob_threshold        = -1.0,
                repetition_penalty        = 1.5,
                vad_filter                = True,
                vad_parameters            = dict(min_silence_duration_ms=200),
            )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        )

        return text.strip()