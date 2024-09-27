#!/bin/bash

# Скрипт для установки и запуска проекта "Генератор Виральных Видео" с установкой FFmpeg на macOS

# Проверка наличия необходимых инструментов
command -v git >/dev/null 2>&1 || { echo >&2 "Git не установлен. Пожалуйста, установите Git и повторите попытку."; exit 1; }

# Проверка операционной системы
OS_TYPE=$(uname)
echo "Операционная система: $OS_TYPE"

if [ "$OS_TYPE" = "Darwin" ]; then
    # macOS
    echo "Обнаружена macOS"

    # Проверка наличия Homebrew
    if ! command -v brew >/dev/null 2>&1; then
        echo "Homebrew не установлен. Установка Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        # Добавление Homebrew в PATH
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.profile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi

    # Установка FFmpeg через Homebrew
    if ! command -v ffmpeg >/dev/null 2>&1; then
        echo "Установка FFmpeg через Homebrew..."
        brew install ffmpeg
    else
        echo "FFmpeg уже установлен."
    fi
else
    # Предполагаем Linux
    echo "Предполагается, что операционная система - Linux"
    command -v ffmpeg >/dev/null 2>&1 || { echo >&2 "FFmpeg не установлен. Пожалуйста, установите FFmpeg и добавьте его в PATH."; exit 1; }
fi

echo "Начало установки проекта..."

# Установка зависимостей
echo "Установка Python-зависимостей из requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание необходимых директорий
echo "Создание необходимых директорий..."
mkdir -p app/templates
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p models
mkdir -p utils
mkdir -p logs
mkdir -p uploads
mkdir -p clips/original
mkdir -p clips/processed

# Скачивание модели Vosk для русского языка
echo "Скачивание модели Vosk..."
if [ ! -d "models/vosk-model-small-ru-0.22" ]; then
    wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip -O vosk-model-small-ru-0.22.zip
    unzip vosk-model-small-ru-0.22.zip -d models/
    rm vosk-model-small-ru-0.22.zip
else
    echo "Модель Vosk уже скачана."
fi

# Копирование эмодзи изображения
echo "Копирование эмодзи изображения..."
if [ ! -f "utils/emoji.png" ]; then
    wget https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.shutterstock.com%2Fru%2Fsearch%2Fconfident-emoji%3Fimage_type%3Dvector&psig=AOvVaw0v4XoqQBpVkFpWj081E9Ca&ust=1727538207371000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCKirgbu744gDFQAAAAAdAAAAABAJ -O utils/emoji.png
    # Замените URL на фактический путь к вашему файлу emoji.png
else
    echo "Файл emoji.png уже существует."
fi

# Создание файлов проекта

echo "Создание файла app/main.py..."
cat > app/main.py << 'EOF'
# app/main.py

import os
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from utils.speech_processing import transcribe_audio
from utils.video_analysis import analyze_video
from utils.key_moment_extraction import extract_key_moments
from utils.clip_generation import generate_clips
from utils.post_processing import process_clips
from utils.metadata_generation import generate_metadata
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
    # Шаг 3: Обработка аудио и речи
    transcription = transcribe_audio(video_path)

    # Шаг 4: Анализ видео
    video_events = analyze_video(video_path)

    # Шаг 5: Извлечение ключевых моментов
    key_moments = extract_key_moments(transcription, video_events)

    # Шаг 6: Генерация клипов
    clips = generate_clips(video_path, key_moments)

    # Шаг 7: Постобработка
    processed_clips = process_clips(clips, transcription)

    # Шаг 8: Генерация метаданных
    metadata = generate_metadata(transcription, key_moments)

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
EOF

echo "Создание файла utils/logging_config.py..."
cat > utils/logging_config.py << 'EOF'
# utils/logging_config.py

import logging
import os

def setup_logging():
    log_dir = 'logs/'
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log')),
            logging.StreamHandler()
        ]
    )
EOF

echo "Создание файла utils/speech_processing.py..."
cat > utils/speech_processing.py << 'EOF'
# utils/speech_processing.py

import os
import subprocess
import logging
import json
import wave
import vosk
import numpy as np

logger = logging.getLogger(__name__)

