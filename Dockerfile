FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        git \
        ca-certificates \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
