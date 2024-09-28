# app/main.py

import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from utils.speech_processing import transcribe_audio, transcribe_audio_advanced
from utils.video_analysis import analyze_video_advanced
from utils.key_moment_extraction import extract_key_moments_advanced
from utils.clip_generation import generate_clips_advanced
from utils.post_processing import process_clips_advanced
from utils.metadata_generation import generate_metadata_advanced
from utils.logging_config import setup_logging
import logging
from tqdm import tqdm
import asyncio
from starlette.websockets import WebSocketDisconnect

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/clips", StaticFiles(directory="clips"), name="clips")

UPLOAD_DIR = 'uploads/'
os.makedirs(UPLOAD_DIR, exist_ok=True)

websocket_clients = set()

async def send_progress_update(message):
    for websocket in websocket_clients:
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            websocket_clients.remove(websocket)

@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            raise HTTPException(status_code=400, detail="Неверный формат видео")

        video_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Загружео видео: {video_path}")

        # Обработка видео
        clips_info = await process_video(video_path)
        
        logger.info(f"Получена информация о клипах: {len(clips_info)} клипов")
        
        return {"message": "Видео успешно загружено и обработано", "clips": clips_info}
    except Exception as e:
        logger.exception(f"Ошибка при загрузке видео: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video(video_path):
    logger.info(f"Начало обработки видео: {video_path}")
    
    total_steps = 6  # Общее количество шагов обработки
    
    with tqdm(total=total_steps, desc="Обработка видео") as pbar:
        # Шаг 3: Расширенная обработка аудио и речи
        transcription = transcribe_audio_advanced(video_path)
        pbar.update(1)
        await send_progress_update("Транскрипция завершена (1/6)")
        logger.info("Транскрипция завершена")
        
        # Шаг 4: Расширенный анализ видео
        video_events = await analyze_video_advanced(video_path)
        if not video_events:
            logger.warning("Не удалось извлечь события из видео")
            video_events = [{'timestamp': 0, 'objects': []}]  # Базовое событие
        pbar.update(1)
        await send_progress_update("Анализ видео завершен (2/6)")
        logger.info("Анализ видео завершен")
        
        # Шаг 5: Расширенное извлечение ключевых моментов
        key_moments = extract_key_moments_advanced(transcription, video_events)
        if not key_moments:
            logger.warning("Не удалось извлечь ключевые моменты")
            key_moments = [{'start': 0, 'end': 10, 'importance_score': 1}]  # Базовый ключевой момент
        pbar.update(1)
        await send_progress_update(f"Извлечено ключевых моментов: {len(key_moments)} (3/6)")
        logger.info(f"Извлечено ключевых моментов: {len(key_moments)}")
        
        # Шаг 6: Расширенная генерация клипов
        clips = generate_clips_advanced(video_path, key_moments)
        pbar.update(1)
        await send_progress_update(f"Сгенерировано клипов: {len(clips)} (4/6)")
        logger.info(f"Сгенерировано клипов: {len(clips)}")
        
        # Шаг 7: Расширенная постобработка
        processed_clips = process_clips_advanced(clips, transcription)
        pbar.update(1)
        await send_progress_update(f"Обработано клипов: {len(processed_clips)} (5/6)")
        logger.info(f"Обработано клипов: {len(processed_clips)}")
        
        # Шаг 8: Расширенная генерация метаданных
        metadata = generate_metadata_advanced(transcription, key_moments, video_events)
        pbar.update(1)
        await send_progress_update("Метаданные сгенерированы (6/6)")
        logger.info("Метаданные сгенерированы")
    
    # Возвращаем информацию о клипах
    clips_info = []
    for idx, clip in enumerate(processed_clips):
        clip_info = {
            "clip_path": f"/clips/modified/clip_{idx}.mp4",
            "metadata": metadata[idx] if idx < len(metadata) else {}
        }
        clips_info.append(clip_info)
    
    logger.info(f"Обработка видео завершена. Сгенерировано клипов: {len(clips_info)}")
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
    clip_path = os.path.join('clips/modified/', clip_name)
    if os.path.exists(clip_path):
        return FileResponse(path=clip_path, filename=clip_name)
    else:
        raise HTTPException(status_code=404, detail="Клип не найден")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
