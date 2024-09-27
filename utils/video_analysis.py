# utils/video_analysis.py

import cv2
import logging
import numpy as np
import torch
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.transforms import functional as F
from transformers import AutoFeatureExtractor, AutoModelForImageClassification

logger = logging.getLogger(__name__)

def analyze_video_advanced(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        
        # Загрузка моделей
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        object_detection_model = fasterrcnn_resnet50_fpn(pretrained=True).to(device)
        object_detection_model.eval()
        
        scene_classification_extractor = AutoFeatureExtractor.from_pretrained("microsoft/resnet-50")
        scene_classification_model = AutoModelForImageClassification.from_pretrained("microsoft/resnet-50").to(device)
        scene_classification_model.eval()
        
        video_events = []
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # в секундах
            
            if frame_idx % int(frame_rate) == 0:  # анализируем каждый секундный кадр
                # Подготовка изображения для object detection
                img_tensor = F.to_tensor(frame).unsqueeze(0).to(device)
                
                # Object detection
                with torch.no_grad():
                    object_detection_output = object_detection_model(img_tensor)[0]
                
                detected_objects = []
                for box, label, score in zip(object_detection_output['boxes'], object_detection_output['labels'], object_detection_output['scores']):
                    if score > 0.5:  # фильтруем объекты с низкой уверенностью
                        detected_objects.append({
                            'label': label.item(),
                            'score': score.item(),
                            'box': box.tolist()
                        })
                
                # Scene classification
                inputs = scene_classification_extractor(images=frame, return_tensors="pt").to(device)
                with torch.no_grad():
                    scene_output = scene_classification_model(**inputs)
                
                scene_logits = scene_output.logits
                scene_pred = torch.argmax(scene_logits, dim=1).item()
                
                video_events.append({
                    'timestamp': timestamp,
                    'detected_objects': detected_objects,
                    'scene_classification': scene_pred
                })
            
            frame_idx += 1
        
        cap.release()
        logger.info("Видео успешно проанализировано с расширенными возможностями")
        return video_events
    except Exception as e:
        logger.exception("Ошибка в analyze_video_advanced")
        raise
