import json
from google import genai
from configs import settings
from configs.prompts import MOM_PROMPT
from datetime import datetime
from utils.logger import logger


client = genai.Client(api_key=settings.mom_key)


def generate_mom(session, start_time: float, end_time: float) -> str:
    
    try:
        duration_seconds = end_time - start_time
        duration_minutes = round(duration_seconds / 60.0, 2)
        date_str = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M")

        transcript = session.get_full_transcript()

        if not transcript.strip():
            transcript = "No meaningful conversation captured."

        prompt = MOM_PROMPT.format(
            date=date_str,
            duration_minutes=duration_minutes,
            business_state=json.dumps(session.business_state, indent=2),
            call_stage=session.call_stage,
            lead_score=session.business_state.get("lead_score", 0),
            properties_discussed=json.dumps(
                session.insights.get("properties_discussed", []),
                indent=2
            ),
            transcript=transcript,
            action_items=json.dumps(session.action_items, indent=2),
            decisions=json.dumps(session.decisions, indent=2),
            sentiment_timeline=json.dumps(session.sentiment_timeline, indent=2),
        )

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.3
            }
        )

        return response.text.strip()

    except Exception as e:
        logger.error(f"MoM generation failed: {e}")
        return "MoM generation failed due to a system error."