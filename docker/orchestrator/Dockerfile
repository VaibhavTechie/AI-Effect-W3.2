FROM python:3.9-slim

# Install Docker CLI for container management
RUN apt-get update && apt-get install -y docker.io && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ../../src/orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source code mounted as volume during development
CMD ["python", "main.py"]
