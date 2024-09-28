# utils/video_analysis.py

import json
from openai import OpenAI
import ast
from typing import List, Set, Dict, Any
import re

def truncate_text(text: str, max_tokens: int = 30000) -> str:
    return text[:max_tokens * 4]  # Грубая оценка: 1 токен ~ 4 символа

def extract_labels_from_response(response: str) -> List[str]:
    # Попытка разобрать JSON
    try:
        data = json.loads(response)
        if isinstance(data, dict) and "labels" in data:
            return [label for label in data["labels"] if label.lower() != "labels"]
    except json.JSONDecodeError:
        pass

    # Попытка извлечь список с помощью ast
    try:
        data = ast.literal_eval(response)
        if isinstance(data, list):
            return [label for label in data if label.lower() != "labels"]
        elif isinstance(data, dict) and "labels" in data:
            return [label for label in data["labels"] if label.lower() != "labels"]
    except (SyntaxError, ValueError):
        pass

    # Извлечение меток с помощью регулярных выражений
    labels = re.findall(r'"([^"]+)"', response)
    if labels:
        return [label for label in labels if label.lower() != "labels"]

    # Если все методы не сработали, разделяем по запятым и новым строкам
    return [label.strip() for label in re.split(r'[,\n]', response) if label.strip().lower() != "labels"]

def generate_candidate_labels(transcript: str) -> List[str]:
    base_url = "http://195.242.25.2:8002/v1"
    openai_api_key = "EMPTY"
    client = OpenAI(base_url=base_url, api_key=openai_api_key)

    system_prompt = """Ты - помощник по анализу видео. Твоя задача - создать список возможных меток для классификации ключевых моментов в видео на основе предоставленного транскрипта. Метки должны быть краткими (1-3 слова) и отражать основные темы или события в видео и быть весьма конкретными. Верни список из 5-10 меток в формате JSON.

Пример ответа. Всегда отвечай на русском:
{
    "labels": [
        "Рассказы о спорте",
        "Виды спорта для богатых",
        "Гольф",
        "БАДы",
    ]
}"""

    user_prompt = f"Создай список меток для классификации на основе этого транскрипта:\n\n{transcript}"

    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    response = completion.choices[0].message.content
    return extract_labels_from_response(response)

def process_transcript_with_rolling_window(transcript: str, window_size: int = 30000, overlap: float = 0.5) -> Set[str]:
    words = transcript.split()
    step = int(window_size * (1 - overlap))
    all_labels = set()

    for i in range(0, len(words), step):
        window = " ".join(words[i:i + window_size])
        truncated_window = truncate_text(window, window_size)
        labels = generate_candidate_labels(truncated_window)
        all_labels.update(labels)

    return all_labels

