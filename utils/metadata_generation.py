# utils/metadata_generation.py

import logging
import json
from openai import OpenAI
import re

logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
base_url = "http://195.242.25.2:8002/v1"
openai_api_key = "EMPTY"
client = OpenAI(
    base_url=base_url,
    api_key=openai_api_key,
)

def generate_metadata_json(transcription):
    try:
        prompt = create_prompt_with_examples(transcription)
        
        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": "Вы - эксперт по анализу видео и генерации метаданных. Создайте метаданные на основе предоставленного описания видео."},
                {"role": "user", "content": prompt}
            ]
        )
        
        metadata_json = completion.choices[0].message.content.strip()
        logger.info(f"Полученный ответ от GPT: {metadata_json}")
        
        # Удаление обрамления Markdown, если оно присутствует
        metadata_json = re.sub(r'^```json\s*|\s*```$', '', metadata_json, flags=re.MULTILINE)
        
        try:
            metadata = json.loads(metadata_json)
            logger.info("Метаданные успешно сгенерированы в формате JSON")
            return metadata
        except json.JSONDecodeError as json_error:
            logger.error(f"Ошибка парсинга JSON: {str(json_error)}")
            logger.error(f"Проблемный JSON: {metadata_json}")
            return {"error": "Ошибка парсинга JSON", "raw_response": metadata_json}
    except Exception as e:
        logger.exception(f"Ошибка в generate_metadata_json: {str(e)}")
        return {"error": str(e)}

def create_prompt_with_examples(transcription):
    examples = [
        {
            "input": "Мастер-класс по приготовлению пасты карбонара. Шеф-повар показывает процесс приготовления классического итальянского блюда, объясняя каждый шаг.",
            "output": {
                "title": "Мастер-класс: Готовим пасту карбонара",
                "description": "Узнайте секреты приготовления классической итальянской пасты карбонара в нашем увлекательном мастер-классе.",
                "hashtags": ["#паста", "#карбонара", "#итальянскаякухня", "#кулинария"],
                "sentiment": "positive",
                "target_audience": "взрослые"
            }
        },
        {
            "input": "Лекция по основам квантовой механики. Профессор объясняет принцип неопределенности Гейзенберга и другие ключевые концепции.",
            "output": {
                "title": "Введение в квантовую механику",
                "description": "Погрузитесь в мир квантовой механики и узнайте о принципе неопределенности Гейзенберга в этой увлекательной лекции.",
                "hashtags": ["#квантоваямеханика", "#физика", "#наука", "#Гейзенберг"],
                "sentiment": "neutral",
                "target_audience": "взрослые"
            }
        }
    ]
    
    prompt = "На основе следующих примеров сгенерируйте метаданные для нового видео в формате JSON:\n\n"
    for example in examples:
        prompt += f"Описание видео: {example['input']}\n"
        prompt += f"Метаданные: {json.dumps(example['output'], ensure_ascii=False)}\n\n"
    
    prompt += f"Теперь сгенерируйте метаданные для этого видео:\n"
    prompt += f"Описание видео: {transcription}\n"
    prompt += "Метаданные:"
    
    return prompt

if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)

    sample_transcription = "Зрителей настиг потоп из -за тропического ливня, который накрыл курортный город. Ну, всякое журналистское быдло и дебилы будут объяснять это погодой. А я скажу, что Стас Михайлов просто решил экранизировать моё любимое аниме Детройт Метал Сити. Смотрите! Токийская башня потекла! Токийская башня кончила!"

    metadata = generate_metadata_json(sample_transcription)
    print("Сгенерированные метаданные:")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))