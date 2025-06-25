# Simple Workflow Orchestrator

This project contains a minimal Python orchestrator that executes a sequence of
Docker containers described in a JSON configuration file.

## Quick start

```bash
# build and run the orchestrator using docker compose
cd docker
docker-compose up --build
```

During development the source code is mounted into the container. To execute a
workflow directly on the host run:

```bash
python src/orchestrator/main.py --workflow config/test-workflow.json
```
