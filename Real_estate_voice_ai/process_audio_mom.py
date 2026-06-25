# process_audio_mom.py
#
# PURPOSE:
#   Given a folder of recorded call audio files (.mp3 / .mp4),
#   this script transcribes each file, runs the reasoning agent
#   over every turn, builds a Session, and generates a MoM report.
#
# USAGE:
#   python process_audio_mom.py --input "C:/path/to/audio/files"
#   python process_audio_mom.py --input "C:/path/to/audio" --file "call.mp3" --lang hi --domain general
#
# OUTPUT:
#   mom/<call_id>_<timestamp>.txt       <- executive MoM report (plain text)
#   mom/<call_id>_analytics.json        <- full session analytics
#
# LANGUAGE:  --lang en | hi | auto (default: auto)
# DOMAIN:    --domain general | realestate (default: general)
#
# SPEAKER DIARIZATION (optional but recommended):
#   pip install pyannote.audio
#   Add HF_TOKEN=hf_xxx to your .env file
#   Accept model terms at:
#     https://huggingface.co/pyannote/speaker-diarization-3.1
#     https://huggingface.co/pyannote/segmentation-3.0

import sys
import time
import json
import argparse
import re
import subprocess
from pathlib import Path
from datetime import datetime
import os
os.environ["HF_HOME"] = "./models"
# -- make sure project root and src/ are on sys.path --------------------------
ROOT = Path(__file__).resolve().parent
SRC  = ROOT / "src"

for p in [str(ROOT), str(SRC)]:
    if p not in sys.path:
        sys.path.insert(0, p)

# -- project imports ----------------------------------------------------------
from src.mainflow.audio2text     import Transcriber
from src.agents.mom_agent        import generate_mom
from src.agents.reasoning_agent  import reason_about_user
from src.agents.summarizer_agent import summarizer_agent
from src.utils.session           import Session
from src.utils.logger            import logger
from src.configs                 import settings

import numpy as np
from google import genai

# -- ffmpeg path (hardcoded so subprocess always finds it) --------------------
FFMPEG_BIN = (
    r"C:\Users\Mohit\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
)

SUPPORTED_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac"}


# ═══════════════════════════════════════════════════════════════════════════════
# REPLACE THESE TWO CONSTANTS IN process_audio_mom.py
# ═══════════════════════════════════════════════════════════════════════════════

GENERIC_REASONING_PROMPT = """
You are an expert conversation analyst. Your job is to deeply analyze a single
turn from a recorded call and extract structured intelligence from it.

You MUST return strict JSON only — no markdown, no backticks, no explanation.

════════════════════════════════════════════════════════
CONTEXT
════════════════════════════════════════════════════════
Conversation Summary So Far:
{summary}

Recent Exchanges:
{recent_context}

Previously Extracted Entities:
{entities}

Current Call State:
{business_state}

Current Call Stage: {call_stage}

════════════════════════════════════════════════════════
CURRENT MESSAGE TO ANALYZE:
"{user_text}"
════════════════════════════════════════════════════════

EXTRACTION INSTRUCTIONS:

intent
  What is the speaker's primary goal or purpose in this message?
  Be specific: e.g. "asking about pricing", "confirming meeting time",
  "expressing dissatisfaction with service", "requesting a callback".

entities
  Extract ALL concrete facts mentioned:
  - People: names, roles, relationships
  - Organizations: company names, departments
  - Dates & Times: deadlines, scheduled events, durations
  - Locations: cities, addresses, regions
  - Numbers: prices, quantities, percentages, budgets
  - Products/Services: specific items discussed
  - Contact Info: phone, email if mentioned
  Use descriptive keys, e.g. {{"budget": "50 lakhs", "location": "Noida", "name": "Rahul"}}

sentiment
  Overall emotional tone of this message.
  Choose exactly one: positive / neutral / hesitant / confused / negative / urgent / excited / frustrated

lead_stage
  Based on ALL context so far, what stage is this lead/conversation at?
  Choose exactly one: new / engaged / interested / needs_followup / negotiating / closed / lost

action_items
  Concrete tasks or follow-ups that arise from this message.
  Each item should be a clear, actionable sentence.
  e.g. ["Send product brochure to Rahul", "Schedule site visit for next Tuesday"]
  Empty list [] if none.

decisions
  Any agreements, commitments, or conclusions reached in this message.
  e.g. ["Customer agreed to visit on Saturday", "Price locked at 45 lakhs"]
  Empty list [] if none.

business_updates
  Key-value pairs of any state that should be updated based on this message.
  Only include fields that changed or were newly established.
  e.g. {{"budget_confirmed": true, "preferred_location": "Sector 62", "follow_up_date": "2026-03-15"}}
  Empty object {{}} if nothing to update.

final_response
  A professional, empathetic 2-3 sentence response that directly addresses
  what the speaker said. Should sound natural and helpful, not robotic.
  Match the language register of the conversation (formal/informal).

end_call
  true ONLY if the conversation is clearly concluding (goodbye, thanks and bye,
  talk later, etc.). false in all other cases.

════════════════════════════════════════════════════════
RETURN EXACTLY THIS JSON STRUCTURE:
════════════════════════════════════════════════════════

{{
    "intent": "",
    "entities": {{}},
    "sentiment": "",
    "lead_stage": "",
    "action_items": [],
    "decisions": [],
    "business_updates": {{}},
    "final_response": "",
    "end_call": false
}}
"""


