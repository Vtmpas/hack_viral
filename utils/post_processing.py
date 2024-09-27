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

def process_clips_advanced(clips, transcription):
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

            # Добавляем субтитры с анимацией
            txt_clip = TextClip(text, fontsize=50, color='white', bg_color='rgba(0,0,0,0.5)', size=video.size, method='caption')
            txt_clip = txt_clip.set_duration(video.duration).set_position(('center', 'bottom')).set_start(0.5)  # Задержка появления текста

            # Добавляем эмодзи с анимацией
            emoji_files = ['utils/emoji.png']  # Можно добавить больше эмодзи
            emoji_path = random.choice(emoji_files)
            emoji = ImageClip(emoji_path).set_duration(video.duration)
            emoji = emoji.set_position(('right', 'top')).resize(height=100).set_start(1)  # Задержка появления эмодзи

            # Добавляем эффект перехода
            if 'effect' in clip_info:
                if clip_info['effect'] == 'fade':
                    video = video.fadeout(1)
                elif clip_info['effect'] == 'speed':
                    video = video.speedx(factor=clip_info.get('speed', 1.5))

            # Композиция видео
            final = CompositeVideoClip([video, txt_clip, emoji])
            final.write_videofile(processed_clip_path, codec='libx264', audio_codec='aac', fps=24, threads=4)
            processed_clips.append({'processed_clip_path': processed_clip_path})
        logger.info("Клипы успешно постобработаны с расширенными возможностями")
        return processed_clips
    except Exception as e:
        logger.exception("Ошибка в process_clips_advanced")
        raise

def get_clip_transcription(transcription, start_time, end_time):
    clip_transcription = []
    for t in transcription:
        if t['end'] >= start_time and t['start'] <= end_time:
            clip_transcription.append(t)
    return clip_transcription
