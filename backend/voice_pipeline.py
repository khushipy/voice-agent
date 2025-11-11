import os
import asyncio
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

import openai
from pydub import AudioSegment
from gtts import gTTS

MAX_AUDIO_SECONDS = 120  # reject very long files for now
ALLOWED_EXT = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4", ".webm"}

# Use a threadpool for blocking I/O (pydub, openai sync calls)
_executor = ThreadPoolExecutor(max_workers=4)

def _ext(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def _convert_to_wav(src_path: str, dst_path: str) -> None:
    """
    Blocking: convert src audio to WAV (16k/mono) using pydub (ffmpeg).
    """
    audio = AudioSegment.from_file(src_path)
    # optionally trim or resample here if needed
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(dst_path, format="wav")

async def _convert_to_wav_async(src_path: str, dst_path: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _convert_to_wav, src_path, dst_path)

async def _transcribe_with_openai(wav_path: str, openai_api_key: str) -> str:
    """
    Blocking call to OpenAI transcription. We call it in run_in_executor to avoid blocking.
    Using the classical openai package. If your SDK differs, change accordingly.
    """
    openai.api_key = openai_api_key

    def _call():
      
        with open(wav_path, "rb") as fh:
         
            try:
                resp = openai.Audio.transcribe(model="gpt-4o-transcribe", file=fh)
            except Exception:
              
                fh.seek(0)
                resp = openai.Audio.transcribe(model="whisper-1", file=fh)
      
        if hasattr(resp, "text"):
            return resp.text
        if isinstance(resp, dict) and "text" in resp:
            return resp["text"]
    
        return str(resp)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _call)

async def _call_llm_answer(prompt: str, openai_api_key: str) -> str:
    openai.api_key = openai_api_key

    def _call():
      
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=450,
                temperature=0.2,
            )
         
            if isinstance(response, dict):
              
                choices = response.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
    
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"LLM call failed: {e}"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _call)

async def _synthesize_tts_gtts(text: str, out_path: str) -> None:
    """
    Blocking: generate mp3 using gTTS and save to out_path.
    """
    def _call():
        tts = gTTS(text=text, lang="en")
        tts.save(out_path)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_executor, _call)

async def process_voice_query(
    input_audio_path: str,
    output_audio_path: str,
    openai_api_key: str,
) -> Tuple[str, str, str]:
    """
    Processes the uploaded audio file:
      1) Convert to WAV
      2) Transcribe via OpenAI
      3) Get an answer from LLM (simple prompt for now)
      4) Generate TTS MP3 to output_audio_path

    Returns: (transcript_text, answer_text, output_audio_path)
    """
    if not os.path.exists(input_audio_path):
        raise FileNotFoundError("input audio not found")

    if _ext(input_audio_path) not in ALLOWED_EXT:
       
        pass

    
    tmpdir = tempfile.mkdtemp(prefix="voice_proc_")
    wav_path = os.path.join(tmpdir, "input.wav")

    try:
        await _convert_to_wav_async(input_audio_path, wav_path)

       
        audio = AudioSegment.from_file(wav_path)
        duration_s = len(audio) / 1000.0
        if duration_s > MAX_AUDIO_SECONDS:
            raise ValueError(f"Audio too long ({duration_s:.1f}s), limit {MAX_AUDIO_SECONDS}s")

       
        transcript = await _transcribe_with_openai(wav_path, openai_api_key)

        
        prompt = f"Answer the user question below concisely and accurately.\nUser question: {transcript}"
        answer = await _call_llm_answer(prompt, openai_api_key)

      
        outdir = os.path.dirname(output_audio_path)
        if outdir:
            os.makedirs(outdir, exist_ok=True)

        await _synthesize_tts_gtts(answer, output_audio_path)

        return transcript, answer, output_audio_path

    finally:
        
        try:
            if os.path.exists(wav_path):
                os.remove(wav_path)
            if os.path.isdir(tmpdir):
                os.rmdir(tmpdir)
        except Exception:
            pass
