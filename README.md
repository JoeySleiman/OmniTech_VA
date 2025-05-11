

# OmniTech\_VA

**A Proactive Virtual Assistant for Smarter Workflows**
Developed as part of the **2025 GDG Hackathon – HCI Track**

---

##  Quick Start Guide

1. **Install dependencies**:

```bash
pip install pyttsx3 SpeechRecognition python-dotenv google-generativeai google-adk pyaudio setuptools google-auth google-auth-oauthlib google-api-python-client cohere pytz
```

2. **Run the assistant**:

```bash
python Virtual_Assistant.py
```

> This will initialize voice input, process tasks using the agent, and schedule actions based on task priority and reasoning.

---

##  Concept Overview

**OmniTech\_VA** is a **multimodal, proactive virtual assistant** that continuously monitors your digital workspace to extract actionable tasks (from email, voice, etc.), intelligently schedule your day, and launch the right tools—right when you need them.

---

##  Core Capabilities

### 1. **Contextual Task Extraction**

* **Perception**: Reads incoming communications (Gmail, chat apps) using native APIs or screen OCR.
* **Understanding**: Uses a large language model (LLM) to infer deadlines, required tools, and estimated effort.

### 2. **Intelligent Scheduling**

* **Urgency + Effort Model**: Ranks tasks based on deadlines and time estimates.
* **Calendar Integration**: Automatically creates Google Calendar events while avoiding conflicts and optimizing workflow.

### 3. **Smart Workspace Launcher**

* **Pre-Task Setup**: Automatically opens the necessary applications and files (e.g., launching Photoshop with the right project file).
* **Voice/Text Control**: Adjust or reprioritize tasks by speaking or typing natural commands.

### 4. **Saved-State Snapshots**

* **Workspace Checkpoints**: Captures active window layouts and tabs at key moments.
* **Quick Resume**: Reconstructs your last working state with a contextual summary (e.g., *“You last edited the title slide and selected a color palette.”*).

---

##  Module Breakdown

* **Speech\_to\_text**, **VO**, and **agent**: Handle voice-based interactions using the **Gemini API**.
* **gmail\_tasks**: Reads Gmail emails and extracts tasks using reasoning, powered by the **Gemini** and **Gmail APIs**.
* **scheduler**: Combines extracted tasks, scores them by importance, and schedules them using:

  * **Cohere**
  * **Google Calendar**
  * **Google Tasks**
  * Local file and application launching logic

