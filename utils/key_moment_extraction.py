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
                len(event['detected_objects']),
                event['scene_classification']
            ]
            video_features.append(feature)
        
        # Объединение текстовых и видео признаков
        combined_features = np.hstack([np.array(text_features), np.array(video_features)])
        
        # Применение DBSCAN для кластеризации
        dbscan = DBSCAN(eps=0.5, min_samples=3)
        clusters = dbscan.fit_predict(combined_features)
        
        # Поиск пиков в кластерах для определения ключевых моментов
        cluster_scores = np.bincount(clusters[clusters >= 0])
        peaks, _ = find_peaks(cluster_scores, height=np.mean(cluster_scores), distance=5)
        
        key_moments = []
        for peak in peaks:
            cluster_indices = np.where(clusters == peak)[0]
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
        logger.exception("Ошибка в extract_key_moments_advanced")
        raise
