from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import whisper
import tempfile
import os
import torch


app = FastAPI()

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)

class Request(BaseModel):
    model: str = "base"  # (tiny, base, small, medium, large)

def split_subs_by_words(result):
    subtitles = []
    for segment in result['segments']:
        for word_info in segment['words']:
            word_info['text'] = word_info.pop('word')
            subtitles.append(word_info)
    return subtitles

def split_subs_by_sentences(result):
    subtitles = []
    current_sentence = []
    current_start = None
    current_end = None
    punctuation_marks = {'.', '!', '?', '...', '…'}

    for segment in result['segments']:
        for word_info in segment['words']:
            word = word_info['word'].strip()
            start = word_info['start']
            end = word_info['end']

            if current_start is None:
                current_start = start

            current_sentence.append(word)
            current_end = end

            if word[-1] in punctuation_marks:
                sentence = ' '.join(current_sentence)
                subtitles.append({
                    'text': sentence,
                    'start': current_start,
                    'end': current_end
                })
                current_sentence = []
                current_start = None
                current_end = None

    # Handle any remaining words that didn't end with punctuation
    if current_sentence:
        sentence = ' '.join(current_sentence)
        subtitles.append({
            'text': sentence,
            'start': current_start,
            'end': current_end
        })
    return subtitles

@app.post("/subtitles/")
async def get_subtitles(audio: UploadFile = File(...)):
    # Create a temporary file to store the audio
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            # Write the audio data to the temporary file
            audio_data = await audio.read()
            temp_file.write(audio_data)
            temp_file_path = temp_file.name  # Get the temporary file path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving audio to temp file: {str(e)}")

    # Transcribe audio using Whisper
    try:
        subtitles = model.transcribe(temp_file_path, word_timestamps=True)  # Pass the temp file path to the model
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio with Whisper: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)  # Delete the temporary file


    sentences = split_subs_by_sentences(subtitles.copy())
    words = split_subs_by_words(subtitles.copy())

    return {
        'sentences': sentences,
        'words': words,
    }

# if __name__ == "__main__":
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)