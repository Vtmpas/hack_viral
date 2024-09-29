## How to run
```bash
docker compose up --build
```

## Request Example 
```python
import requests

url = "http://x.x.x.x:8008/subtitles/"
audio_file_path = "audios/test_audio.wav"  # Path to your audio file

# Open the audio file
with open(audio_file_path, 'rb') as audio_file:
    files = {
        'audio': audio_file,  # Send the audio file
    }
    response = requests.post(url, files=files)

# Check the response
if response.status_code == 200:
    print(response.json())  # Successfully received a response
else:
    print(f"Error: {response.status_code} - {response.text}")
```
