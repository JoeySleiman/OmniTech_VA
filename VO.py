import asyncio
import pyttsx3
import json
from pathlib import Path
from Speech_to_text import record_and_transcribe
from agent import get_agent_reply, ensure_session  # import both functions

engine = pyttsx3.init()

TASKS_FILE = Path("incoming_tasks.json")

def save_task_to_json(text):
    if not text:
        return
    tasks = []
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, "r") as f:
                tasks = json.load(f)
        except json.JSONDecodeError:
            tasks = []

    tasks.append({"task": text})
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

async def run_voice_task_capture():
    user_id = "user1"
    session_id = "session1"
    ensure_session(user_id, session_id)

    spoken_text = record_and_transcribe()
    if spoken_text in ["NO_INPUT", "UNRECOGNIZED", "API_ERROR"]:
        print(f"Issue: {spoken_text}.")
        return []

    print(f"You said: {spoken_text}")
    response = await get_agent_reply(spoken_text, user_id, session_id)

    try:
        tasks = json.loads(response)
        if isinstance(tasks, dict):  # In case a single dict is returned
            tasks = [tasks]
        return tasks
    except Exception as e:
        print(f"Failed to parse voice agent reply as JSON: {e}")
        print("Raw reply:", response)
        return []
