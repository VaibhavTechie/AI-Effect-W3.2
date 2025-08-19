# src/orchestrator/config_parser.py

import json
import os
import sys
from typing import Dict, Any

def parse_config(path: str) -> Dict[str, Any]:
    """
    Parses and validates the JSON configuration file for the orchestration workflow.
    """
    if not os.path.exists(path):
        print(f"Error: Configuration file not found at '{path}'")
        sys.exit(1)

    with open(path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file '{path}'. Details: {e}")
            sys.exit(1)

    # --- Start of New Validation Logic ---

    # Validate that 'start_node' exists and is a non-empty string
    if "start_node" not in config or not isinstance(config["start_node"], str) or not config["start_node"]:
        print("Error: Invalid config. It must contain a non-empty 'start_node' string.")
        sys.exit(1)

    # Validate that 'containers' exists and is a dictionary
    if "containers" not in config or not isinstance(config["containers"], dict):
        print("Error: Invalid config. It must contain a 'containers' dictionary.")
        sys.exit(1)

    # Validate that 'service_registry' exists and is a dictionary
    if "service_registry" not in config or not isinstance(config["service_registry"], dict):
        print("Error: Invalid config. It must contain a 'service_registry' dictionary.")
        sys.exit(1)
        
    start_node_id = config["start_node"]
    if start_node_id not in config["containers"]:
        print(f"Error: The 'start_node' ID '{start_node_id}' does not exist in the 'containers' dictionary.")
        sys.exit(1)

    # --- End of New Validation Logic ---

    print("Configuration parsed and validated successfully.")
    return config