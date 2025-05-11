import base64
import email
import json
import time
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import google.generativeai as genai

# Gemini API Key
GEMINI_API_KEY = "AIzaSyBi4TAfIHOjQcREGP0EN25mNa4Dmnv6Sws"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    creds = None
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token2.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service


def get_unread_emails(service, seen_ids, max_results=10):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread", maxResults=max_results).execute()
    messages = results.get('messages', [])
    new_emails = []

    for message in messages:
        msg_id = message['id']
        if msg_id in seen_ids:
            continue  # skip previously seen

        msg = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_raw)

        subject = "(No Subject)"
        headers = mime_msg.items()
        for key, val in headers:
            if key.lower() == "subject":
                subject = val.strip()

        body = ""
        if mime_msg.is_multipart():
            for part in mime_msg.walk():
                if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get("Content-Disposition", "")):
                    charset = part.get_content_charset() or 'utf-8'
                    body = part.get_payload(decode=True).decode(charset, errors="ignore")
                    break
        else:
            charset = mime_msg.get_content_charset() or 'utf-8'
            body = mime_msg.get_payload(decode=True).decode(charset, errors="ignore")

        new_emails.append((msg_id, subject, body.strip()))

    return new_emails


def extract_tasks_with_gemini(emails):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-001")

    prompt = (
        "Given the following plain-text emails, extract any task-related content. "
        "For each email that includes a task, return a JSON object with:\n"
        "- 'summary': (string) → Title of the task/event\n"
        "- 'description': (string) → Full email content or context\n"
        "- 'start': { 'dateTime': 'YYYY-MM-DDTHH:MM:SS+02:00', 'timeZone': 'Europe/Rome' }\n"
        "- 'end': { 'dateTime': 'YYYY-MM-DDTHH:MM:SS+02:00', 'timeZone': 'Europe/Rome' }\n\n"
        "The 'dateTime' must include the timezone offset (e.g., +02:00).\n"
        "Return a JSON array. Only return the JSON with no explanation or extra text.\n\n"
    )

    for i, (msg_id, subject, body) in enumerate(emails):
        prompt += f"Email {i+1}:\nSubject: {subject}\nBody: {body}\n\n"

    response = model.generate_content(prompt)
    return response.candidates[0].content.parts[0].text


def clean_json_string(s):
    import re
    s = re.sub(r'```json', '', s)
    s = re.sub(r'```', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def fetch_tasks_from_email():
    service = authenticate_gmail()
    seen_ids = set()

    new_emails = get_unread_emails(service, seen_ids)

    if not new_emails:
        return []

    gemini_output = extract_tasks_with_gemini(new_emails)
    clean_output = clean_json_string(gemini_output)

    try:
        parsed = json.loads(clean_output)
        return parsed
    except json.JSONDecodeError:
        print("Failed to parse Gemini output:")
        print(clean_output)
        return []


if __name__ == '__main__':
    tasks = fetch_tasks_from_email()
    print(json.dumps(tasks, indent=2))