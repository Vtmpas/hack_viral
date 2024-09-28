import moviepy.editor as mp
import requests
import os


def extract_audio(video_path: str, audio_path: str):
    """Extract audio from video."""
    try:
        video = mp.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        return audio_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting audio: {str(e)}")

def transcribe_audio(video_path, cache_dir):
    
    # url = "http://localhost:8000/subtitles/"
    url = "http://195.242.25.2:8008/subtitles/"
    model = "base"  # Specify your model here
    audio_file_path = os.path.join(cache_dir, 'audio.wav')
    extract_audio(video_path, audio_file_path)
    # Open the audio file
    with open(audio_file_path, 'rb') as audio_file:
        files = {
            'audio': audio_file,  # Send the audio file
            'request': '{"model": "' + model + '"}'  # Send the model info as a JSON string
        }
        response = requests.post(url, files=files)

    return  response.json()