GENERIC_MOM_PROMPT = """
You are a senior executive assistant with expertise in preparing concise,
accurate, and professional post-call Minutes of Meeting (MoM) reports.

Your reports are read by managers and decision-makers who need clarity fast.
Write with precision. Avoid filler. Every sentence must add value.

════════════════════════════════════════════════════════
CALL METADATA
════════════════════════════════════════════════════════
Date & Time : {date}
Duration    : {duration_minutes:.1f} minutes
Call Stage  : {call_stage}

════════════════════════════════════════════════════════
FULL TRANSCRIPT
════════════════════════════════════════════════════════
{transcript}

════════════════════════════════════════════════════════
STRUCTURED INTELLIGENCE EXTRACTED
════════════════════════════════════════════════════════
Session State  : {business_state}
Action Items   : {action_items}
Decisions Made : {decisions}
Sentiment Arc  : {sentiment_timeline}

════════════════════════════════════════════════════════
INSTRUCTIONS
════════════════════════════════════════════════════════

Generate the MoM report using EXACTLY these 6 sections in this order.
Do not add, remove, or rename any section.

---

EXECUTIVE SUMMARY

Write 4-5 sentences covering:
- Who was on the call and the purpose
- The most important outcomes or conclusions
- The overall tone and engagement level
- What happens next

---

KEY DISCUSSION POINTS

List every significant topic discussed. Each point should be 1-2 sentences
with enough detail to be meaningful without reading the full transcript.
Minimum 3 points if the call had substance.
Use hyphen (-) as bullet symbol.

---

DECISIONS TAKEN

List every decision, agreement, or commitment made during the call.
Each item must be specific and attributable where possible.
e.g. "- Customer confirmed interest in the 3BHK unit at Sector 62"
If no decisions were made, write: No decisions recorded.

---

ACTION ITEMS

List all follow-up tasks with owner and deadline where known.
Format: - [Owner if known] Action description (by Date if mentioned)
e.g. "- Sales team to send pricing sheet by Friday"
If none, write: No immediate action required.

---

SENTIMENT ANALYSIS

Write 3-4 sentences describing:
- The opening tone of the call
- How the sentiment evolved through the conversation
- The closing sentiment
- Overall assessment of the relationship/engagement quality

---

CALL QUALITY NOTES

Write 2-3 sentences noting:
- Any communication gaps, misunderstandings, or unclear points
- Topics that need clarification in the next interaction
- Any red flags or positive signals worth noting
If the call was clear and productive, state that here.

════════════════════════════════════════════════════════
FORMATTING RULES (STRICT)
════════════════════════════════════════════════════════
- Plain text only. No markdown. No asterisks. No bold. No headers with #.
- Section titles in ALL CAPS followed by a blank line.
- Bullet points use hyphen (-) only, one space after hyphen.
- Paragraphs separated by a single blank line.
- Professional tone throughout. No casual language.
- Do not mention "the transcript says" or "based on the data" — write directly.
- If information is genuinely unavailable, say so briefly. Do not fabricate.
"""


