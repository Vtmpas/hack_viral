FROM nvidia/cuda:12.5.0-devel-ubuntu22.04

WORKDIR /app

COPY ./requirements.txt ./

RUN apt update && apt install -y python3 python3-pip && apt clean
RUN pip3 install numpy --pre torch torchvision torchaudio --force-reinstall --index-url https://download.pytorch.org/whl/nightly/cu121

RUN pip3 install -r ./requirements.txt
COPY . .
#RUN vllm serve llava-hf/llava-1.5-7b-hf --chat-template template_llava.jinja --port 8002
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.openai.api_server", "--model", "Qwen/Qwen2.5-7B-Instruct", "--port", "8000", "--host", "0.0.0.0"]