def process_transcript_with_highlights_and_emoji(transcript: Dict[str, Any], emoji_dict: Dict[str, str]) -> Dict[str, List[Dict[str, Any]]]:
    base_url = "http://195.242.25.2:8002/v1"
    openai_api_key = "EMPTY"
    client = OpenAI(base_url=base_url, api_key=openai_api_key)

    system_prompt = """Ты - помощник п анализу видео. Твоя задача - обработать предоставленное предложение из транскрипта, выделяя ключевые слова  и добавляя эмодзи. Выделяй слова, которые имеют большое эмоциональное или смысловое значение. Не меняй форму слов из предложения. Добавляй эмодзи, отражающие общую тему предложения. Используй контекст из предыдущих предложений для лучшего понимания.

Пример входных данных:
{
  "context": [
    "Вчера я ходил в парк.",
    "Погода была отличная.",
    "Я встретил там своего друга.",
    "Мы решили поиграть в футбол."
  ],
  "current_sentence": {
    "start": 15.6,
    "end": 20.3,
    "text": "Это была очень увлекательная игра, мы отлично провели время."
  }
}

Примеры выходных данных:
1. Четкое определение темы и эмодзи:
{
  "text": "Это была очень увлекательная игра, мы отлично провели время.",
  "highlights": ["*увлекательная*", "*отлично провели время*"],
  "emoji": {
    "theme": "развлечение",
    "emoji_name": "футбольный мяч"
  }
}

2. Неопределенная тема или эмодзи:
{
  "text": "Погода сегодня неоднозначная.",
  "highlights": ["*неоднозначная*"],
  "emoji": null
}

3. Отсутствие ключевых слов:
{
  "text": "Ну да, ладно.",
  "highlights": [],
  "emoji": null
}

Обрати внимание на следующие особые случаи:
1. Если в предложении нет явных ключевых слов, оставь список highlights пустым.
2. Если тема предложения неопределенная или нет подходящего эмодзи, используй null для всего поля emoji.
3. Если ты не уверен в выборе темы или эмодзи, используй null для всего поля emoji.

Всегда отвечай в формате JSON."""

    processed_sentences = []
    context = []

    for i, sentence in enumerate(transcript["sentences"]):
        input_data = {
            "context": context,
            "current_sentence": sentence
        }
        user_prompt = f"Обработай это предложение, выделяя ключевые слова и добавляя эмодзи:\n\n{json.dumps(input_data, ensure_ascii=False)}"

        completion = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.
        )

        response = completion.choices[0].message.content
        try:
            processed_sentence = json.loads(response)
            
            # Добавляем start и end из исходного предложения
            processed_sentence["start"] = sentence["start"]
            processed_sentence["end"] = sentence["end"]
            
            # Проверяем, нужно ли добавлять эмодзи
            if processed_sentence["emoji"] is not None:
                emoji_name = processed_sentence["emoji"].get("emoji_name")
                if emoji_name:
                    # Если emoji_name - список, берем первый элемент
                    if isinstance(emoji_name, list):
                        emoji_name = emoji_name[0] if emoji_name else None
                    
                    if emoji_name:
                        processed_sentence["emoji"]["emoji_path"] = emoji_dict.get(emoji_name, emoji_dict["default emoji"])
                        del processed_sentence["emoji"]["emoji_name"]
                        
                        # Рассчитываем временные метки для эмодзи
                        if i < len(transcript["sentences"]) - 1:
                            next_sentence = transcript["sentences"][i + 1]
                            if next_sentence["start"] - sentence["end"] > 1:
                                processed_sentence["emoji"]["start"] = sentence["end"]
                                processed_sentence["emoji"]["end"] = sentence["end"] + 0.5
                            else:
                                processed_sentence["emoji"] = None
                        else:
                            # Для последнего предложения
                            processed_sentence["emoji"]["start"] = sentence["end"]
                            processed_sentence["emoji"]["end"] = sentence["end"] + 0.5
                    else:
                        processed_sentence["emoji"] = None
                else:
                    processed_sentence["emoji"] = None
            
            processed_sentences.append(processed_sentence)
        except json.JSONDecodeError:
            print(f"Ошибка при разборе JSON ответа для предложения: {sentence['text']}. Пропускаем это предложение.")
            continue

        # Обновляем контекст
        context.append(sentence["text"])
        if len(context) > 5:
            context.pop(0)

    return {"sentences": processed_sentences}

if __name__ == "__main__":
    with open('/Users/matvejsaprykin/Downloads/test2.json', 'r', encoding='utf-8') as file:
        sample_transcription = json.load(file)

    emoji_dict = {"default emoji": "/Users/matvejsaprykin/Desktop/hack_viral/emoji — копия.png"}
    processed_transcript = process_transcript_with_highlights_and_emoji(sample_transcription, emoji_dict)
    
    print("Обработанный транскрипт:")
    print(json.dumps(processed_transcript, ensure_ascii=False, indent=2))

    # Существующий код для генерации меток
    full_transcript = " ".join([segment["text"] for segment in sample_transcription["sentences"]])
    all_labels = process_transcript_with_rolling_window(full_transcript)
    print("Уникальные метки: " + str(all_labels))