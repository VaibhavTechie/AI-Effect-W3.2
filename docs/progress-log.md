# Progress Log – WP3.2 Orchestrator

## Stage 1: Configuration Parser Test

- Created a test script `test_config_parser.py` in `src/orchestrator/`:

  ```python
  from config_parser import parse_config

  if __name__ == "__main__":
      config = parse_config("/config/energy-pipeline.json")
      print("Config loaded successfully:")
      print(config)
  ```

- Mounted `config/energy-pipeline.json` inside the container at `/config/energy-pipeline.json`.

- Ran the test script inside the container:

  ```bash
  docker-compose run --rm orchestrator /bin/sh
  python test_config_parser.py
  ```

- Output:

  ```
  gun@Legion:~/ai-effect-wp3.2-orchestrator/docker$ docker-compose run --rm orchestrator /bin/sh
  WARN[0000] /home/gun/ai-effect-wp3.2-orchestrator/docker/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
  # python test_config_parser.py
  Config loaded successfully:
  {'workflow_name': 'energy_data_pipeline', 'containers': [{'id': 'energy-generator', 'name': 'Energy Data Generator', 'command': 'docker run energy-generator', 'input_file': 'energy_data.csv', 'output_file': 'output1.json', 'depends_on': []}, {'id': 'energy-analyzer', 'name': 'Energy Data Analyzer', 'command': 'docker run energy-analyzer', 'input_file': 'output1.json', 'output_file': 'output2.json', 'depends_on': ['energy-generator']}, {'id': 'report-generator', 'name': 'Report Generator', 'command': 'docker run report-generator', 'input_file': 'output2.json', 'output_file': 'energy_report.csv', 'depends_on': ['energy-analyzer']}]}
  ```

- Result:
  - Config file parsed successfully
  - Volumes and config file mounted correctly
  - Parser ready to integrate into orchestrator

---

## Stage 2: Execution Engine Test

- Implemented `execute_workflow()` in `executor.py` to execute Docker commands from the workflow config.
- Updated `main.py` to load config and call the executor.
- Ran the main orchestrator entry:

  ```bash
  docker-compose run --rm orchestrator python main.py
  ```

- Output:

  ```
  WARN[0000] /home/gun/ai-effect-wp3.2-orchestrator/docker/docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
  Running: docker run energy-generator
  Unable to find image 'energy-generator:latest' locally
  docker: Error response from daemon: pull access denied for energy-generator, repository does not exist or may require 'docker login'.
  See 'docker run --help'.
  Error: Command failed: docker run energy-generator
  ```

- Result:
  - Commands read and executed in defined order
  - Waits for each container to finish
  - Basic error handling in place (invalid image names, etc.)

---

## Stage 3: Integration with WP3.1 Pipeline

- Cloned the WP3.1 repo:  
  `https://github.com/AvantiRao/AIEffect-3.1-to-3.2.git`

- Fixes performed:
  - Corrected volume mount paths in `docker-compose.yaml`
  - Fixed Dockerfile `COPY` path errors and typos (e.g., `CCOPY`)
  - Updated code in containers to use absolute paths (e.g., `/data/output1.json`) instead of relative

- Created `energy_data.csv` manually to simulate input (since W3.1 had not supplied it)
- All output files were stored in the `data/` folder:
  - `energy_data.csv`
  - `output1.json`, `output2.json`
  - `energy_report.csv`

---

## Successful Pipeline Execution

- Ran full pipeline with:

  ```bash
  docker-compose -f docker-compose.yaml up --build
  ```

- Results:
  -  `energy-generator`: generated 3 records
  -  `energy-analyzer`: analyzed and annotated records
  -  `report-generator`: generated `energy_report.csv`
  - All containers exited with code `0`

---

## Next Steps

- Replace `docker run` with `docker-compose run` for more isolated workflow testing
- Add execution logs (stdout) to file or orchestrator log
- Begin integration with WP3.2 orchestrator for dynamic execution in Iteration 2

# WP3.2 Orchestrator – Stage 3 Run Documentation

## Summary
This document records the execution of the full energy pipeline orchestration using the WP3.1 Docker-based microservices and WP3.2 orchestrator.

---

## Stage 3 – Orchestrated Pipeline Execution

### Setup Steps
1. Copied the generated `energy_data.csv` file into the shared `data/` directory.
2. Ensured Docker and Docker Compose are installed and running.
3. Inside the project root (`AIEffect-3.1-to-3.2`), executed:
   ```bash
   docker-compose -f docker-compose.yaml up --build
   ```

---

### Component Execution Logs

#### 1. **Energy Generator**
- Successfully generated 10 rows of mock household energy usage data.
- Output saved to: `data/energy_data.csv`
- Sample Entry:
  ```csv
  timestamp,household_id,power_consumption,voltage,current
  2024-01-15T10:30:00Z,H003,2.04,230.12,8.5
  ```

#### 2. **Energy Analyzer**
- Read `energy_data.csv`, calculated efficiency, flagged anomalies.
- Output saved to: `data/output1.json`
- Sample JSON Entry:
  ```json
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "household_id": "H003",
    "power": 2.04,
    "efficiency": 0.135,
    "status": "normal",
    "anomaly_detected": false
  }
  ```
- All 10 records processed with no invalid rows.

#### 3. **Report Generator**
- Took the analyzed JSON and created a final report.
- Output saved to: `data/energy_report.csv`

---

## Issues Encountered
- Initial Docker builds failed due to incorrect Dockerfile paths.
- Needed to generate test CSV manually for the pipeline to consume.
- Resolved permission errors while writing to `data/`.
- Fixed a typo (`CCOPY`) in Dockerfile which broke image build.

---

