FROM nvidia/cuda:12.5.0-devel-ubuntu22.04

WORKDIR /app

RUN apt update && apt install -y python3 python3-pip && apt clean

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install numpy --pre torch torchvision torchaudio --force-reinstall --index-url https://download.pytorch.org/whl/nightly/cu121
RUN pip install einops
RUN pip install scipy
RUN pip install packaging
RUN pip install ninja
RUN pip install transformers==4.41.2
RUN pip install safetensors>=0.4.2
RUN pip install aiohttp
RUN pip install pyyaml
RUN pip install Pillow
RUN pip install scipy
RUN pip install tqdm
RUN pip install psutil
RUN pip install segment-anything
RUN pip install scikit-image
RUN pip install piexif
RUN pip install opencv-python-headless
RUN pip install GitPython
RUN pip install torchsde
RUN pip install fastapi
RUN pip install  pydub
RUN pip install  opencv-python-headless
RUN pip install  scikit-learn
RUN pip install  scipy
RUN pip install moviepy
RUN pip install python-multipart
RUN apt install ffmpeg
RUN pip install uvicorn
RUN pip install openai
RUN apt install imagemagick -y
RUN pip install ImageMagic
RUN apt install libmagick++-dev -y
RUN apt install nano

COPY ./utils /app/utils
COPY ./cache_dir /app/cache_dir
COPY ./video_path /app/video_path
COPY ./policy.xml /etc/ImageMagick-6/policy.xml

COPY ./main.py /app/main.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

