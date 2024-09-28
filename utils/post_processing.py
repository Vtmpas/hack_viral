# utils/post_processing.py

import logging
import os
import subprocess
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

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
            # Используем 'original_clip_path' вместо 'clip_path'
            clip_path = clip_info['original_clip_path']
            start_time = clip_info['start']
            end_time = clip_info['end']

            # Находим соответствующий текст для клипа
            clip_text = extract_clip_text(transcription, start_time, end_time)

            # Добавляем текст к видео
            processed_clip_path = add_text_to_video(clip_path, clip_text, processed_clips_dir, idx)

            processed_clips.append({
                'processed_clip_path': processed_clip_path,
                'start': start_time,
                'end': end_time,
                'text': clip_text
            })

        logger.info(f"Постобработка завершена. Обработано клипов: {len(processed_clips)}")
        return processed_clips
    except Exception as e:
        logger.exception(f"Ошибка в process_clips_advanced: {str(e)}")
        raise

def get_clip_transcription(transcription, start_time, end_time):
    clip_transcription = []
    for t in transcription:
        if t['end'] >= start_time and t['start'] <= end_time:
            clip_transcription.append(t)
    return clip_transcription

def extract_clip_text(transcription, start_time, end_time):
    clip_text = ""
    for segment in transcription:
        if segment['start'] >= start_time and segment['end'] <= end_time:
            clip_text += segment['text'] + " "
    return clip_text.strip()

def add_text_to_video(clip_path, text, output_dir, idx):
    try:
        video = VideoFileClip(clip_path)
        text_clip = TextClip(text, fontsize=24, color='white', bg_color='black', size=(video.w, None))
        text_clip = text_clip.set_position(('center', 'bottom')).set_duration(video.duration)

        final_clip = CompositeVideoClip([video, text_clip])
        output_path = os.path.join(output_dir, f"clip_{idx}.mp4")
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

        return output_path
    except Exception as e:
        logger.exception(f"Ошибка при добавлении текста к видео: {str(e)}")
        return clip_path  # Возвращаем оригинальный путь в случае ошибки
