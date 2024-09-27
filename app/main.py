# app/main.py

import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from utils.speech_processing import transcribe_audio, transcribe_audio_advanced
from utils.video_analysis import analyze_video, analyze_video_advanced
from utils.key_moment_extraction import extract_key_moments, extract_key_moments_advanced
from utils.clip_generation import generate_clips, generate_clips_advanced
from utils.post_processing import process_clips, process_clips_advanced
from utils.metadata_generation import generate_metadata, generate_metadata_advanced
from utils.logging_config import setup_logging
import logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR = 'uploads/'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            raise HTTPException(status_code=400, detail="Неверный формат видео")

        video_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Загружено видео: {video_path}")

        # Обработка видео
        clips_info = await process_video(video_path)

        return {"message": "Видео успешно загружено и обработано", "clips": clips_info}
    except Exception as e:
        logger.exception("Ошибка при загрузке видео")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video(video_path):
    # Шаг 3: Расширенная обработка аудио и речи
    transcription = transcribe_audio_advanced(video_path)

    # Шаг 4: Расширенный анализ видео
    video_events = analyze_video_advanced(video_path)

    # Шаг 5: Расширенное извлечение ключевых моментов
    key_moments = extract_key_moments_advanced(transcription, video_events)

    # Шаг 6: Расширенная генерация клипов
    clips = generate_clips_advanced(video_path, key_moments)

    # Шаг 7: Расширенная постобработка
    processed_clips = process_clips_advanced(clips, transcription)

    # Шаг 8: Расширенная генерация метаданных
    metadata = generate_metadata_advanced(transcription, key_moments, video_events)

    # Возвращаем информацию о клипах
    clips_info = []
    for idx, clip in enumerate(processed_clips):
        clip_info = {
            "clip_path": f"/{clip['processed_clip_path']}",
            "metadata": metadata[idx]
        }
        clips_info.append(clip_info)
    return clips_info

@app.get("/editor/", response_class=HTMLResponse)
async def editor(request: Request):
    try:
        return HTMLResponse(content=open("app/templates/editor.html", encoding='utf-8').read())
    except Exception as e:
        logger.exception("Ошибка при загрузке редактора")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download_clip/")
async def download_clip(clip_name: str):
    clip_path = os.path.join('clips/processed/', clip_name)
    if os.path.exists(clip_path):
        return FileResponse(path=clip_path, filename=clip_name)
    else:
        raise HTTPException(status_code=404, detail="Клип не найден")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
