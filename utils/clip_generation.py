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
