# Issue Log – WP3.2 Orchestrator

This document tracks all issues encountered during the initial Docker setup, orchestration scaffolding, and final integration for WP3.2.

---

### Issue 1: `docker-compose: command not found`

- **Summary:** Docker Compose was not pre-installed on the system.  
- **Resolution:** Installed Docker Compose using APT:
    sudo apt install docker-compose

---

### Issue 2: `PermissionError(13) — Docker socket access denied`

- **Summary:** The orchestrator container exited due to lack of permission to access the Docker daemon socket (`/var/run/docker.sock`).  
- **Resolution:** Added user to the docker group:
    sudo usermod -aG docker $USER

  Then logged out and back in (or rebooted) to apply the group membership.

---

### Issue 3: `COPY failed: forbidden path outside the build context`

- **Summary:** Dockerfile used a COPY command referencing a path (`../../src/...`) outside of the Docker build context.  
- **Resolution:** Modified the `docker-compose.yml` to expand the build context:
    build:
      context: ../
      dockerfile: docker/orchestrator/Dockerfile

  Adjusted the Dockerfile COPY path accordingly:
    COPY src/orchestrator/requirements.txt .

---

### Issue 4: `lstat .../orchestrator: no such file or directory`

- **Summary:** Docker build failed due to an incorrect Dockerfile path in `docker-compose.yml`.  
- **Resolution:** Verified that the Dockerfile exists at `docker/orchestrator/Dockerfile` and corrected the reference.

---

### Issue 5: `FileNotFoundError: /data/energy_data.csv`

- **Summary:** Generator container failed due to missing input file.  
- **Root Cause:** The orchestrator was running containers with `docker run` that expected volume-mounted files in `/data/`, but the mount path was missing.  
- **Resolution:**  
  - Updated `config/energy-pipeline.json` to inject absolute volume paths.  
  - Ensured `data/energy_data.csv` was generated beforehand.

---

### Issue 6: Output files not found during orchestrator execution

- **Summary:** Analyzer and report-generator containers failed because their expected input files (`output1.json`, `output2.json`) were missing.  
- **Root Cause:** A prior step in the pipeline had failed, so required input files were never created.  
- **Resolution:** Verified file presence in `/data/` and manually tested each container with:
    docker run --rm -v "$PWD/data:/data" <container-name>

---

### Issue 7: `ModuleNotFoundError: No module named 'proto'`

- **Summary:** `dummy_grpc_server.py` failed because Python couldn’t locate the `proto` package.  
- **Resolution:** Prepended the project root to `sys.path` at the top of the relevant scripts.

---

### Issue 8 & 10: Nested gRPC Import Errors

- **Summary:** Python raised `ImportError` and `ModuleNotFoundError` from within the auto-generated gRPC files.  
- **Root Cause:** Auto-generated code was not using relative imports.  
- **Resolution:** Edited `energy_pipeline_pb2_grpc.py`:
    from . import energy_pipeline_pb2

---

### Issue 9: gRPC proto generation targeting wrong folder

- **Summary:** Initial compilation of `.proto` placed generated files in the wrong directory.  
- **Resolution:** Corrected the `protoc` command:
    protoc --python_out=proto --grpc_python_out=proto energy_pipeline.proto

---

### Issue 11: `.venv` files mistakenly added to Git

- **Summary:** `git add .` included the virtual environment directory.  
- **Resolution:** Updated `.gitignore` to include `.venv/` and removed staged files.

---

### Issue 12: `OSError: [Errno 30] Read-only file system: '/logs'` on macOS

- **Summary:** `grpc_main.py` failed when trying to create logs in a system directory.  
- **Root Cause:** Default `LOG_DIR` was hardcoded to an absolute path.  
- **Resolution:** Changed `LOG_DIR` to a relative path (`logs/`).

---

### Issue 13: Config file not found: `/config/energy-pipeline.json` on fresh machine

- **Summary:** gRPC orchestrator failed because the config path was Docker-specific.  
- **Resolution:** Updated `grpc_main.py` to use relative path:
    config/energy-pipeline.json

---

### Issue 14: `ModuleNotFoundError: No module named 'grpc'`

- **Summary:** Python import error after setting up a new virtual environment.  
- **Resolution:** Installed gRPC dependencies:
    pip install grpcio grpcio-tools

---

## Phase 3: Live Integration & WP 3.1 Code Correction

This phase involved debugging the end-to-end pipeline with the salvaged and corrected WP 3.1 services.

---

### Issue 15: Critical `.proto` Contract Mismatch (`Method not found!`)

- **Problem:** Integration failed with gRPC `Method not found!`.  
- **Root Cause:** WP 3.1 team used a different `.proto` contract with methods like `GenerateData` and direct data passing.  
- **Resolution:** Replaced incorrect `.proto` with official contract and regenerated Python gRPC files.

---

### Issue 16: `AttributeError: ... has no attribute 'ContainerExecutorServicer'`

- **Problem:** Services failed to start after fixing the `.proto`.  
- **Root Cause:** `server.py` still referenced old, incorrect service classes.  
- **Resolution:** Rewrote `server.py` for all three services to correctly implement `ContainerExecutorServicer` and `Execute`.

---

### Issue 17: `ModuleNotFoundError: No module named 'pandas'`

- **Problem:** Corrected service logic failed due to missing pandas dependency.  
- **Resolution:** Added `pandas` to `requirements.txt` for all services.

---

### Issue 18: FileNotFoundError Between Services

- **Problem:** Generator created files, but analyzer couldn’t find them.  
- **Root Cause:** Each service had its own isolated Docker volume.  
- **Resolution:** Reconfigured `docker-compose.yml` to use a shared bind mount:
    - ./wp31_services/data:/data

---

## Final Outcome

All documented issues, including critical integration blockers, have been successfully resolved.  
The project now contains a **fully self-contained, corrected, and functional set of WP 3.1 services** that comply with the project’s architectural requirements.  
The **WP 3.2 orchestrator successfully executes the entire pipeline end-to-end.**