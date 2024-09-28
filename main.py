import sys
import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, WebSocket
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from utils.speech_processing import transcribe_audio
from utils.video_analysis import analyze_video_advanced
from utils.key_moment_extraction import extract_key_moments_advanced
from utils.clip_generation import generate_clips_advanced
from utils.post_processing import crop_video_to_9_16, save_video
from utils.metadata_generation import generate_metadata_advanced
from utils.logging_config import setup_logging
import logging
from tqdm import tqdm
import asyncio
from starlette.websockets import WebSocketDisconnect
from transformers import AutoTokenizer, AutoModel
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware

tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased")
app = FastAPI()

ALLOWED_EXTENSIONS = {"mp4", "mov", "3gp", "avi"}
VIDEO_STORAGE_PATH = '/app/video_path'
CACHE_DIR = '/app/cache_dir'
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/api/upload")
async def upload_video(videoId: str = Form(...), file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file format. Only mp4, mov, 3gp, and avi are allowed.")
    
    file_location = os.path.join(VIDEO_STORAGE_PATH, f"{videoId}.{file.filename.rsplit('.', 1)[1].lower()}")
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.get("/api/generate")
async def generate_video(videoId: str):
    cache_dir = os.path.join(CACHE_DIR, videoId)
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    for ext in ALLOWED_EXTENSIONS:
        video_path = os.path.join(VIDEO_STORAGE_PATH, f"{videoId}.{ext}")
        print(video_path)
        if os.path.exists(video_path):
            transcription = transcribe_audio(video_path, cache_dir)
            print('transcription')
            clips, words = extract_key_moments_advanced(transcription['sentences'], num_clips=4, clip_len=15, model=model, tokenizer=tokenizer, words=transcription['words'])
            paths = save_video(clips, video_path, cache_dir)
            for i, path in enumerate(paths):
                ind = i + 1
                proccessed_path = os.path.join(cache_dir, f'video_last_{ind}.mp4')
                if os.path.exists(proccessed_path):
                    os.remove(proccessed_path)
                crop_video_to_9_16(path, proccessed_path, words=words[i])
            return 4

    raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/part")
async def get_video_part(videoId: str, clipsNum: str):
    part_path = os.path.join(CACHE_DIR, videoId, f'video_last_{clipsNum}.mp4')
    if os.path.exists(part_path):
        return FileResponse(part_path, media_type="video/mp4"), {"": }
    raise HTTPException(status_code=404, detail="Part not found")


# Настройка CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://89.110.109.100",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
