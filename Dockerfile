FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

RUN python -m pip install telethon requests boto3

WORKDIR /app
COPY . .

CMD ["python", "index.py"]
