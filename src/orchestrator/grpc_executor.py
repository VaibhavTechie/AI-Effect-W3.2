# src/orchestrator/grpc_executor.py

import grpc
import logging
import os
import sys
from typing import Dict, Any

# Add root directory to PYTHONPATH for import resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from proto import energy_pipeline_pb2, energy_pipeline_pb2_grpc

# Stricter validation: ensure required fields are present and not empty
def validate_container_config(container_id: str, container_config: Dict[str, Any]):
    required_fields = ["id", "input_file", "output_file"]
    for field in required_fields:
        if field not in container_config:
            raise ValueError(f"Container '{container_id}' missing required field: '{field}'")
        if not container_config[field]:
            # This check prevents empty strings, which was a "Dangerous Default"
            raise ValueError(f"Container '{container_id}' field '{field}' cannot be empty")

def execute_workflow(config: Dict[str, Any]):
    # Get the dictionary of containers, not a list
    containers = config.get("containers", {})
    service_registry = config.get("service_registry", {})

    start_node_id = config.get("start_node")
    if not start_node_id:
        raise ValueError("Missing 'start_node' in config")

    current_id = start_node_id
    visited = set()

    while current_id:
        if current_id in visited:
            raise ValueError(f"Cycle detected in workflow at node: {current_id}")
        visited.add(current_id)

        container = containers.get(current_id)
        if not container:
            raise ValueError(f"Container ID '{current_id}' not found in 'containers' config")

        # Run validation for the current container
        validate_container_config(current_id, container)

        # Get the specific server address for THIS container from the registry
        server_address = service_registry.get(current_id)
        if not server_address:
            raise ValueError(f"Missing service address for '{current_id}' in 'service_registry'")

        # These now get the full, correct path directly from the config
        input_file = container["input_file"]
        output_file = container["output_file"]
        
        logging.info(f"[gRPC] Connecting to {current_id} at {server_address}")
        print(f"[gRPC] Executing {current_id} -> {input_file} -> {output_file}")

        try:
            # Open a new channel for each service call
            with grpc.insecure_channel(server_address) as channel:
                stub = energy_pipeline_pb2_grpc.ContainerExecutorStub(channel)

                # The hardcoded "/data/" prefix is now REMOVED
                request = energy_pipeline_pb2.ExecuteRequest(
                    input_file=input_file,
                    output_file=output_file
                )

                response = stub.Execute(request, timeout=container.get("timeout_seconds", 30))
                
                if response.success:
                    logging.info(f"{current_id} succeeded: {response.message}")
                    print(f"  -> SUCCESS: {response.message}")
                else:
                    logging.error(f"{current_id} failed: {response.message}")
                    print(f"  -> ERROR: {current_id} failed: {response.message}")
                    break # Stop the workflow on failure
        
        except grpc.RpcError as e:
            logging.error(f"gRPC error for {current_id}: {e.details()}")
            print(f"  -> FATAL gRPC ERROR: Could not connect to {current_id} at {server_address}. Details: {e.details()}")
            break # Stop the workflow on connection error

        # Move to the next node
        current_id = container.get("next_node")

    if not current_id:
        logging.info("gRPC pipeline completed successfully.")
        print("\nWorkflow completed successfully.")
    else:
        logging.warning("gRPC pipeline stopped due to an error.")
        print("\nWorkflow stopped due to an error.")