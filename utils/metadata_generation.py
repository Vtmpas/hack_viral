# utils/metadata_generation.py

import logging
from transformers import pipeline
from collections import Counter
import re

logger = logging.getLogger(__name__)

def generate_metadata_advanced(transcription, key_moments, video_events):
    try:
        # Инициализация модели генерации текста
        text_generator = pipeline("text-generation", model="sberbank-ai/rugpt3large_based_on_gpt2")
        
        metadata = []
        for moment in key_moments:
            # Получение текста для данного ключевого момента
            moment_text = get_moment_text(transcription, moment['start'], moment['end'])
            
            # Генерация названия
            title = generate_title(text_generator, moment_text)
            
            # Генерация описания
            description = generate_description(text_generator, moment_text)
            
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
        
        logger.info("Метаданные успешно сгенерированы с использованием расширенных методов")
        return metadata
    except Exception as e:
        logger.exception("Ошибка в generate_metadata_advanced")
        raise

def get_moment_text(transcription, start_time, end_time):
    return ' '.join([t['text'] for t in transcription if start_time <= t['start'] < end_time or start_time < t['end'] <= end_time])

def generate_title(text_generator, text):
    prompt = f"Создайте короткое и привлекательное название для видео на основе следующего текста: {text[:100]}..."
    generated_title = text_generator(prompt, max_length=50, num_return_sequences=1)[0]['generated_text']
    return generated_title.split('\n')[1]  # Берем вторую строку, так как первая - это промпт

def generate_description(text_generator, text):
    prompt = f"Напишите краткое и интересное описание для видео на основе следующего текста: {text[:200]}..."
    generated_description = text_generator(prompt, max_length=200, num_return_sequences=1)[0]['generated_text']
    return generated_description.split('\n', 1)[1]  # Берем текст после первой строки

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
    # Простой анализ настроения на основе ключевых слов
    positive_words = set(['хорошо', 'отлично', 'прекрасно', 'замечательно', 'великолепно'])
    negative_words = set(['плохо', 'ужасно', 'отвратительно', 'неприятно', 'ужасающе'])
    
    words = set(text.lower().split())
    positive_count = len(words.intersection(positive_words))
    negative_count = len(words.intersection(negative_words))
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'

def determine_target_audience(text, video_events):
    # Простое определение целевой аудитории на основе контента
    keywords = {
        'дети': ['ребенок', 'дети', 'школа', 'игрушки'],
        'подростки': ['подросток', 'школа', 'тренды', 'музыка'],
        'взрослые': ['работа', 'бизнес', 'финансы', 'политика'],
        'пожилые люди': ['пенсия', 'здоровье', 'сад', 'внуки']
    }
    
    audience_scores = {audience: 0 for audience in keywords}
    
    # Анализ текста
    for audience, words in keywords.items():
        for word in words:
            if word in text.lower():
                audience_scores[audience] += 1
    
    # Анализ объектов в видео
    for event in video_events:
        for obj in event['detected_objects']:
            for audience, words in keywords.items():
                if obj['label'] in words:
                    audience_scores[audience] += 1
    
    # Определение наиболее подходящей аудитории
    target_audience = max(audience_scores, key=audience_scores.get)
    return target_audience