## Outcome
The pipeline executed successfully end-to-end:
- 10 records flowed through 3 containers.
- Every output file was generated as intended.
- Each container ran independently and exited cleanly.

---

## Files in `/data` after execution
- `energy_data.csv`
- `output1.json`
- `output2.json`
- `energy_report.csv`

---

## Next Steps
- Add additional validation logic or exception handling in orchestrator.
- Automate data generation or allow config-based batch runs.
- Move on to Iteration 2 as described in mentor docs.

---

## Stage 3 – Orchestrator Triggering External Containers

### Objective:
To verify that the WP3.2 orchestrator can execute and control the WP3.1 containerized services using a JSON-driven workflow.

### Key Fixes Implemented:
- Manually updated `energy-pipeline.json` to include absolute volume mounts:
  ```json
  "command": "docker run -v /home/work/project/AIEffect-3.1-to-3.2/data:/data aieffect-31-to-32-energy-generator"
  ```
  - Applied same fix for analyzer and report-generator containers.
- Verified output file generation by running each container manually:
  ```bash
  docker run --rm -v "$PWD/data:/data" aieffect-31-to-32-energy-analyzer
  docker run --rm -v "$PWD/data:/data" aieffect-31-to-32-report-generator
  ```

### Final Run from WP3.2 Orchestrator:
- From `AI-Effect-W3.2/docker/`, executed:
  ```bash
  docker-compose run --rm orchestrator python main.py
  ```
- Observed full pipeline execution:
  - Generator → Analyzer → Report
  - All outputs created correctly in `/data/`
- Output logs confirmed that all 3 containers executed in order and completed without error.

### Outcome:
- Confirmed that WP3.2 orchestrator can run WP3.1 containers using volume-mounted files.
- Pipeline completes from within WP3.2 context, even though containers belong to 3.1.
- No refactor needed inside container logic; orchestration driven via JSON `command` field.

---

## Stage 4 – gRPC-Based Orchestrator Setup (Iteration 2)

### Objective:
Introduce a parallel orchestrator logic using gRPC to execute containers, without altering the legacy `main.py` logic.

### Setup:
- Created new `energy_pipeline.proto` definition in `proto/`:
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

- Compiled `.proto` using `grpcio-tools`:
  ```bash
  python3 -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/energy_pipeline.proto
  ```

- Generated:
  - `proto/energy_pipeline_pb2.py`
  - `proto/energy_pipeline_pb2_grpc.py`

### New Files Created:
- `src/orchestrator/grpc_executor.py`:
  - Parses container list
  - Sends `ExecuteRequest` via gRPC
  - Logs success/failure for each container

- `src/orchestrator/grpc_main.py`:
  - Alternate entry point to orchestrate using gRPC
  - Uses same config as legacy orchestrator

- `src/orchestrator/dummy_grpc_server.py`:
  - Simulates container execution logic
  - Reads input/output file paths, writes dummy output

### Testing:
- Resolved import issues caused by generated `pb2` modules:
  - Added `__init__.py` to `proto/`
  - Updated imports to use:
    ```python
    from proto import energy_pipeline_pb2, energy_pipeline_pb2_grpc
    ```

- Verified dummy server runs:
  ```bash
  python3 src/orchestrator/dummy_grpc_server.py
  ```
  Output:
  ```
  [DUMMY SERVER] gRPC server running on port 50051
  ```

- Confirmed all gRPC scripts import successfully and connect to server

### Next Steps:
- Validate `grpc_main.py` against the running dummy server
- Gradually adapt WP3.1 container logic to respond to gRPC calls
- Include this progress in mentor meeting for Iteration 2 review


## Stage 4 – gRPC Integration Test on macOS (Cross-System Validation)

### Objective:
To validate the gRPC orchestrator and dummy server on a clean macOS machine using a virtual environment, outside Docker.

### Setup & Steps:

1. Cloned the `AI-Effect-W3.2` repository on macOS.

2. Created a Python virtual environment and installed required packages:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install grpcio grpcio-tools
   ```

3. Verified project structure and ensured the following changes:
   - `proto/` directory has an `__init__.py` file.
   - All import statements for protobuf files use:
     ```python
     from proto import energy_pipeline_pb2, energy_pipeline_pb2_grpc
     ```
   - Added `sys.path.insert(0, os.path.abspath(...))` to Python files like `grpc_executor.py` and `dummy_grpc_server.py` to enable clean relative imports across directories.

4. Started the dummy gRPC server:
   ```bash
   python3 src/orchestrator/dummy_grpc_server.py
   ```
   Output:
   ```
   [DUMMY SERVER] gRPC server running on port 50051
   ```

5. Ran the orchestrator client to test pipeline execution via gRPC:
   ```bash
   python3 src/orchestrator/grpc_main.py
   ```
   Output:
   ```
   [gRPC] Executing energy-generator -> energy_data.csv -> output1.json
   energy-generator: Dummy processed /data/energy_data.csv to /data/output1.json
   [gRPC] Executing energy-analyzer -> output1.json -> output2.json
   energy-analyzer: Dummy processed /data/output1.json to /data/output2.json
   [gRPC] Executing report-generator -> output2.json -> energy_report.csv
   report-generator: Dummy processed /data/output2.json to /data/energy_report.csv
   All containers executed via gRPC.
   ```

### Outcome:
- gRPC orchestrator pipeline confirmed working on macOS using virtual environment.
- Dummy server received and processed all 3 container stages correctly.
- Imports, protobufs, and execution paths fully resolved outside Docker.

### Next Steps:
- Begin replacing dummy handler logic with real WP3.1 service implementations.
- Enable containerized services to register and handle gRPC `ExecuteRequest`.
- Transition orchestrator from subprocess-based control to gRPC-based orchestration.