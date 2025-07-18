import os
import logging

from config_parser import parse_config
from grpc_executor import execute_workflow  # new gRPC logic

LOG_DIR = os.environ.get("LOG_DIR", "/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "orchestrator.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    config = parse_config("/config/energy-pipeline.json")
    execute_workflow(config["containers"])
