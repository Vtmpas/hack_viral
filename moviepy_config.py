import os
from moviepy.config import change_settings

# Путь к ImageMagick может отличаться в зависимости от вашей системы
IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', 'convert')

change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})