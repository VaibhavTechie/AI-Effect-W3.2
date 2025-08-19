# src/orchestrator/main.py
import os
import sys
import logging

from .logging_config import setup_logging
from .config_parser import parse_config
from .executor import execute_workflow


def main() -> int:
    # Structured JSON logger (to stdout + logs/execution_log.log)
    log = setup_logging("orchestrator")
    log.info("process_start")

    # Config path (env override supported)
    config_path = os.environ.get("PIPELINE_CONFIG", "config/energy-pipeline.json")

    # 1) Load & validate config
    try:
        cfg = parse_config(config_path)
        containers = cfg.get("containers", [])
        if not isinstance(containers, list) or not containers:
            raise ValueError("Config must contain a non-empty 'containers' list.")
    except Exception as e:
        # Clear, actionable error
        abs_path = os.path.abspath(config_path)
        log.error("config_error", extra={"status": "failure"})
        print(f"Config error: {e}\nChecked path: {abs_path}")
        return 1

    # 2) Execute the workflow
    try:
        execute_workflow(containers)
        log.info("workflow_complete")
        return 0
    except Exception as e:
        log.error("workflow_failure", extra={"status": "failure"})
        print(f"Workflow error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
