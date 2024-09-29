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

## Example Output

```
{
    "sentences": [
        {
            "text": "Один Два Три",
            "start": 3.44,
            "end": 5.64
        }
    ],
    "words": [
        {
            "start": 3.44,
            "end": 3.98,
            "probability": 0.554,
            "text": "Один"
        },
        {
            "start": 3.98,
            "end": 4.98,
            "probability": 0.898,
            "text": "Два"
        },
        {
            "start": 4.98,
            "end": 5.64,
            "probability": 0.936,
            "text": "Три"
        }
    ]
}
```
