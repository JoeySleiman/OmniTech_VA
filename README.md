# OmniTech_VA
A virtual assistant developed as part of the 2025 GDG Hackathon HCI track

A quick start up guide:
run: pip install pyttsx3 SpeechRecognition python-dotenv google-generativeai google-adk pyaudio setuptools google-auth google-auth-oauthlib google-api-python-client python-dotenv cohere pyttsx3    

The Speech_to_text, VO, and agent are used for the voice over capabilty and work based on the following APIs:
- Gemini
The gmail_tasks reads gmail emails and uses reasoning to extract events from the emails using the following APIs:
- Gemini
- Gmail API
The scheduler creates events and tasks from the outputs of the previous two, and opens the necessary appliction and files using reasoning from the event names using the following APIs:
- Cohere
- Google Calender
- Google Tasks

Run the main file by using: pyhton Virtual_Assistant.py . The file combines the outputs of the Speech and Voice and feeds them into the scheduler after passing a rudimentary importance calculation of the events and rearranges them according to that score.