# =============================================================================
# 1.  AUDIO LOADING  (via ffmpeg subprocess — no pydub PATH dependency)
# =============================================================================

def load_audio_as_pcm(filepath: Path, target_sr: int = settings.SAMPLE_RATE) -> tuple:
    """
    Decode any audio file to mono int16 PCM at target_sr using ffmpeg directly.
    Applies audio enhancement for low-quality telephone recordings.
    Returns (pcm: np.ndarray, duration_sec: float)
    """
    logger.info(f"Loading audio file: {filepath.name}  (format: {filepath.suffix.lower()})")

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", str(filepath),
        "-ac", "1",                       # mono
        "-ar", str(target_sr),            # resample to 16000 Hz
        "-af", (
            "aresample=resampler=soxr,"   # high quality resampler
            "highpass=f=80,"              # remove low freq rumble
            "lowpass=f=7500,"             # remove high freq noise
            "volume=2.0"                  # boost volume for quiet recordings
        ),
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        "pipe:1"
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300
        )
    except Exception as e:
        raise RuntimeError(f"Could not load '{filepath.name}'.\nError: {e}")

    if result.returncode != 0:
        err = result.stderr.decode(errors="ignore")[-500:]
        raise RuntimeError(f"ffmpeg failed on '{filepath.name}'.\nffmpeg stderr: {err}")

    pcm = np.frombuffer(result.stdout, dtype=np.int16)
    duration_sec = len(pcm) / target_sr
    logger.info(f"Audio loaded — duration: {duration_sec:.1f}s  samples: {len(pcm)}")
    return pcm, duration_sec


# =============================================================================
# 2.  HALLUCINATION DETECTION
# =============================================================================

def is_hallucinated(full_transcript: str) -> bool:
    """
    Detect if Whisper hallucinated (repeating same phrase over and over).
    Returns True if >60% of sentences are identical.
    """
    sentences = [s.strip() for s in re.split(r'[.!?]', full_transcript) if s.strip()]
    if not sentences:
        return False
    most_common       = max(set(sentences), key=sentences.count)
    repetition_ratio  = sentences.count(most_common) / len(sentences)
    if repetition_ratio > 0.6:
        logger.warning(
            f"Hallucination detected — '{most_common[:60]}' "
            f"repeated {sentences.count(most_common)}/{len(sentences)} times."
        )
        return True
    return False


# =============================================================================
# 3.  TRANSCRIPT SEGMENTATION  (fallback when pyannote not available)
# =============================================================================

def split_into_turns(full_transcript: str) -> list:
    """
    Split transcript into conversational turns using smart sentence/phrase boundaries.
    Handles both punctuated and unpunctuated Whisper output.
    """
    # normalize spacing
    text = re.sub(r'\s+', ' ', full_transcript.strip())

    # split on punctuation
    text = re.sub(r'([.!?]+)\s+', r'\1\n', text)

    # split on question starters
    text = re.sub(
        r'\s+((?:what|where|when|how|why|who|is|are|do|does|did|can|could|would|should|have|has)\s)',
        r'\n\1', text, flags=re.IGNORECASE
    )

    # split on common response/conversation starters
    text = re.sub(
        r'\s+((?:yes|no|yeah|okay|ok|sure|right|well|so|but|and|oh|ah|hmm|actually|'
        r'basically|look|listen|sorry|thanks|thank you|hello|hi|bye|goodbye)\s)',
        r'\n\1', text, flags=re.IGNORECASE
    )

    raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
    turns     = []
    buffer    = ""

    for line in raw_lines:
        buffer = (buffer + " " + line).strip() if buffer else line
        if len(buffer.split()) >= 10 or re.search(r'[.!?]$', buffer):
            turns.append(buffer)
            buffer = ""

    if buffer:
        turns.append(buffer)

    # merge very short turns (<4 words) with next turn
    merged = []
    i = 0
    while i < len(turns):
        if len(turns[i].split()) < 4 and i + 1 < len(turns):
            turns[i + 1] = turns[i] + " " + turns[i + 1]
            i += 1
        else:
            merged.append(turns[i])
            i += 1

    logger.info(f"Transcript split into {len(merged)} conversational turns")
    return merged


