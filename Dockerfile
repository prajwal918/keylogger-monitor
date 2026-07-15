FROM python:3.10-slim

WORKDIR /app

# Install necessary system dependencies for pynput if running in linux
RUN apt-get update && apt-get install -y \
    python3-xlib \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN pip install --no-cache-dir pynput

COPY src/ ./src/
COPY tests/ ./tests/
COPY config.example.json ./config.json

CMD ["python", "src/workkeylogger.py"]