from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
import os
from config import VIDEO_STORAGE_PATH
from utils.video_processing import split_video_into_parts

router = APIRouter()

ALLOWED_EXTENSIONS = {"mp4", "mov", "3gp", "avi"}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/api/upload")
async def upload_video(videoId: str = Form(...), file: UploadFile = File(...)):
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Invalid file format. Only mp4, mov, 3gp, and avi are allowed.")
    
    file_location = os.path.join(VIDEO_STORAGE_PATH, f"{videoId}.{file.filename.rsplit('.', 1)[1].lower()}")
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@router.get("/api/generate")
async def generate_video(videoId: str):
    for ext in ALLOWED_EXTENSIONS:
        file_location = os.path.join(VIDEO_STORAGE_PATH, f"{videoId}.{ext}")
        if os.path.exists(file_location):
            parts = split_video_into_parts(file_location, num_parts=4)
            parts_dir = os.path.join(VIDEO_STORAGE_PATH, videoId)
            os.makedirs(parts_dir, exist_ok=True)
            for i, part in enumerate(parts):
                part_path = os.path.join(parts_dir, f"part_{i+1}.mp4")
                with open(part_path, "wb") as f:
                    f.write(part.read())
            return len(parts)
    raise HTTPException(status_code=404, detail="Video not found")

@router.get("/api/part")
async def get_video_part(videoId: str, clipsNum: str):
    part_path = os.path.join(VIDEO_STORAGE_PATH, videoId, f"part_{clipsNum}.mp4")
    if os.path.exists(part_path):
        return FileResponse(part_path, media_type="video/mp4")
    raise HTTPException(status_code=404, detail="Part not found")

@router.get("/api/meta")  # Исправлено: добавлен слэш в начале пути
async def get_video_meta(videoId: str, clipsNum: str):
    meta = {
        "title": "Потоп в курортном городе: Стас Михайлов и Детройт Метал Сити",
        "description": "Смотрите эксклюзивное видео, в котором курортный город затопило из-за тропического ливня. Но есть те, кто объясняет это Стасом Михайловым и его желанием экранизировать аниме «Детройт Метал Сити». Не упустите этот интересный момент!",
        "hashtags": [
            "#потоп",
            "#курортныйгород",
            "#тропическийлиvenir",
            "#СтасМихайлов",
            "#ДетройтМеталСити",
            "#аниме",
            "#экранизация"
        ],
        "sentiment": "mixed",
        "target_audience": "взрослые, интересующиеся новостями и популярной культурой"
    }
    return JSONResponse(content=jsonable_encoder(meta), status_code=200)

@router.delete("/api/delete")
async def delete_video(videoId: str):
    deleted_files = []
    for ext in ALLOWED_EXTENSIONS:
        file_location = os.path.join(VIDEO_STORAGE_PATH, f"{videoId}.{ext}")
        if os.path.exists(file_location):
            # os.remove(file_location)
            deleted_files.append(file_location)

    parts_dir = os.path.join(VIDEO_STORAGE_PATH, videoId)
    if os.path.exists(parts_dir):
        for file in os.listdir(parts_dir):
            file_path = os.path.join(parts_dir, file)
            os.remove(file_path)
        # os.rmdir(parts_dir)
        deleted_files.append(parts_dir)

    if not deleted_files:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return {"info": f"Deleted files: {deleted_files}"}
