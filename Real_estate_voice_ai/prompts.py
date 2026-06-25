from google import genai
from configs import settings

client = genai.Client(api_key=settings.summarizer_key)

def summarizer_agent(previous_summary: str, recent_turns: str) -> str:

    prompt = f"""
        You are a Conversation Memory Compression Agent for a real-time AI Voice Assistant.

        Your job is to maintain a COMPLETE and STRUCTURED memory state of the ongoing call.

        This memory will be used by other agents (Intent Detection, Objection Handling, Lead Qualification, Closing Agent).
        Therefore, it must preserve full business context without losing critical details.

        ========================
        PREVIOUS MEMORY STATE:
        {previous_summary}

        NEW CONVERSATION TURNS:
        {recent_turns}
        ========================

        INSTRUCTIONS:

        1. Update the memory state by integrating new information.
        2. NEVER remove previously confirmed facts unless the customer explicitly corrects them.
        3. Track changes in:
        - Customer name
        - Contact details
        - Budget range
        - Location preferences
        - Property preferences
        - Timeline
        - Intent (buying, renting, inquiry, comparison, negotiation)
        - Objections
        - Emotional tone (confused, excited, hesitant, price-sensitive, urgent)
        - Decision status
        - Follow-up commitments
        4. If customer changes intent or constraints, clearly mark it as:
        "UPDATED: <field> changed from X to Y"
        5. Maintain logical business state progression.
        6. Do NOT summarize loosely.
        7. Do NOT invent information.
        8. Keep it structured and easy for downstream agents to parse.

        OUTPUT FORMAT:

        CALL MEMORY STATE

        Customer Profile:
        - Name:
        - Phone:
        - Budget:
        - Preferred Location:
        - Property Type:
        - Timeline:

        Intent & Stage:
        - Current Intent:
        - Lead Stage:
        - Confidence Level:

        Objections:
        - 

        Key Decisions:
        - 

        Emotional Signals:
        - 

        Pending Actions:
        - 

        Conversation Highlights:
        - Bullet points capturing important statements.

        Return ONLY the updated CALL MEMORY STATE.
        No explanations.
        """
    response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "temperature": 0.2,
            }
        )
    
    return response.text.strip()