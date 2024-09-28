# utils/metadata_generation.py

import logging
from collections import Counter
import re
from openai import OpenAI

logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
base_url = "http://195.242.25.2:8002/v1"
openai_api_key = "EMPTY"
client = OpenAI(
    base_url=base_url,
    api_key=openai_api_key,
)

def generate_metadata_advanced(transcription, key_moments, video_events):
    try:
        metadata = []
        for moment in key_moments:
            try:
                # Получение текста для данного ключевого момента
                moment_text = get_moment_text(transcription, moment['start'], moment['end'])
                
                # Генерация названия
                title = generate_title(moment_text)
                
                # Генерация описания
                description = generate_description(moment_text)
                
                # Генерация хэштегов
                hashtags = generate_hashtags(moment_text, video_events)
                
                # Анализ эмоциональной окраски
                sentiment = analyze_sentiment(moment_text)
                
                # Определение целевой аудитории
                target_audience = determine_target_audience(moment_text, video_events)
                
                metadata.append({
                    'title': title,
                    'description': description,
                    'hashtags': hashtags,
                    'sentiment': sentiment,
                    'target_audience': target_audience,
                    'start_time': moment['start'],
                    'end_time': moment['end'],
                    'importance_score': moment.get('importance_score', 0)
                })
            except Exception as e:
                logger.error(f"Ошибка при обработке момента: {str(e)}")
                # Добавляем базовые метаданные в случае ошибки
                metadata.append({
                    'title': 'Без названия',
                    'description': 'Описание недоступно',
                    'hashtags': [],
                    'sentiment': 'neutral',
                    'target_audience': 'general',
                    'start_time': moment['start'],
                    'end_time': moment['end'],
                    'importance_score': moment.get('importance_score', 0)
                })
        
        logger.info("Метаданные успешно сгенерированы с использованием расширенных методов")
        return metadata
    except Exception as e:
        logger.exception(f"Ошибка в generate_metadata_advanced: {str(e)}")
        # Возвращаем пустой список метаданных в случае критической ошибки
        return []

def get_moment_text(transcription, start_time, end_time):
    return ' '.join([t['text'] for t in transcription if start_time <= t['start'] < end_time or start_time < t['end'] <= end_time])

def generate_title(moment_text):
    prompt = f"Придумайте короткое и привлекательное название для видео на основе следующего текста: {moment_text}\nНазвание:"
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-32B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    title = completion.choices[0].message.content.strip()
    return title[:50]  # Ограничиваем длину названия 50 символами

def generate_description(moment_text):
    prompt = f"Напишите краткое описание видео на основе следующего текста: {moment_text}\nОписание:"
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-32B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    description = completion.choices[0].message.content.strip()
    return description[:200]  # Ограничиваем длину описания 200 символами

def generate_hashtags(text, video_events):
    # Извлечение ключевых слов из текста
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)
    
    # Добавление информации о объектах из видео
    for event in video_events:
        for obj in event['detected_objects']:
            word_freq[obj['label']] += 1
    
    # Фильтрация общих слов
    common_words = set(['и', 'в', 'на', 'с', 'по', 'а', 'что', 'это', 'из', 'не', 'для', 'к', 'то'])
    hashtags = [f"#{word}" for word, freq in word_freq.most_common(10) if word not in common_words and len(word) > 3]
    
    return hashtags

def analyze_sentiment(text):
    prompt = f"Проанализируйте эмоциональную окраску следующего текста и ответьте одним словом (positive, negative или neutral): {text}"
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-32B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    sentiment = completion.choices[0].message.content.strip().lower()
    return sentiment if sentiment in ['positive', 'negative', 'neutral'] else 'neutral'

def determine_target_audience(text, video_events):
    prompt = f"Определите целевую аудиторию для видео на основе следующего текста и объектов. Ответьте одним словом (дети, подростки, взрослые или пожилые_люди): Текст: {text}, Объекты: {[obj['label'] for event in video_events for obj in event['detected_objects']]}"
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-32B-Instruct",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    target_audience = completion.choices[0].message.content.strip().lower()
    valid_audiences = ['дети', 'подростки', 'взрослые', 'пожилые_люди']
    return target_audience if target_audience in valid_audiences else 'general'
