from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import whisper
import tempfile
import os
import torch
import logging

# Initialize the FastAPI app
app = FastAPI()

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Determine if CUDA is available for model acceleration
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"Device selected: {device}")
print(f"Device selected: {device}")

# Load the Whisper model
model = whisper.load_model("base", device=device)
logging.info("Whisper model loaded")
print("Whisper model loaded")

# Define a Pydantic model for request validation
class Request(BaseModel):
    model: str = "base"  # Available options: tiny, base, small, medium, large

# Function to split subtitles by individual words
def split_subs_by_words(result):
    '''
    Convert JSON from Whisper to a word-level subtitle format.
    '''
    logging.info("Splitting subtitles by words")
    print("Splitting subtitles by words")
    
    subtitles = []
    for segment in result['segments']:
        for word_info in segment['words']:
            word_info['text'] = word_info.pop('word')  # Rename 'word' to 'text'
            subtitles.append(word_info)
    
    logging.info("Word-level subtitles generated")
    print("Word-level subtitles generated")
    
    return subtitles

# Function to split subtitles by sentences
def split_subs_by_sentences(result):
    '''
    Convert JSON from Whisper to a sentence-level subtitle format.
    '''
    logging.info("Splitting subtitles by sentences")
    print("Splitting subtitles by sentences")
    
    subtitles = []
    current_sentence = []
    current_start = None
    current_end = None
    punctuation_marks = {'.', '!', '?', '...', '…'}  # Sentence-ending punctuation

    for segment in result['segments']:
        for word_info in segment['words']:
            word = word_info['word'].strip()
            start = word_info['start']
            end = word_info['end']

            if current_start is None:
                current_start = start  # Mark the start of the sentence

            current_sentence.append(word)
            current_end = end  # Update end time for the sentence

            if word[-1] in punctuation_marks:  # Sentence complete
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
    
    logging.info("Sentence-level subtitles generated")
    print("Sentence-level subtitles generated")
    
    return subtitles

# Endpoint for generating subtitles
@app.post("/subtitles/")
async def get_subtitles(audio: UploadFile = File(...)):
    '''
    Receives an audio file and generates both word-level and sentence-level subtitles.
    '''
    logging.info(f"Received audio file: {audio.filename}")
    print(f"Received audio file: {audio.filename}")

    # Create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            logging.info("Saving audio file to temporary location")
            print("Saving audio file to temporary location")
            
            # Write the audio data to the temporary file
            audio_data = await audio.read()
            temp_file.write(audio_data)
            temp_file_path = temp_file.name  # Get the temporary file path
        except Exception as e:
            logging.error(f"Error saving audio to temp file: {str(e)}")
            print(f"Error saving audio to temp file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving audio to temp file: {str(e)}")

    # Transcribe the audio using Whisper
    try:
        logging.info("Starting transcription using Whisper")
        print("Starting transcription using Whisper")
        
        subtitles = model.transcribe(temp_file_path, word_timestamps=True)  # Pass the temp file path to the model
        
        logging.info("Transcription completed")
        print("Transcription completed")
    except Exception as e:
        logging.error(f"Error transcribing audio with Whisper: {str(e)}")
        print(f"Error transcribing audio with Whisper: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio with Whisper: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)  # Delete the temporary file
            logging.info("Temporary audio file deleted")
            print("Temporary audio file deleted")

    # Generate sentence-level and word-level subtitles
    sentences = split_subs_by_sentences(subtitles.copy())
    words = split_subs_by_words(subtitles.copy())

    logging.info("Returning subtitles response")
    print("Returning subtitles response")
    
    return {
        'sentences': sentences,
        'words': words,
    }

# Main entry point for running the app
if __name__ == "__main__":
    import uvicorn
    logging.info("Starting the FastAPI server")
    print("Starting the FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