def transcribe_audio(video_path):
    try:
        # Извлечение аудио
        audio_path = extract_audio(video_path)
        # Транскрибация аудио
        transcription = speech_to_text(audio_path)
        return transcription
    except Exception as e:
        logger.exception("Ошибка в transcribe_audio")
        raise

def extract_audio(video_path):
    try:
        audio_path = os.path.splitext(video_path)[0] + '.wav'
        command = f"ffmpeg -i \"{video_path}\" -q:a 0 -ar 16000 -ac 1 -map a \"{audio_path}\" -y"
        subprocess.call(command, shell=True)
        logger.info(f"Аудио извлечено: {audio_path}")
        return audio_path
    except Exception as e:
        logger.exception("Ошибка при извлечении аудио")
        raise

def speech_to_text(audio_path):
    try:
        wf = wave.open(audio_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            logger.error("Аудиофайл должен быть в формате WAV mono PCM.")
            raise ValueError("Аудиофайл должен быть в формате WAV mono PCM.")
        model = vosk.Model("models/vosk-model-small-ru-0.22")
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        transcription = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if 'text' in result and result['text'].strip() != '':
                    transcription.append({
                        'text': result['text'],
                        'start': result.get('result', [{}])[0].get('start', 0),
                        'end': result.get('result', [{}])[-1].get('end', 0)
                    })
        final_result = json.loads(rec.FinalResult())
        if 'text' in final_result and final_result['text'].strip() != '':
            transcription.append({
                'text': final_result['text'],
                'start': final_result.get('result', [{}])[0].get('start', 0),
                'end': final_result.get('result', [{}])[-1].get('end', 0)
            })
        logger.info("Аудио успешно транскрибировано")
        return transcription
    except Exception as e:
        logger.exception("Ошибка в speech_to_text")
        raise
EOF

echo "Создание файла utils/video_analysis.py..."
cat > utils/video_analysis.py << 'EOF'
# utils/video_analysis.py

import cv2
import logging
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50

logger = logging.getLogger(__name__)

def analyze_video(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = resnet50(pretrained=True).to(device)
        model.eval()
        preprocess = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor()
        ])

        key_frames = []
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # в секундах
            if frame_idx % int(frame_rate) == 0:
                input_tensor = preprocess(frame).unsqueeze(0).to(device)
                with torch.no_grad():
                    output = model(input_tensor)
                # Извлекаем значимые признаки
                features = output.cpu().numpy()
                key_frames.append({
                    'timestamp': timestamp,
                    'features': features.flatten()
                })
            frame_idx += 1

        cap.release()
        logger.info("Видео успешно проанализировано")
        return key_frames
    except Exception as e:
        logger.exception("Ошибка в analyze_video")
        raise
EOF

echo "Создание файла utils/key_moment_extraction.py..."
cat > utils/key_moment_extraction.py << 'EOF'
# utils/key_moment_extraction.py

import logging
from sklearn.cluster import KMeans
import numpy as np

logger = logging.getLogger(__name__)

def extract_key_moments(transcription, video_events):
    try:
        # Объединяем аудио и видео данные
        timestamps = [event['timestamp'] for event in video_events]
        features = [event['features'] for event in video_events]
        features = np.array(features)

        n_clusters = min(20, len(features))
        kmeans = KMeans(n_clusters=n_clusters, random_state=0)
        clusters = kmeans.fit_predict(features)

        key_moments = []
        for cluster_id in range(n_clusters):
            cluster_indices = np.where(clusters == cluster_id)[0]
            cluster_timestamps = [timestamps[i] for i in cluster_indices]
            start = min(cluster_timestamps)
            end = max(cluster_timestamps)
            # Проверяем длительность клипа
            duration = end - start
            if 10 <= duration <= 180:
                key_moments.append({
                    'start': start,
                    'end': end
                })
        # Убираем пересекающиеся моменты
        key_moments = remove_overlaps(key_moments)
        logger.info("Ключевые моменты успешно извлечены")
        return key_moments
    except Exception as e:
        logger.exception("Ошибка в extract_key_moments")
        raise

