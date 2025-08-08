# src/orchestrator/grpc_main.py

import os
import sys
import json
import logging

# Add project root to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config_parser import parse_config
from grpc_executor import execute_workflow

LOG_DIR = os.environ.get("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "orchestrator.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CONFIG_PATH = "config/energy-pipeline.json"

if __name__ == "__main__":
    try:
        if not os.path.exists(CONFIG_PATH):
            logging.error(f"Configuration file not found: {CONFIG_PATH}")
            print(f"Error: Configuration file not found at {CONFIG_PATH}")
            sys.exit(1)

        with open(CONFIG_PATH, "r") as f:
            json.load(f)  # validate it's valid JSON

        config = parse_config(CONFIG_PATH)
        execute_workflow(config["containers"])

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in config file: {e}")
        print("Error: Config file contains invalid JSON.")
        sys.exit(1)

    except Exception as e:
        logging.exception("Unhandled error in orchestrator")
        print(f"Unhandled error: {e}")
        sys.exit(1)