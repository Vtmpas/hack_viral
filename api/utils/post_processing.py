import subprocess
import json
import imageio
from PIL import Image
import numpy as np
import moviepy.editor as mpe
from moviepy.editor import *
import cv2
from moviepy.video.fx.all import crop
def get_video_metadata(video_path):
    # Run ffprobe command
    command = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # Parse the result as JSON
    metadata = json.loads(result.stdout)
    return metadata

def save_video(clips, video_path, cache_dir):
    paths = []
    target_aspect_ratio=9/16
    for i, clip in enumerate(clips):
        start = clip['start']
        end = clip['end']
        output_file = os.path.join(cache_dir, 'video' + str(i) + '.mp4')
        
        if os.path.exists(output_file):
            os.remove(output_file)
        output_file2 = os.path.join(cache_dir, 'video_' + str(i) + '.mp4')
        
        if os.path.exists(output_file2):
            os.remove(output_file2)
        reader = imageio.get_reader(video_path)
        original_width, original_height = reader.get_meta_data()['size']
        try:
            if original_width == original_height:
                aspect_ratio = get_video_metadata(video_path=video_path)['streams'][0]['sample_aspect_ratio']
                aspect_ratio_w, aspect_ratio_h = int(aspect_ratio.split(':')[0]), int(aspect_ratio.split(':')[1])
                if aspect_ratio_w > aspect_ratio_h:
                    original_width = int((original_width / aspect_ratio_h) * aspect_ratio_w)
                else:
                    original_height = int((original_height / aspect_ratio_w) * aspect_ratio_h)
                use_convert=True
            else:
                use_convert=False
        except Exception as e:
            print(e)
            use_convert = False
        if original_width / original_height > target_aspect_ratio:
            new_width = int(original_height * target_aspect_ratio) // 16 * 16
            x1 = (original_width - new_width) // 2
            x2 = x1 + new_width
            y1, y2 = 0, original_height
        else:
            new_height = int(original_width / target_aspect_ratio)
            y1 = (original_height - new_height) // 2
            y2 = y1 + new_height
            x1, x2 = 0, original_width
        #"crop=640:480:0:0"
        height = y2 - y1
        width = x2 - x1
        crop_size = f"crop={width}:{height}:{x1}:{y1}"
        print('[y1:y2, x1:x2]', y1,y2, x1, x2, crop_size)
        print('use_convert', use_convert)
        if use_convert:
            command = f'''ffmpeg -i {video_path}  -ss {start} -to {end} -c:v libx264 -threads 128 -vf "scale={original_width}:{original_height}" -c:a  copy {output_file}'''
            subprocess.call(command, shell=True)
            command = f'''ffmpeg -i {output_file} -threads 128 -vf "{crop_size}" {output_file2}'''
            subprocess.call(command, shell=True)
            paths.append(output_file2)
        else:
            command = f'''ffmpeg -i "{video_path}" -ss {start} -to {end} -threads 128 -vf "{crop_size}" {output_file}'''
            subprocess.call(command, shell=True)
            paths.append(output_file)  
    return paths


def crop_video_to_9_16(input_video_path, output_video_path, background_audio_path=None, target_aspect_ratio=9/16, words=None):
    if 1:
        reader = imageio.get_reader(input_video_path)
        mp_clip = mpe.VideoFileClip(input_video_path)
        fps = reader.get_meta_data()['fps']
        original_width, original_height = reader.get_meta_data()['size']
        print('original_width, original_height111', original_width, original_height)
        cropped_clip = mp_clip#crop(mp_clip, x1=x1, y1=y1, x2=x2, y2=y2)#mpe.VideoFileClip(temp_video_path)
        if words is not None:
            texts = []
            for i in range(len(words)):
                text = TextClip(words[i]['text'], fontsize=40, color='white', font="Lane",)

                # Set the duration for which the text will be visible
                text = text.set_duration(words[i]['end'] - words[i]['start'])  # Visible for 5 seconds
                text = text.set_start(words[i]['start'])

                # Position the text in the center of the screen
                text = text.set_pos(('center', 0.8), relative=True)
                texts.append(text)
                    
                # Overlay the text clip on the first video clip  
            cropped_clip = CompositeVideoClip([cropped_clip] + texts)  

        if background_audio_path:
            audio_background = mpe.AudioFileClip(background_audio_path)
            audio_background = audio_background.subclip(0, cropped_clip.duration)
            final_audio = mpe.CompositeAudioClip([cropped_clip.audio, audio_background])
            final_clip = cropped_clip.set_audio(final_audio)
        else:
            final_clip = cropped_clip.set_audio(mp_clip.audio)

        # Write the final output video with audio preserved or combined
        final_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
        print(f"Video successfully cropped and saved to {output_video_path}")

    else:
        print(f"Error: {str(e)}")
    