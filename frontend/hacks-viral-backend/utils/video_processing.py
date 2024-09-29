from moviepy.video.io.VideoFileClip import VideoFileClip
from io import BytesIO
import tempfile
import os

def split_video_into_parts(file_location: str, num_parts: int = 10):
    clip = VideoFileClip(file_location)
    duration = clip.duration
    part_duration = duration / num_parts
    parts = []
    for i in range(num_parts):
        start_time = i * part_duration
        end_time = (i + 1) * part_duration
        part_clip = clip.subclip(start_time, end_time)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file_path = temp_file.name
            part_clip.write_videofile(temp_file_path, codec="libx264", audio_codec="aac")
        
        with open(temp_file_path, "rb") as f:
            part_buffer = BytesIO(f.read())
            part_buffer.seek(0)
            parts.append(part_buffer)
        
        os.remove(temp_file_path)
    return parts
