from google import genai
from configs import settings

client = genai.Client(api_key=settings.conversation_key)


def stream_conversational_response(seed_text: str, sentence_callback):

    stream = client.models.generate_content_stream(
        model=settings.GEMINI_MODEL,
        contents=f"""
            You are a professional real estate consultant speaking on a call.

            Speak naturally in short conversational sentences.
            Do not repeat information unnecessarily.
            Keep it 2-4 sentences.

            Core message:
            {seed_text}
        """,
        config={"temperature": 0.6}
    )

    buffer = ""

    for chunk in stream:
        if chunk.text:
            buffer += chunk.text

            while True:
                sentence_end = None
                for punct in [".", "?", "!"]:
                    idx = buffer.find(punct)
                    if idx != -1:
                        sentence_end = idx
                        break

                if sentence_end is not None:
                    sentence = buffer[:sentence_end + 1].strip()
                    buffer = buffer[sentence_end + 1:].strip()

                    if sentence:
                        sentence_callback(sentence)
                else:
                    break
                
    if buffer.strip():
        sentence_callback(buffer.strip())