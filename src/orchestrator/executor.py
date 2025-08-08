import subprocess
import logging
from typing import Dict, Any, List


REQUIRED_KEYS = {"id", "command", "input_file", "output_file"}


def validate_containers(containers: List[Dict[str, Any]]):
    for container in containers:
        missing_keys = REQUIRED_KEYS - container.keys()
        if missing_keys:
            raise ValueError(f"Container {container.get('id', '[unknown]')} missing keys: {missing_keys}")


def execute_workflow(config: Dict[str, Any]):
    containers = config.get("containers", [])
    container_map = {c["id"]: c for c in containers}

    validate_containers(containers)

    start_node_id = config.get("start_node")
    if not start_node_id:
        raise ValueError("Missing 'start_node' in configuration")

    current_id = start_node_id
    visited = set()

    while current_id:
        if current_id in visited:
            raise ValueError(f"Cycle detected in workflow at: {current_id}")
        visited.add(current_id)

        container = container_map.get(current_id)
        if not container:
            raise ValueError(f"Container with id '{current_id}' not found in config")

        cmd = container.get("command")
        if "-v" not in cmd and "--volume" not in cmd:
            raise ValueError(f"Container {container['id']} missing required volume mount in command")

        logging.info(f"Starting container: {container['id']}")
        logging.info(f"Command: {cmd}")
        print(f"Running: {cmd}")

        try:
            result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
            logging.info(f"{container['id']} STDOUT:\n{result.stdout}")
            if result.stderr:
                logging.warning(f"{container['id']} STDERR:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            logging.error(f"{container['id']} FAILED with error:\n{e.stderr}")
            print(f"Error: Command failed: {cmd}")
            break

        current_id = container.get("next_node")

    logging.info("All containers executed.")
    print("All containers executed successfully.")