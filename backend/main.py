# backend/main.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rag import answer_from_docs
from tts import text_to_speech
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    """Handle voice agent query — run RAG + generate audio."""
    answer = answer_from_docs(question)
    audio_path = text_to_speech(answer)

    # save transcript
    transcript = {"question": question, "answer": answer}
    os.makedirs("transcripts", exist_ok=True)
    with open(f"transcripts/session.json", "a") as f:
        f.write(json.dumps(transcript) + "\n")

    return {"answer": answer, "audio_file": audio_path}

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    return FileResponse(os.path.join("outputs", filename))
