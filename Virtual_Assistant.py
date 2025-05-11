import os
import json
import time
import pytz
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from dateutil.parser import parse as parse_datetime
from Scheduler import create_event
from Scheduler import handle_todays_events
from Scheduler import log_completed_tasks_for_today

from VO import run_voice_task_capture
from gmail_task import fetch_tasks_from_email

INCOMING_TASKS_FILE = Path("incoming_tasks.json")
WORK_START = 3
WORK_END = 20

# Load existing or start new
if INCOMING_TASKS_FILE.exists():
    with open(INCOMING_TASKS_FILE, 'r') as f:
        try:
            TASK_QUEUE = json.load(f)
        except json.JSONDecodeError:
            TASK_QUEUE = []
else:
    TASK_QUEUE = []

# Save task queue to disk
def save_tasks():
    with open(INCOMING_TASKS_FILE, 'w') as f:
        json.dump(TASK_QUEUE, f, indent=2)

# Append new tasks from voice and Gmail
async def update_task_queue():
    new_tasks = []
    new_tasks += run_voice_task_capture()  # [{title, description, duration, deadline}]
    new_tasks += fetch_tasks_from_email()
    for task in new_tasks:
        if task and task not in TASK_QUEUE:
            print(f"New task captured: {task.get('summary', 'No Title')}")
            TASK_QUEUE.append(task)

    save_tasks()

# Prioritize by urgency (deadline - now) and duration
def prioritize_tasks(tasks):
    tz = pytz.timezone("Europe/Rome")
    now = datetime.now(tz) 
    def score(task):
        start_str = task.get("start", {}).get("dateTime")
        if not start_str:
            return float('inf')  # No start time, deprioritize

        start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        if start_time.tzinfo is None:
            start_time = tz.localize(start_time)
        hours_left = (start_time - now).total_seconds() / 3600

        # Estimate duration if 'end' exists
        end_str = task.get("end", {}).get("dateTime")
        if end_str:
            end_time = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            if end_time.tzinfo is None:
                end_time = tz.localize(end_time)
            duration_hours = (end_time - start_time).total_seconds() / 3600
        else:
            duration_hours = 1  # Default duration

        return hours_left + duration_hours
    return sorted(tasks, key=score)

# Find next available slot
def find_next_slot(duration_minutes):
    tz = datetime.now().astimezone().tzinfo
    current = datetime.now(tz).replace(second=0, microsecond=0)

    while True:
        if WORK_START <= current.hour < WORK_END:
            return current
        current += timedelta(minutes=30)

# Scheduler loop
async def main_loop():  
    while True:
        await update_task_queue()
        await handle_todays_events()
        await log_completed_tasks_for_today()
        prioritized = prioritize_tasks(TASK_QUEUE)
        scheduled = []

        for task in prioritized:
            try:
                start_time = parse_datetime(task['start']['dateTime'])
                end_time = parse_datetime(task['end']['dateTime'])
                duration_minutes = int((end_time - start_time).total_seconds() // 60)
                create_event(
                    title=task['summary'],
                    description=task.get('description', ''),
                    start_time=start_time,
                    duration_minutes=duration_minutes
                )
                scheduled.append(task)
                TASK_QUEUE.remove(task)
                save_tasks()
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Failed to schedule task '{task.get('summary', '')}': {e}")

        print("All pending tasks scheduled. Sleeping 30 seconds...")
        await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.run(main_loop())