\## Phase 2 — Logging \& Project Logs



\### What changed

\- Added \*\*structured JSON logs\*\* to stdout and `logs/execution\_log.log`.

\- Each step emits: `timestamp`, `level`, `message`, `service`, `node`, `container\_id`, `status` (`start|success|failure`), and `duration\_ms`.

\- Central logger: `src/orchestrator/logging\_config.py`.

\- gRPC demo logs are working; pipeline (per-container) logs are ready (run once Docker is installed).



\### How to run (gRPC demo — no Docker)

```powershell

\# one-time

pip install grpcio grpcio-tools

py -m grpc\_tools.protoc -I proto --python\_out=src --grpc\_python\_out=src proto\\energy\_pipeline.proto



\# server (terminal 1)

$env:PYTHONPATH = (Resolve-Path .\\src).Path

py -m src.orchestrator.dummy\_grpc\_server



\# client (terminal 2)

$env:PYTHONPATH = (Resolve-Path .\\src).Path

py -m src.orchestrator.grpc\_client



