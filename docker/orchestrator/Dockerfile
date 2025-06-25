FROM python:3.9-slim

# Install Docker CLI
RUN apt-get update && \
    apt-get install -y docker.io && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

COPY src/orchestrator/requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
