# utils/speech_processing.py

import os
import subprocess
import logging
import torch
import torchaudio
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence

logger = logging.getLogger(__name__)

def transcribe_audio_advanced(video_path):
    try:
        # Извлечение аудио
        audio_path = extract_audio(video_path)
        
        # Загрузка модели и процессора Wav2Vec2
        model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
        processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
        
        # Загрузка и предобработка аудио
        waveform, sample_rate = torchaudio.load(audio_path)
        waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
        
        # Разделение аудио на чанки
        audio = AudioSegment.from_wav(audio_path)
        chunks = split_on_silence(audio, min_silence_len=500, silence_thresh=-40)
        
        transcription = []
        current_time = 0
        
        for chunk in chunks:
            chunk_duration = len(chunk) / 1000.0  # длительность в секундах
            chunk_array = np.array(chunk.get_array_of_samples())
            
            # Нормализация входных данных
            input_values = processor(chunk_array, sampling_rate=16000, return_tensors="pt").input_values
            
            # Получение логитов
            with torch.no_grad():
                logits = model(input_values).logits
            
            # Декодирование предсказаний
            predicted_ids = torch.argmax(logits, dim=-1)
            transcribed_text = processor.batch_decode(predicted_ids)[0]
            
            transcription.append({
                'text': transcribed_text,
                'start': current_time,
                'end': current_time + chunk_duration
            })
            
            current_time += chunk_duration
        
        logger.info("Аудио успешно транскрибировано с использованием Wav2Vec2")
        return transcription
    except Exception as e:
        logger.exception("Ошибка в transcribe_audio_advanced")
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
