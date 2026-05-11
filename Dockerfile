FROM python:3.14-slim
RUN apt-get update && \
    apt-get install -y curl iputils-ping && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY nerva/ nerva/

RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000
