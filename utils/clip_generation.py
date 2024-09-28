# utils/clip_generation.py

import subprocess
import logging
import os
import random
from moviepy.editor import VideoFileClip

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

def generate_clips_advanced(video_path, key_moments):
    try:
        original_clips_dir = 'clips/original/'
        os.makedirs(original_clips_dir, exist_ok=True)
        clips = []
        
        video = VideoFileClip(video_path)
        total_duration = video.duration
        
        for idx, moment in enumerate(key_moments):
            start_time = moment['start']
            end_time = moment['end']
            importance_score = moment.get('importance_score', 1)
            
            # Интеллектуальный подбор длительности клипа
            base_duration = min(end_time - start_time, 60)
            adjusted_duration = base_duration * (importance_score / 10)
            clip_duration = max(min(adjusted_duration, 180), 10)
            
            clip_start = max(start_time - (clip_duration - base_duration) / 2, 0)
            clip_end = min(clip_start + clip_duration, total_duration)
            
            if clip_end > total_duration:
                clip_start = max(total_duration - clip_duration, 0)
                clip_end = total_duration
            
            original_clip_path = f"{original_clips_dir}clip_{idx}.mp4"
            
            # Сохранение оригинального фрагмента без эффектов
            original_command = f"ffmpeg -i \"{video_path}\" -ss {clip_start} -to {clip_end} -c copy \"{original_clip_path}\" -y"
            subprocess.call(original_command, shell=True)
            
            clips.append({
                'clip_path': original_clip_path,
                'original_clip_path': original_clip_path,
                'start': clip_start,
                'end': clip_end,
                'duration': clip_end - clip_start,
                'importance_score': importance_score
            })
        
        video.close()
        logger.info(f"Клипы успешно сгенерированы. Всего клипов: {len(clips)}")
        return clips
    except Exception as e:
        logger.exception(f"Ошибка в generate_clips_advanced: {str(e)}")
        raise
