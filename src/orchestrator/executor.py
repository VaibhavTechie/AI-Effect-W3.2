# src/orchestrator/executor.py
import os
import socket
import subprocess
import time

from .logging_config import get_logger

log = get_logger("orchestrator")

def execute_workflow(containers):
    node = os.getenv("NODE_NAME", socket.gethostname())

    for c in containers:
        cid = c.get("id", "unknown")
        cmd = c["command"]

        # If it's a Docker command and there's no explicit -v, inject host ../data -> /data
        if "docker run" in cmd and "-v" not in cmd:
            host_data = os.path.abspath(os.path.join(os.getcwd(), "..", "data"))
            # Make Windows path Docker-friendly
            host_data = host_data.replace("\\", "/")
            cmd = cmd.replace("docker run", f'docker run -v "{host_data}:/data"')

        # START
        start = time.perf_counter()
        log.info("container_start", extra={
            "container_id": cid,
            "status": "start",
            "node": node
        })
        print(f"Running: {cmd}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                text=True,
                check=True,
                capture_output=True
            )
            duration_ms = int((time.perf_counter() - start) * 1000)

            # SUCCESS
            log.info("container_success", extra={
                "container_id": cid,
                "status": "success",
                "duration_ms": duration_ms,
                "node": node
            })
            if result.stdout:
                log.info(result.stdout.strip(), extra={"container_id": cid})
            if result.stderr:
                log.warning(result.stderr.strip(), extra={"container_id": cid})

        except subprocess.CalledProcessError as e:
            duration_ms = int((time.perf_counter() - start) * 1000)
            log.error("container_failure", extra={
                "container_id": cid,
                "status": "failure",
                "duration_ms": duration_ms,
                "returncode": e.returncode,
                "node": node
            })
            print(f"Error: Command failed: {cmd}")
            break

    log.info("workflow_complete", extra={"node": node})
    print("All containers executed.")
