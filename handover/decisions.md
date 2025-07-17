# WP 3.2 - Handover Document

## Stage 3: End-to-End Integration Test

### Objective:
To verify that the WP 3.2 orchestrator can successfully execute and manage the complete WP 3.1 pipeline using configuration-driven commands.

### Actions Taken:
- Ensured WP 3.1 repository containers were working and built.
- Generated a new `energy_data.csv` file with valid synthetic data.
- Launched the orchestrator using:
  ```bash
  docker-compose run --rm orchestrator python main.py
  ```
- Observed sequential execution:
  - `energy-generator` ran and created `energy_data.csv`
  - `energy-analyzer` ran and created `output1.json`
  - `report-generator` ran and created `output2.json` and final `energy_report.csv`
- Verified correctness of each intermediate and final output.
- Confirmed container logs output expected content.

---

## Stage 3: Execution from 3.1 Orchestrator

### Objective:
To confirm that the orchestrator in WP 3.2 correctly triggers WP 3.1 containers with volume-mounted data handoff.

### Execution:
- Ran orchestrator from `AI-Effect-W3.2/docker/` directory:
  ```bash
  docker-compose run --rm orchestrator python main.py
  ```
- Verified logs step-by-step:
  - `energy-generator`: Generated CSV and saved it under `/data/`
  - `energy-analyzer`: Parsed and transformed the CSV into `output1.json`
  - `report-generator`: Generated final `energy_report.csv`
  - Logs show correct execution and sequencing
- Confirmed outputs in mounted folder:
  - `energy_data.csv`
  - `output1.json`
  - `output2.json`
  - `energy_report.csv`

### Notes:
- Mount path resolved to `/home/work/project/AIEffect-3.1-to-3.2/data`
- Subprocess commands injected volume mounting dynamically in `executor.py`

---

## Limitations

- Communication between components is file-based, not service-based.
- `docker run` is executed from within containers, not using APIs or IPC.
- No health check or fault tolerance implemented.
- No true orchestration engine or scheduler yet.
- Logs are console-based, no structured logs or metrics collected.

---

## Screenshots
- [x] Screenshot of CSV in `/data/`
![alt text](image.png)
- [x] Screenshot of command run of main.py
![alt text](image-1.png)
- [x] Screenshot of orchestrator success message / trace
![alt text](image-2.png)



---

## Artifacts in Repo (Mentor Access)

- All source code and Dockerfiles are committed to repo:
  - `src/orchestrator/main.py`
  - `src/orchestrator/config_parser.py`
  - `src/orchestrator/executor.py`
- Config JSON:
  - `config/energy-pipeline.json`
- Data pipeline:
  - `/data/energy_data.csv`
  - `/data/output1.json`
  - `/data/output2.json`
  - `/data/energy_report.csv`
- Run logs available in Teams & documented.
- README contains run instructions.

---

## Learning Summary (By Student)

### What I Learned About Containers:
- How to build and tag multi-service Docker containers.
- How `docker-compose` links volumes and networks.
- How to mount shared data folders and pass outputs between services.

### What Broke and How I Fixed It:
- `docker-compose` volume paths were incorrect – fixed relative path alignment.
- `COPY` instructions in Dockerfiles failed due to bad directory layout – corrected Docker context.
- `data` directory permissions – used `sudo` to generate required files.
- Missing images – handled using `docker build` prior to orchestration.

### What I Understood About Orchestrator Sequencing:
- Parsed the config JSON to extract sequence of execution.
- Used `subprocess.run()` to execute Docker commands serially.
- Verified execution order via logs.
- Ensured dependency containers only run after their inputs are ready.

---

## Ready for Mentor Review
This log summarizes the full integration and handover status of WP 3.2, including verification with WP 3.1 deliverables.

Next step: Begin Iteration 2 with service-to-service orchestration using gRPC & async execution.



---

## Iteration 2: gRPC-based Orchestration Setup

### Objective:
To refactor the WP3.2 orchestrator to use gRPC communication instead of subprocess-based `docker run` calls, enabling a more modular, service-driven architecture.

### Actions Taken:
- Defined a new `.proto` file `energy_pipeline.proto` under `proto/` directory with the following schema:
  ```proto
  syntax = "proto3";

  service ContainerExecutor {
    rpc Execute(ExecuteRequest) returns (ExecuteResponse);
  }

  message ExecuteRequest {
    string input_file = 1;
    string output_file = 2;
  }

  message ExecuteResponse {
    bool success = 1;
    string message = 2;
  }
  ```

- Used `grpc_tools.protoc` to generate two Python modules:
  - `energy_pipeline_pb2.py`
  - `energy_pipeline_pb2_grpc.py`

- Relocated both files into `proto/` and fixed imports using relative syntax (`from . import energy_pipeline_pb2`).

- Implemented `grpc_executor.py` to replace the legacy `executor.py`:
  - Establishes channel with `localhost:50051`
  - Sends serialized request to remote service
  - Logs all responses and errors

- Implemented `dummy_grpc_server.py` to simulate a basic gRPC-compatible backend:
  - Accepts request, validates file paths
  - Returns a success/failure message for testing without running actual containers

- Modified `grpc_main.py` to integrate config parsing and gRPC-driven container dispatch.

- All gRPC orchestrator files were moved to `src/orchestrator/` while keeping proto definitions in `proto/`.

### Outcome:
- gRPC communication between orchestrator and dummy backend confirmed.
- Correct logging and file path transfer observed.
- The structure allows drop-in replacement of dummy server with actual container gRPC services in future iterations.

---

## Screenshots – Iteration 2

- [x] gRPC Protobuf Structure Setup  
  ![Grpc Setup and Implementation](image-3.png)

- [x] Dummy gRPC Server Validation  
  ![gRPC Dummy Server Test](image-4.png)

---

## Next Steps

- Replace dummy backend with actual container-based gRPC handlers.
- Run end-to-end tests by invoking real containers through gRPC interface.
- Compare performance and logging between subprocess vs. gRPC execution.

