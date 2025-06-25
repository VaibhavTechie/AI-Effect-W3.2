# Issue Log – WP3.2 Orchestrator Setup

This document tracks all issues encountered during initial Docker setup and orchestration scaffolding for WP3.2.

---

### Issue 1: `docker-compose: command not found`

- **Summary:** Docker Compose was not pre-installed on the system.
- **Resolution:**
  Installed Docker Compose using APT:
  ```bash
  sudo apt install docker-compose
  ```

---

### Issue 2: `PermissionError(13)` — Docker socket access denied

- **Summary:** The orchestrator container exited due to lack of permission to access the Docker daemon socket (`/var/run/docker.sock`).
- **Resolution:**
  Added user to the `docker` group:
  ```bash
  sudo usermod -aG docker $USER
  ```
  Then logged out and back in (or rebooted) to apply the group membership.

---

### Issue 3: `COPY failed: forbidden path outside the build context`

- **Summary:** Dockerfile used a `COPY` command referencing a path (`../../src/...`) outside of the Docker build context.
- **Resolution:**
  - Modified the `docker-compose.yml` to expand the build context:
    ```yaml
    build:
      context: ../
      dockerfile: docker/orchestrator/Dockerfile
    ```
  - Adjusted the Dockerfile `COPY` path accordingly:
    ```dockerfile
    COPY src/orchestrator/requirements.txt .
    ```

---

### Issue 4: `lstat .../orchestrator: no such file or directory`

- **Summary:** Docker build failed due to an incorrect Dockerfile path in `docker-compose.yml`.
- **Resolution:**
  Verified that the Dockerfile exists at `docker/orchestrator/Dockerfile` and corrected the reference:
  ```yaml
  dockerfile: docker/orchestrator/Dockerfile
  ```

---

### Outcome

All issues were resolved. The orchestrator container now:
- Builds successfully with Docker and Compose
- Executes `main.py` from the mounted volume
- Is ready for the next development stage (workflow execution, testing, and integration)
