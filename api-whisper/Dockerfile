# Use the official Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg
# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code to the container
COPY . .

# Expose the port that the app runs on
EXPOSE 8000

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "whisper_api:app", "--host", "0.0.0.0", "--port", "8000"]
