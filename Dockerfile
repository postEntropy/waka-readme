FROM python:3.12-slim

LABEL maintainer="seu-usuario"
LABEL description="WakaTime + GitHub profile README stats action"

# System deps for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create an init so that `src` is a proper package
RUN touch src/__init__.py

ENTRYPOINT ["python", "-u", "/app/main.py"]
