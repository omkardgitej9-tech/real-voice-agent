# 🏡 Project Title: Real Estate AI Voice Assistant  
### 👥 Team Name: Wifi

---

# 📌 Project Overview

This project is a real-time AI voice assistant designed for intelligent real estate sales conversations.

The system is capable of:

- Handling live microphone-based voice conversations
- Detecting speech using Voice Activity Detection (VAD)
- Converting speech to text using Faster-Whisper
- Understanding intent using Gemini API
- Extracting structured business entities
- Classifying lead stage (new, qualified, hot, follow-up, closed)
- Handling interruptions naturally
- Generating executive-level Minutes of Meeting (MoM) after the call

This project demonstrates a complete conversational AI pipeline with structured business logic and CRM-style memory tracking.

---
# What this project demonstrates 

It demonstrates:
-Real-time audio processing
-Structured conversational reasoning
-Lead qualification intelligence
-Stateful session memory
-Post-call business analytics generation
-API-based modular architecture

---

# ⚙️ Setup Instructions  
### ❓ How do I run this code?

Follow these steps carefully.

---

## 🟢 Step 1: Install Python

Install Python 3.10 or above from:

https://www.python.org/downloads/

Verify installation:

```bash
python --version
```

---

## 🟢 Step 2: Clone the Repository

```bash
git clone https://github.com/Lambo-IITian/Real-estate-voice-AI
cd Real-estate-voice-AI
```

---

## 🟢 Step 3: Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

---

## 🟢 Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🟢 Step 5: Configure Environment Variables

Create a `.env` file in the root folder.

Add your Gemini API key:

```
GEMINI_API_KEY=your_gemini_api_key_here
reasoning_key=your_gemini_api_key_here
mom_key=your_gemini_api_key_here
```
---

## 🟢 Step 6: Run the Local Voice Assistant (Mic Test Mode)

```bash
python src/main.py
```

The assistant will:

- Greet you
- Listen via microphone
- Respond using synthesized speech
- Generate MoM after call ends

---

# 🏗 Architecture Diagram
 ![System Architecture](docs/mermaid-diagram.png)

---

# 🛠 Tech Stack Used

### Telephony
- Asterisk
- SIP (Zoiper)

### AI & NLP
- Google Gemini API
- Faster-Whisper (Speech-to-Text)
- Structured Prompt Engineering

### Speech Processing
- Voice Activity Detection (VAD)
- Piper TTS (Text-to-Speech)

### Backend
- Python
- FastAPI
- Uvicorn

### System Design
- Session Management
- Lead Qualification Logic
- Conversation Memory Tracking
- Post-Call intelligence Generator

---

# 🧠 Core System Features

### ✔ Intent Detection  
Classifies user intent such as:
- Property Inquiry
- Pricing Inquiry
- Site Visit Request
- Objection Handling
- Call Termination

### ✔ Entity Extraction  
Extracts:
- Budget
- Location
- Configuration (2BHK, 3BHK, Villa)
- Timeline
- Investment Type

### ✔ Lead Stage Classification  
- new
- qualified
- hot
- needs_followup
- closed

### ✔ Interruption Handling  
If the user speaks while AI is talking:
- TTS stops immediately
- AI switches back to listening mode

### ✔ Executive MoM Generation  
Generates structured post-call report including:
- Executive Summary
- Customer Requirements
- Key Discussion Points
- Objections
- Lead Assessment
- Action Items
- Sentiment Analysis

---

# 🔐 Security Notes

- API keys stored securely in `.env`
- `.env` excluded via `.gitignore`
- No credentials committed to repository

---

# 🚀 Future Enhancements

- Full RTP streaming integration
- Token-level streaming responses
- Multi-language support
- Cloud deployment (Azure/AWS)
- CRM database integration

---

# 👨‍💻 Developed By

Mohit Gunani , Aditya Kumar Sharma  
IIT BHU  

