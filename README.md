# Создание виральных клипов

<table>
  <tr>
    <td><img src="assets/start_page.jpg" alt="start_page_preview" width="400"/></td>
    <td><img src="assets/upload_page.jpg" alt="upload_page_preview" width="400"/></td>
  </tr>
  <tr>
    <td><img src="assets/progress.jpg" alt="progress_preview" width="400"/></td>
    <td><img src="assets/result.jpg" alt="result_preview" width="400"/></td>
  </tr>
</table>

## Требования
## Установка и запуск

Следуйте этим шагам для запуска всех необходимых сервисов.
### 1. Запуск сервиса API
```bash
cd api
docker compose up --build -d
```
### 2. Запуск модели Qwen2.5 7b VLLM
```bash
cd qwen_vllm
docker compose up --build -d
```
### 3. Запуск сервиса API Whisper
```bash
cd api-whisper
docker compose up --build -d
```
### 4. Запуск frontend 
```bash
cd frontend
docker compose up -d --build
```
