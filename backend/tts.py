import pyttsx3
import os
from datetime import datetime

def text_to_speech(text: str) -> str:
    """Convert text to speech and save as MP3 (offline)."""
    engine = pyttsx3.init()
    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename
