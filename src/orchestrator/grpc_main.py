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
        # We don't need to manually check for the file or load JSON here,
        # because our new parse_config function does all of that for us.
        
        config = parse_config(CONFIG_PATH)
        
        
        # Pass the entire 'config' object, not just a part of it.
        execute_workflow(config)

    except json.JSONDecodeError as e:
        
        logging.error(f"Invalid JSON in config file: {e}")
        print("Error: Config file contains invalid JSON.")
        sys.exit(1)

    except Exception as e:
        logging.exception("Unhandled error in orchestrator")
        # Print the specific error message from the exception
        print(f"An error occurred: {e}")
        sys.exit(1)