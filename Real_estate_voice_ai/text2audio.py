# src/main.py
import time
import numpy as np
import sys
from pathlib import Path
import threading

sys.path.append(str(Path(__file__).parent.parent))

from mainflow.audio import AudioStream
from mainflow.vad import VAD
from mainflow.audio2text import Transcriber
from mainflow.text2audio import Synthesizer
from utils.session import Session
from utils.logger import logger
from configs import settings

from agents.mom_agent import generate_mom
from agents.reasoning_agent import reason_about_user
from agents.summarizer_agent import summarizer_agent


class VoiceAssistant:
    def __init__(self):
        logger.info("Starting Real Estate Voice Assistant...")
        self.audio = AudioStream(
            rate     = settings.SAMPLE_RATE,
            chunk    = settings.CHUNK_SIZE,
            channels = settings.CHANNELS
        )
        self.vad = VAD(
            sample_rate           = settings.SAMPLE_RATE,
            threshold             = settings.VAD_THRESHOLD,
            min_speech_duration_ms= settings.VAD_MIN_SPEECH_MS,
            min_silence_duration_ms=settings.VAD_MIN_SILENCE_MS,
            on_speech_end         = self.on_speech_end
        )
        self.transcriber  = Transcriber()
        self.synthesizer  = Synthesizer()
        call_id           = f"call_{int(time.time())}"
        self.session      = Session(call_id)
        self.session.start_time = time.time()

        self.audio_buffer        = bytearray()
        self.call_active         = True
        self.last_activity_time  = time.time()
        self.max_silence_seconds = 60
        self.reminder_sent       = False
        self.ai_speaking         = False
        self.ai_interrupted      = False
        self._tts_lock           = threading.Lock()

    # ── TTS helper ────────────────────────────────────────────────────────────

    def _speak(self, text: str):
        """Speak text synchronously — safe to call from any thread."""
        with self._tts_lock:
            self.ai_speaking    = True
            self.ai_interrupted = False
            try:
                self.synthesizer.synthesize_stream(text, self.audio.play_audio_chunk)
            except Exception as e:
                logger.error(f"TTS error: {e}")
            finally:
                self.ai_speaking = False
                self.last_activity_time = time.time()

    def _speak_async(self, text: str):
        """Speak text in a background thread."""
        threading.Thread(target=self._speak, args=(text,), daemon=True).start()

    # ── VAD callback ──────────────────────────────────────────────────────────

    def on_speech_end(self):
        if len(self.audio_buffer) == 0:
            return

        logger.info("Processing speech...")
        audio_np = np.frombuffer(bytes(self.audio_buffer), dtype=np.int16).copy()
        self.audio_buffer.clear()

        try:
            user_text = self.transcriber.transcribe_array(audio_np, live=True)
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return

        self.last_activity_time = time.time()

        if not user_text or len(user_text.strip()) <= 1:
            return

        logger.user(user_text)

        self.session.add_user_message(user_text)
        self.session.update_summary(summarizer_agent)

        try:
            logger.info("🤖 Running reasoning agent...")
            reasoning_output = reason_about_user(self.session, user_text)

            final_response = reasoning_output.get("final_response", "")
            end_call_flag  = reasoning_output.get("end_call", False)

            logger.ai(final_response)

            self.session.add_ai_message(final_response, reasoning_output)
            self.session.update_summary(summarizer_agent)

            if self.ai_speaking:
                self.ai_interrupted = True
                self.synthesizer.stop()

            self._speak_async(final_response)

            if end_call_flag:
                time.sleep(3)  # let farewell finish
                self.end_call()

        except Exception as e:
            logger.error(f"Agent failure: {e}")
            self._speak_async("I apologize, I am experiencing a temporary issue. Could you please repeat that?")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        greeting = (
            "Hello, thank you for calling Wifi Estates India. "
            "How may I assist you today?"
        )
        self._speak_async(greeting)
        self.session.add_ai_message(greeting, {
            "intent": "greeting", "sentiment": "neutral",
            "entities": {}, "action_items": [], "decisions": [],
            "business_updates": {}, "lead_stage": "new", "end_call": False
        })

        self.audio.start_input_stream()
        self.last_activity_time = time.time()

        try:
            for chunk in self.audio.generate_chunks():
                if not self.call_active:
                    break

                silence_duration = time.time() - self.last_activity_time

                if silence_duration > 20 and not self.reminder_sent and not self.ai_speaking:
                    self._speak_async("Are you still there? Could you please respond?")
                    self.reminder_sent = True

                if silence_duration > self.max_silence_seconds:
                    logger.system("Call ended due to inactivity")
                    self.end_call()
                    break

                speaking = self.vad.process_chunk(chunk)

                if speaking:
                    self.reminder_sent      = False
                    self.last_activity_time = time.time()

                    if self.ai_speaking:
                        self.ai_interrupted = True
                        self.synthesizer.stop()

                    self.audio_buffer.extend(chunk.tobytes())

        except KeyboardInterrupt:
            self.end_call()

    # ── End call ──────────────────────────────────────────────────────────────

    def end_call(self):
        if not self.call_active:
            return
        self.call_active = False
        logger.system("Call ended")

        farewell = "Thank you for contacting Wifi Estates India. Have a wonderful day."
        self._speak(farewell)  # synchronous — wait for it to finish

        try:
            self.session.update_summary(summarizer_agent)
        except Exception:
            pass

        self.session.business_state["call_status"] = "completed"

        try:
            self.audio.close()
        except Exception as e:
            logger.error(f"Audio close failed: {e}")

        try:
            logger.info("📊 Generating MoM...")
            mom_text = generate_mom(
                session    = self.session,
                start_time = self.session.start_time,
                end_time   = time.time()
            )
            self._save_mom(mom_text)
            self.session.save_to_file(f"mom/{self.session.call_id}_analytics.json")
            logger.info(f"MoM saved | Stage: {self.session.call_stage} | Score: {self.session.business_state.get('lead_score')}")
        except Exception as e:
            logger.error(f"MoM generation failed: {e}")

    def _save_mom(self, mom_text: str):
        from datetime import datetime
        mom_dir   = Path("mom")
        mom_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = mom_dir / f"{self.session.call_id}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(mom_text.strip())
        logger.info(f"📄 MoM saved: {filename}")


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()