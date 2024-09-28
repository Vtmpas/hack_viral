# utils/video_analysis.py

import cv2
import logging
import numpy as np
import torch
from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_320_fpn
from transformers import AutoFeatureExtractor
import psutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Загрузка моделей один раз при импорте модуля
object_detection_model = fasterrcnn_mobilenet_v3_large_320_fpn(pretrained=True).eval()
feature_extractor = AutoFeatureExtractor.from_pretrained("microsoft/resnet-18")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
object_detection_model.to(device)

def preprocess_image(frame):
    return cv2.resize(frame, (800, 800))

async def check_available_memory():
    return psutil.virtual_memory().percent < 90

def process_frame(frame, timestamp):
    image = preprocess_image(frame)
    with torch.no_grad():
        predictions = object_detection_model([torch.from_numpy(image).permute(2, 0, 1).float().to(device)])
    
    objects = []
    for box, label, score in zip(predictions[0]['boxes'], predictions[0]['labels'], predictions[0]['scores']):
        if score > 0.5:
            objects.append({
                'label': COCO_INSTANCE_CATEGORY_NAMES[label],
                'score': float(score),
                'box': box.tolist()
            })
    
    return {
        'timestamp': timestamp,
        'objects': objects
    }

async def analyze_video_advanced(video_path, step=30):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    video_events = []
    with ThreadPoolExecutor() as executor:
        for frame_count in range(0, total_frames, step):
            if not await check_available_memory():
                break
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count)
            ret, frame = cap.read()
            if not ret:
                break
            
            timestamp = frame_count / fps
            event = await asyncio.get_event_loop().run_in_executor(
                executor, process_frame, frame, timestamp
            )
            video_events.append(event)
            
            logger.debug(f"Обработан кадр {frame_count}/{total_frames}, найдено объектов: {len(event['objects'])}")
            
            await asyncio.sleep(0)
    
    logger.info(f"Всего обработано кадров: {len(video_events)}, найдено объектов: {sum(len(e['objects']) for e in video_events)}")
    cap.release()
    return video_events

# Остальные функции остаются без изменений

COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'TV', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair dryer', 'toothbrush'
]