def remove_overlaps(key_moments):
    key_moments.sort(key=lambda x: x['start'])
    non_overlapping = []
    prev_end = -1
    for moment in key_moments:
        if moment['start'] > prev_end:
            non_overlapping.append(moment)
            prev_end = moment['end']
        else:
            # Если пересекается более чем на 50%, пропускаем
            overlap = prev_end - moment['start']
            duration = moment['end'] - moment['start']
            if overlap / duration < 0.5:
                non_overlapping.append(moment)
                prev_end = moment['end']
    return non_overlapping
EOF

echo "Создание файла utils/clip_generation.py..."
cat > utils/clip_generation.py << 'EOF'
# utils/clip_generation.py

import subprocess
import logging
import os

logger = logging.getLogger(__name__)

def generate_clips(video_path, key_moments):
    try:
        clips_dir = 'clips/original/'
        os.makedirs(clips_dir, exist_ok=True)
        clips = []
        for idx, moment in enumerate(key_moments):
            start_time = moment['start']
            end_time = moment['end']
            duration = end_time - start_time
            if duration < 10 or duration > 180:
                continue  # Пропускаем клипы вне диапазона длительности
            clip_path = f"{clips_dir}clip_{idx}.mp4"
            command = f"ffmpeg -i \"{video_path}\" -ss {start_time} -to {end_time} -vf \"scale=1080:1920\" -preset ultrafast -c:v libx264 -c:a aac \"{clip_path}\" -y"
            subprocess.call(command, shell=True)
            clips.append({'clip_path': clip_path, 'start': start_time, 'end': end_time})
        logger.info("Клипы успешно сгенерированы")
        return clips
    except Exception as e:
        logger.exception("Ошибка в generate_clips")
        raise
EOF

echo "Создание файла utils/post_processing.py..."
cat > utils/post_processing.py << 'EOF'
# utils/post_processing.py

import logging
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
import random

logger = logging.getLogger(__name__)

def process_clips(clips, transcription):
    try:
        processed_clips_dir = 'clips/processed/'
        os.makedirs(processed_clips_dir, exist_ok=True)
        processed_clips = []
        for idx, clip_info in enumerate(clips):
            clip_path = clip_info['clip_path']
            processed_clip_path = f"{processed_clips_dir}clip_{idx}_processed.mp4"

            # Загружаем видео
            video = VideoFileClip(clip_path)

            # Получаем соответствующий текст из транскрипции
            clip_transcription = get_clip_transcription(transcription, clip_info['start'], clip_info['end'])
            text = ' '.join([t['text'] for t in clip_transcription])

            # Добавляем субтитры
            txt_clip = TextClip(text, fontsize=50, color='white', bg_color='rgba(0,0,0,0.5)', size=video.size, method='caption')
            txt_clip = txt_clip.set_duration(video.duration).set_position(('center', 'bottom'))

            # Добавляем эмодзи
            emoji_files = ['utils/emoji.png']  # Можно добавить больше эмодзи
            emoji_path = random.choice(emoji_files)
            emoji = ImageClip(emoji_path).set_duration(video.duration)
            emoji = emoji.set_position(('right', 'top')).resize(height=100)

            # Композиция видео
            final = CompositeVideoClip([video, txt_clip, emoji])
            final.write_videofile(processed_clip_path, codec='libx264', audio_codec='aac', fps=24, threads=4)
            processed_clips.append({'processed_clip_path': processed_clip_path})
        logger.info("Клипы успешно постобработаны")
        return processed_clips
    except Exception as e:
        logger.exception("Ошибка в process_clips")
        raise

def get_clip_transcription(transcription, start_time, end_time):
    clip_transcription = []
    for t in transcription:
        if t['end'] >= start_time and t['start'] <= end_time:
            clip_transcription.append(t)
    return clip_transcription
EOF

echo "Создание файла utils/metadata_generation.py..."
cat > utils/metadata_generation.py << 'EOF'
# utils/metadata_generation.py

import logging
import random

logger = logging.getLogger(__name__)

