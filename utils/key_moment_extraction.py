# utils/key_moment_extraction.py

import logging
import numpy as np
from sklearn.cluster import DBSCAN
from transformers import AutoTokenizer, AutoModel
import torch
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)

def extract_key_moments_advanced(transcription, video_events):
    try:
        # Загрузка модели для анализа текста
        tokenizer = AutoTokenizer.from_pretrained("DeepPavlov/rubert-base-cased")
        model = AutoModel.from_pretrained("DeepPavlov/rubert-base-cased")
        
        # Извлечение признаков из текста
        text_features = []
        for segment in transcription:
            inputs = tokenizer(segment['text'], return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
            text_features.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())
        
        # Извлечение признаков из видео событий
        video_features = []
        for event in video_events:
            feature = [
                event['timestamp'],
                len(event['objects']),
            ]
            video_features.append(feature)
        
        # Добавим проверку на пустые данные
        if len(text_features) == 0 or len(video_features) == 0:
            logger.warning("Пустые данные для извлечения ключевых моментов")
            return []
        
        # Приведение размерностей к одинаковому количеству элементов
        min_length = min(len(text_features), len(video_features))
        text_features = text_features[:min_length]
        video_features = video_features[:min_length]
        
        # Объединение текстовых и видео признаков
        text_features = np.array(text_features)
        video_features = np.array(video_features)
        
        # Проверка и корректировка размерностей
        if text_features.ndim == 1:
            text_features = text_features.reshape(-1, 1)
        if video_features.ndim == 1:
            video_features = video_features.reshape(-1, 1)
        
        combined_features = np.hstack([text_features, video_features])
        
        # Применение DBSCAN для кластеризации
        dbscan = DBSCAN(eps=0.5, min_samples=3)
        clusters = dbscan.fit_predict(combined_features)
        
        # Поиск пиков в кластерах для определения ключевых моментов
        cluster_scores = np.bincount(clusters[clusters >= 0])
        peaks, _ = find_peaks(cluster_scores, height=np.mean(cluster_scores), distance=5)
        
        # Добавим проверку на отсутствие кластеров
        if len(peaks) == 0:
            logger.warning("Не найдено значимых кластеров для ключевых моментов")
            # Возвращаем несколько равномерно распределенных моментов
            total_duration = transcription[-1]['end'] - transcription[0]['start']
            num_moments = 5  # или другое желаемое количество
            key_moments = []
            for i in range(num_moments):
                start_time = transcription[0]['start'] + (i * total_duration / num_moments)
                end_time = start_time + (total_duration / num_moments)
                key_moments.append({
                    'start': start_time,
                    'end': end_time,
                    'importance_score': 1
                })
        else:
            key_moments = []
            for peak in peaks:
                cluster_indices = np.where(clusters == peak)[0]
                if cluster_indices.size > 0:
                    start_time = transcription[cluster_indices[0]]['start']
                    end_time = transcription[cluster_indices[-1]]['end']
                    
                    # Проверка длительности ключевого момента
                    duration = end_time - start_time
                    if 10 <= duration <= 180:
                        key_moments.append({
                            'start': start_time,
                            'end': end_time,
                            'importance_score': cluster_scores[peak]
                        })
        
        # Сортировка ключевых моментов по важности
        key_moments.sort(key=lambda x: x['importance_score'], reverse=True)
        
        logger.info(f"Извлечено {len(key_moments)} ключевых моментов с использованием расширенного метода")
        return key_moments
    except Exception as e:
        logger.exception(f"Ошибка в extract_key_moments_advanced: {str(e)}")
        # Возвращаем базовый набор ключевых моментов в случае ошибки
        return [{'start': 0, 'end': 10, 'importance_score': 1}]
