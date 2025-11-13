import os
import json
import pyttsx3
from pipecat.services.whisper.stt import WhisperSTTService
from rag import get_vectorstore

TRANSCRIPT_FILE = "transcripts.json"

# Initialize Whisper
stt_service = WhisperSTTService()

# Initialize pyttsx3 TTS
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 180)

def voice_pipeline(audio_path):
    # Convert audio → text
    query = stt_service.transcribe(audio_path).text

    # Get answer from FAISS
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=2)
    answer = " ".join([d.page_content for d in docs]) if docs else "No answer found."

    # Convert answer → audio (MP3)
    response_mp3 = audio_path.replace(".mp3", "_response.mp3")
    tts_engine.save_to_file(answer, response_mp3)
    tts_engine.runAndWait()

    # Save transcript + query + answer
    transcript = {"query": query, "answer": answer}
    if os.path.exists(TRANSCRIPT_FILE):
        with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(transcript)
    with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return response_mp3, transcript