# =============================================================================
# 4.  SPEAKER DIARIZATION  (pyannote — optional, falls back to split_into_turns)
# =============================================================================

def diarize_and_split(
    pcm: np.ndarray,
    full_transcript: str,
    sample_rate: int = settings.SAMPLE_RATE
) -> list:
    """
    Use pyannote speaker diarization to split transcript by speaker turns.
    Falls back to split_into_turns if pyannote is not installed or HF_TOKEN is missing.

    Requirements:
        pip install pyannote.audio
        HF_TOKEN=hf_xxx in .env
        Accept model terms at huggingface.co/pyannote/speaker-diarization-3.1
    """
    hf_token = getattr(settings, "HF_TOKEN", "")

    if not hf_token:
        logger.warning("HF_TOKEN not set in .env — skipping diarization, using sentence split.")
        return split_into_turns(full_transcript)

    try:
        import torch
        from pyannote.audio import Pipeline

        logger.info("Running speaker diarization (pyannote)...")

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=hf_token
        )

        # convert numpy PCM to torch tensor for pyannote
        waveform   = torch.tensor(pcm, dtype=torch.float32).unsqueeze(0) / 32768.0
        audio_dict = {"waveform": waveform, "sample_rate": sample_rate}

        diarization = pipeline(audio_dict)

        # collect segments: [(start, end, speaker)]
        annotation = diarization.speaker_diarization

        segments = [
            (segment.start, segment.end, speaker)
            for segment, _, speaker in annotation.itertracks(yield_label=True)
        ]

        if not segments:
            logger.warning("Diarization returned no segments — falling back to sentence split.")
            return split_into_turns(full_transcript)

        # distribute transcript words across speaker segments proportionally
        words      = full_transcript.split()
        total_dur  = max(seg[1] for seg in segments) - min(seg[0] for seg in segments)
        turns      = []
        word_idx   = 0

        for i, (start, end, speaker) in enumerate(segments):
            seg_dur    = end - start
            seg_ratio  = (seg_dur / total_dur) if total_dur > 0 else (1.0 / len(segments))
            word_count = max(1, round(len(words) * seg_ratio))
            seg_words  = words[word_idx: word_idx + word_count]
            word_idx  += word_count

            if seg_words:
                turns.append(f"[{speaker}]: {' '.join(seg_words)}")

        # append any remaining words to last turn
        if word_idx < len(words):
            remaining = ' '.join(words[word_idx:])
            if turns:
                turns[-1] += " " + remaining
            else:
                turns.append(remaining)

        unique_speakers = len(set(seg[2] for seg in segments))
        logger.info(
            f"Diarization complete — {unique_speakers} speaker(s) detected, "
            f"{len(turns)} turns"
        )
        return turns

    except ImportError:
        logger.warning(
            "pyannote.audio not installed — falling back to sentence split.\n"
            "To enable speaker diarization, run: pip install pyannote.audio"
        )
        return split_into_turns(full_transcript)

    except Exception as e:
        logger.warning(f"Diarization failed ({e}) — falling back to sentence split.")
        return split_into_turns(full_transcript)


# =============================================================================
# 5.  GENERIC REASONING AGENT  (domain-agnostic)
# =============================================================================

def reason_about_user_generic(session: Session, user_text: str) -> dict:
    """Domain-agnostic reasoning — works for any type of call."""
    client = genai.Client(api_key=settings.reasoning_key)

    prompt = GENERIC_REASONING_PROMPT.format(
        summary        = session.summary,
        recent_context = session.get_context_for_prompt(5),
        entities       = json.dumps(session.entities),
        business_state = json.dumps(session.business_state),
        call_stage     = session.call_stage,
        user_text      = user_text
    )

    try:
        response = client.models.generate_content(
            model   = settings.GEMINI_MODEL,
            contents= prompt,
            config  = {"temperature": 0.2}
        )
        text  = response.text.strip()
        match = re.search(r'\{[\s\S]*\}', text, re.DOTALL)
        if match:
            result   = json.loads(match.group(0))
            defaults = {
                "intent"         : "unknown",
                "entities"       : {},
                "sentiment"      : "neutral",
                "lead_stage"     : session.call_stage,
                "action_items"   : [],
                "decisions"      : [],
                "business_updates": {},
                "final_response" : "",
                "end_call"       : False
            }
            for field, default in defaults.items():
                if field not in result:
                    result[field] = default
            if not isinstance(result.get("end_call"), bool):
                result["end_call"] = False
            return result
    except Exception as e:
        logger.error(f"Generic reasoning failed: {e}")

    return {
        "intent": "unknown", "entities": {}, "sentiment": "neutral",
        "lead_stage": session.call_stage, "action_items": [], "decisions": [],
        "business_updates": {}, "final_response": "", "end_call": False
    }


# =============================================================================
# 6.  GENERIC MoM GENERATOR  (domain-agnostic)
# =============================================================================

