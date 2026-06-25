import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent.parent.parent


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
conversation_key = os.getenv("conversation_key")
mom_key = os.getenv("mom_key")
reasoning_key = os.getenv("reasoning_key")
summarizer_key = os.getenv("summarizer_key")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment or .env file")
if not conversation_key:
    raise ValueError("conversation_key not found in environment or .env file")
if not mom_key:
    raise ValueError("mom_key not found in environment or .env file")
if not reasoning_key:
    raise ValueError("reasoning_key not found in environment or .env file")
if not summarizer_key:
    raise ValueError("summarizer_key not found in environment or .env file")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")

PIPER_VOICE = str(ROOT_DIR / "src" / "voices" / "en_US-hfc_female-medium.onnx")


RECORDINGS_DIR = ROOT_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

MOM_DIR = ROOT_DIR / "mom"
MOM_DIR.mkdir(exist_ok=True)

LOG_FILE = ROOT_DIR / "call.log"

SAMPLE_RATE = 16000       # for Whisper/VAD (keep this)
PLAYBACK_RATE = 44100     # for speaker output
        # Hz, for VAD/STT/TTS (Piper may use 22050 internally)
CHUNK_SIZE = 512            # frames per buffer
CHANNELS = 1                  # mono

VAD_THRESHOLD = 0.35
VAD_MIN_SPEECH_MS = 180
VAD_MIN_SILENCE_MS = 400

DEBUG = os.getenv("DEBUG", "false").lower() == "true"


ASTERISK_HOST = os.getenv("ASTERISK_HOST", "localhost")
ASTERISK_PORT = int(os.getenv("ASTERISK_PORT", "4573"))
HF_TOKEN = os.getenv("HF_TOKEN", None)