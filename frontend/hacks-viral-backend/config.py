import os

# Путь к директории для хранения видео
VIDEO_STORAGE_PATH = "video_storage"

# Создаем директорию, если она не существует
os.makedirs(VIDEO_STORAGE_PATH, exist_ok=True)