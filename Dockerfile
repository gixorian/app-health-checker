FROM python:3.14-slim
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY health_check.py .
COPY tasks.py .
COPY main.py .

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000
