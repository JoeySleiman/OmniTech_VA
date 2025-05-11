import speech_recognition as sr

def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak something... (say 'stop' to exit)")
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return "NO_INPUT"

        with open("last_audio.wav", "wb") as f:
            f.write(audio.get_wav_data())

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "UNRECOGNIZED"
    except sr.RequestError:
        return "API_ERROR"
    except Exception as e:
        print(f"Unexpected error during recognition: {e}")
        return "API_ERROR"