def generate_mom_generic(session: Session, start_time: float, end_time: float) -> str:
    """Domain-agnostic MoM generation — works for any type of call."""
    client           = genai.Client(api_key=settings.mom_key)
    duration_minutes = round((end_time - start_time) / 60.0, 2)
    date_str         = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M")
    transcript       = session.get_full_transcript() or "No meaningful conversation captured."

    prompt = GENERIC_MOM_PROMPT.format(
        date             = date_str,
        duration_minutes = duration_minutes,
        transcript       = transcript,
        business_state   = json.dumps(session.business_state, indent=2),
        call_stage       = session.call_stage,
        action_items     = json.dumps(session.action_items, indent=2),
        decisions        = json.dumps(session.decisions, indent=2),
        sentiment_timeline = json.dumps(session.sentiment_timeline, indent=2),
    )

    try:
        response = client.models.generate_content(
            model   = settings.GEMINI_MODEL,
            contents= prompt,
            config  = {"temperature": 0.3}
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Generic MoM generation failed: {e}")
        return "MoM generation failed due to a system error."


# =============================================================================
# 7.  SESSION BUILDER
# =============================================================================

def build_session_from_turns(
    turns     : list,
    call_id   : str,
    start_time: float,
    domain    : str = "general"
) -> Session:
    """
    Feed each transcript turn through the reasoning agent and build a Session.
    domain: "general"     -> generic reasoning (any call type)
            "realestate"  -> real estate reasoning with property knowledge
    """
    session = Session(call_id=call_id, start_time=start_time)
    logger.info(f"Processing {len(turns)} turns | domain: {domain}")

    for i, turn_text in enumerate(turns, 1):
        logger.info(
            f"  Turn {i}/{len(turns)}: "
            f"{turn_text[:80]}{'...' if len(turn_text) > 80 else ''}"
        )

        session.add_user_message(turn_text)
        session.update_summary(summarizer_agent)

        try:
            if domain == "realestate":
                reasoning_output = reason_about_user(session, turn_text)
            else:
                reasoning_output = reason_about_user_generic(session, turn_text)
        except Exception as e:
            logger.error(f"Reasoning agent failed on turn {i}: {e}")
            reasoning_output = {
                "intent"          : "unknown",
                "entities"        : {},
                "sentiment"       : "neutral",
                "lead_stage"      : session.call_stage,
                "action_items"    : [],
                "decisions"       : [],
                "business_updates": {},
                "final_response"  : "",
                "end_call"        : False
            }

        session.add_ai_message(
            reasoning_output.get("final_response", ""),
            reasoning_output
        )
        session.update_summary(summarizer_agent)

        if reasoning_output.get("end_call", False):
            logger.info(f"  end_call signalled at turn {i} — stopping.")
            break

    logger.info(
        f"Session built — Stage: {session.call_stage} | "
        f"Lead Score: {session.business_state.get('lead_score', 0)}"
    )
    return session


# =============================================================================
# 8.  MoM SAVING
# =============================================================================

def save_mom(mom_text: str, call_id: str, start_time: float) -> Path:
    mom_dir   = Path("mom")
    mom_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.fromtimestamp(start_time).strftime("%Y%m%d_%H%M%S")
    filename  = mom_dir / f"{call_id}_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(mom_text.strip())
    logger.info(f"MoM saved: {filename}")
    return filename


def save_analytics(session: Session) -> Path:
    mom_dir        = Path("mom")
    mom_dir.mkdir(parents=True, exist_ok=True)
    analytics_path = mom_dir / f"{session.call_id}_analytics.json"
    session.save_to_file(str(analytics_path))
    logger.info(f"Analytics saved: {analytics_path}")
    return analytics_path


# =============================================================================
# 9.  SINGLE-FILE PROCESSOR
# =============================================================================

def process_audio_file(
    audio_path: Path,
    transcriber: Transcriber,
    lang  : str = "auto",
    domain: str = "general"
) -> dict:
    """
    Full pipeline for one audio file:
      load -> transcribe -> hallucination check -> diarize/split -> reason -> MoM -> save

    lang:   "en" | "hi" | "auto"
    domain: "general" | "realestate"
    """
    start_time = time.time()
    call_id    = f"batch_{audio_path.stem}_{int(start_time)}"

    logger.separator("=", 60)
    logger.info(f"Processing : {audio_path.name}")
    logger.info(f"Call ID    : {call_id}")
    logger.info(f"Language   : {lang}")
    logger.info(f"Domain     : {domain}")
    logger.separator("-", 60)

    # 1. load + enhance audio
    try:
        pcm, duration_sec = load_audio_as_pcm(audio_path)
    except Exception as e:
        logger.error(str(e))
        return {"file": audio_path.name, "status": "failed", "error": str(e)}

    # 2. transcribe
    logger.info("Transcribing audio (this may take a moment)...")
    try:
        whisper_lang    = None if lang == "auto" else lang
        full_transcript = transcriber.transcribe_array(pcm, language=whisper_lang)
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return {"file": audio_path.name, "status": "failed", "error": str(e)}

    # 3. validate transcript
    if not full_transcript.strip():
        logger.warning("Transcription returned empty text — skipping file.")
        return {"file": audio_path.name, "status": "skipped", "reason": "empty transcript"}

    if is_hallucinated(full_transcript):
        return {
            "file"  : audio_path.name,
            "status": "skipped",
            "reason": "hallucination detected — audio quality too low (try better recording)"
        }

    logger.info(
        f"Transcript ({len(full_transcript)} chars):\n"
        f"{full_transcript[:300]}{'...' if len(full_transcript) > 300 else ''}"
    )

    # 4. speaker diarization / turn splitting
    turns = diarize_and_split(pcm, full_transcript)
    if not turns:
        logger.warning("No usable turns after segmentation — skipping file.")
        return {"file": audio_path.name, "status": "skipped", "reason": "no turns"}

    # 5. build session via reasoning agent
    session  = build_session_from_turns(turns, call_id, start_time, domain)
    end_time = time.time()

    # 6. generate MoM
    logger.info("Generating MoM report...")
    try:
        if domain == "realestate":
            mom_text = generate_mom(
                session    = session,
                start_time = start_time,
                end_time   = end_time
            )
        else:
            mom_text = generate_mom_generic(
                session    = session,
                start_time = start_time,
                end_time   = end_time
            )
    except Exception as e:
        logger.error(f"MoM generation failed: {e}")
        return {"file": audio_path.name, "status": "failed", "error": str(e)}

    # 7. save outputs
    mom_path       = save_mom(mom_text, call_id, start_time)
    analytics_path = save_analytics(session)

    logger.info(
        f"Done — Stage: {session.call_stage} | "
        f"Lead Score: {session.business_state.get('lead_score', 0)} | "
        f"Turns: {len(turns)} | Duration: {duration_sec:.1f}s"
    )
    logger.separator("=", 60)

    return {
        "file"           : audio_path.name,
        "status"         : "success",
        "call_id"        : call_id,
        "domain"         : domain,
        "duration_sec"   : round(duration_sec, 1),
        "turns_processed": len(turns),
        "lead_stage"     : session.call_stage,
        "lead_score"     : session.business_state.get("lead_score", 0),
        "mom_path"       : str(mom_path),
        "analytics_path" : str(analytics_path),
    }


# =============================================================================
# 10. BATCH PROCESSOR
# =============================================================================

def process_folder(
    input_dir  : Path,
    transcriber: Transcriber,
    lang       : str,
    domain     : str
) -> list:
    audio_files = sorted(
        f for f in input_dir.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not audio_files:
        logger.warning(f"No supported audio files found in: {input_dir}")
        return []

    logger.info(f"Found {len(audio_files)} audio file(s) to process")
    results = []
    for audio_path in audio_files:
        result = process_audio_file(audio_path, transcriber, lang, domain)
        results.append(result)
    return results


def print_summary(results: list) -> None:
    logger.separator("=", 60)
    logger.info("BATCH PROCESSING SUMMARY")
    logger.separator("-", 60)

    success = [r for r in results if r.get("status") == "success"]
    failed  = [r for r in results if r.get("status") == "failed"]
    skipped = [r for r in results if r.get("status") == "skipped"]

    logger.info(f"Total  : {len(results)}")
    logger.info(f"Success: {len(success)}")
    logger.info(f"Skipped: {len(skipped)}")
    logger.info(f"Failed : {len(failed)}")

    if success:
        logger.separator("-", 60)
        logger.info("Successful files:")
        for r in success:
            logger.info(
                f"  {r['file']} -> Stage: {r['lead_stage']} | "
                f"Score: {r['lead_score']} | MoM: {r['mom_path']}"
            )

    if skipped:
        logger.separator("-", 60)
        logger.warning("Skipped files:")
        for r in skipped:
            logger.warning(f"  {r['file']} -> {r.get('reason', 'unknown reason')}")

    if failed:
        logger.separator("-", 60)
        logger.error("Failed files:")
        for r in failed:
            logger.error(f"  {r['file']} -> {r.get('error', 'unknown error')}")

    logger.separator("=", 60)


# =============================================================================
# 11. CLI ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate MoM reports from recorded call audio files (.mp3 / .mp4)"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to folder containing audio files OR path to a single audio file"
    )
    parser.add_argument(
        "--file", "-f",
        default=None,
        help="(Optional) Process only this specific filename inside --input folder"
    )
    parser.add_argument(
        "--lang", "-l",
        default="auto",
        choices=["en", "hi", "auto"],
        help=(
            "Transcription language: "
            "'en' = English, "
            "'hi' = Hindi, "
            "'auto' = auto-detect / Hinglish (default: auto)"
        )
    )
    parser.add_argument(
        "--domain", "-d",
        default="general",
        choices=["general", "realestate"],
        help=(
            "Call domain: "
            "'general' = any type of call (default), "
            "'realestate' = real estate sales call with property knowledge"
        )
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)

    logger.info("Loading Whisper transcription model...")
    transcriber = Transcriber()
    logger.info("Whisper model ready.")

    if input_path.is_file():
        results = [process_audio_file(input_path, transcriber, args.lang, args.domain)]
    elif args.file:
        target = input_path / args.file
        if not target.exists():
            logger.error(f"File not found: {target}")
            sys.exit(1)
        results = [process_audio_file(target, transcriber, args.lang, args.domain)]
    else:
        results = process_folder(input_path, transcriber, args.lang, args.domain)

    print_summary(results)

    if results:
        summary_path = Path("mom") / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Batch summary saved: {summary_path}")


if __name__ == "__main__":
    main()