def generate_metadata(transcription, key_moments):
    try:
        metadata = []
        for moment in key_moments:
            # Находим текстовые данные для данного временного отрезка
            texts = [t['text'] for t in transcription if t['start'] >= moment['start'] and t['end'] <= moment['end']]
            combined_text = ' '.join(texts)
            # Генерируем название, описание и хештеги
            title = generate_title(combined_text)
            description = generate_description(combined_text)
            hashtags = generate_hashtags(combined_text)
            justification = "Ключевой момент выбран на основе анализа речи и видео."
            metadata.append({
                'title': title,
                'description': description,
                'hashtags': hashtags,
                'justification': justification
            })
        logger.info("Метаданные успешно сгенерированы")
        return metadata
    except Exception as e:
        logger.exception("Ошибка в generate_metadata")
        raise

def generate_title(text):
    # Простая генерация названия на основе ключевых слов
    words = text.split()
    if words:
        title = ' '.join(words[:5])
    else:
        title = 'Интересное видео'
    return title.capitalize()

def generate_description(text):
    return text

def generate_hashtags(text):
    # Генерация хештегов из наиболее часто встречающихся слов
    words = text.lower().split()
    common_words = ['и', 'в', 'на', 'с', 'по', 'а', 'что', 'это', 'из', 'не', 'для', 'к', 'то']
    filtered_words = [word for word in words if word not in common_words and len(word) > 3]
    hashtags = ['#' + word for word in set(filtered_words)][:5]
    return hashtags
EOF

echo "Создание файла utils/__init__.py..."
cat > utils/__init__.py << 'EOF'
# utils/__init__.py

# Пустой файл, необходимый для обозначения директории как пакета Python.
EOF

echo "Создание файла app/templates/editor.html..."
cat > app/templates/editor.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Редактор видео</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="/static/js/editor.js"></script>
</head>
<body>
    <h1>Редактор видео</h1>
    <form id="uploadForm" enctype="multipart/form-data">
        <label for="fileInput">Загрузить видео:</label>
        <input type="file" id="fileInput" name="file">
        <button type="submit">Загрузить и обработать</button>
    </form>
    <div id="clipsContainer"></div>
</body>
</html>
EOF

echo "Создание файла app/static/js/editor.js..."
cat > app/static/js/editor.js << 'EOF'
// app/static/js/editor.js

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let formData = new FormData();
    let fileInput = document.getElementById('fileInput');
    formData.append('file', fileInput.files[0]);
    fetch('/upload_video/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        displayClips(data.clips);
    })
    .catch(error => console.error('Ошибка:', error));
});

function displayClips(clips) {
    let container = document.getElementById('clipsContainer');
    container.innerHTML = '';
    clips.forEach(clip => {
        let clipElement = document.createElement('div');
        clipElement.className = 'clip';
        clipElement.innerHTML = `
            <video width="320" height="240" controls>
                <source src="${clip.clip_path}" type="video/mp4">
            </video>
            <p><strong>Название:</strong> <input type="text" value="${clip.metadata.title}"></p>
            <p><strong>Описание:</strong> <textarea>${clip.metadata.description}</textarea></p>
            <p><strong>Хештеги:</strong> <input type="text" value="${clip.metadata.hashtags.join(' ')}"></p>
            <button onclick="downloadClip('${clip.clip_path}')">Скачать</button>
        `;
        container.appendChild(clipElement);
    });
}

function downloadClip(clipPath) {
    window.location.href = clipPath;
}
EOF

echo "Создание файла app/static/css/style.css..."
cat > app/static/css/style.css << 'EOF'
/* app/static/css/style.css */

body {
    font-family: Arial, sans-serif;
    margin: 20px;
}

h1 {
    color: #333;
}

#uploadForm {
    margin-bottom: 20px;
}

.clip {
    border: 1px solid #ccc;
    padding: 10px;
    margin-bottom: 20px;
}

.clip video {
    display: block;
    margin-bottom: 10px;
}

.clip p {
    margin: 5px 0;
}

.clip input[type="text"], .clip textarea {
    width: 100%;
    padding: 5px;
    box-sizing: border-box;
}

.clip button {
    margin-top: 10px;
}
EOF

echo "Создание файла README.md..."
cat > README.md << 'EOF'
# Генератор Виральных Видео

(здесь вставьте содержимое файла README.md)
EOF

echo "Создание файла .gitignore..."
cat > .gitignore << 'EOF'
venv/
__pycache__/
uploads/
clips/
logs/
*.pyc
EOF

echo "Установка завершена."

echo "Запуск приложения..."
python -m uvicorn app.main:app --reload
