import json
import re
from google import genai
from configs import settings
from configs.prompts import REASONING_PROMPT
from utils.logger import logger
from data import property_knowledge


client = genai.Client(api_key=settings.reasoning_key)


def reason_about_user(session, user_text: str) -> dict:

    company_context = property_knowledge.MASTER_CONTEXT

    prompt = REASONING_PROMPT.format(
        company_context=company_context,
        summary=session.summary,
        recent_context=session.get_context_for_prompt(5),
        entities=json.dumps(session.entities),
        business_state=json.dumps(session.business_state),
        lead_score=session.business_state.get("lead_score", 0),
        decisions=json.dumps(session.decisions),
        action_items=json.dumps(session.action_items),
        call_stage=session.call_stage,
        insights=json.dumps(session.insights),
        user_text=user_text
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.2
            }
        )

        text = response.text.strip()

        match = re.search(r'\{[\s\S]*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group(0))

            required_fields = [
                "intent",
                "entities",
                "sentiment",
                "lead_stage",
                "action_items",
                "decisions",
                "business_updates",
                "final_response",
                "end_call"
            ]

            for field in required_fields:
                if field not in result:
                    result[field] = {} if field in ["entities", "business_updates"] else [] if field in ["action_items", "decisions"] else ""

            if not isinstance(result.get("end_call"), bool):
                result["end_call"] = False

            if not result.get("final_response"):
                result["final_response"] = "Could you please clarify that?"

            return result

        logger.error("No valid JSON found in reasoning response.")

    except Exception as e:
        logger.error(f"Reasoning model call failed: {e}")

    return {
        "intent": "unknown",
        "entities": {},
        "sentiment": "neutral",
        "lead_stage": "new",
        "action_items": [],
        "decisions": [],
        "business_updates": {},
        "final_response": "I'm sorry, I am facing a temporary issue. Could you please repeat that?",
        "end_call": False
    }