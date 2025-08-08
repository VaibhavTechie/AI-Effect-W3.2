# src/orchestrator/grpc_executor.py

import grpc
import logging
import os
import sys
from typing import Dict, Any, List

# Add root directory to PYTHONPATH for import resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from proto import energy_pipeline_pb2, energy_pipeline_pb2_grpc

REQUIRED_KEYS = {"id", "command", "input_file", "output_file"}

def validate_containers(containers: List[Dict[str, Any]]):
    for container in containers:
        missing = REQUIRED_KEYS - container.keys()
        if missing:
            raise ValueError(f"Container '{container.get('id', '[unknown]')}' missing keys: {missing}")

def execute_workflow(config: Dict[str, Any], server_address="localhost:50051"):
    containers = config.get("containers", [])
    container_map = {c["id"]: c for c in containers}

    validate_containers(containers)

    start_node_id = config.get("start_node")
    if not start_node_id:
        raise ValueError("Missing 'start_node' in config")

    current_id = start_node_id
    visited = set()

    with grpc.insecure_channel(server_address) as channel:
        stub = energy_pipeline_pb2_grpc.ContainerExecutorStub(channel)

        while current_id:
            if current_id in visited:
                raise ValueError(f"Cycle detected in workflow at node: {current_id}")
            visited.add(current_id)

            container = container_map.get(current_id)
            if not container:
                raise ValueError(f"Container '{current_id}' not found in config")

            input_file = container.get("input_file", "")
            output_file = container.get("output_file", "")
            container_id = container.get("id", "unknown")

            logging.info(f"[gRPC] Executing {container_id}")
            print(f"[gRPC] Executing {container_id} -> {input_file} -> {output_file}")

            request = energy_pipeline_pb2.ExecuteRequest(
                input_file=f"/data/{input_file}",
                output_file=f"/data/{output_file}"
            )

            try:
                response = stub.Execute(request)
                if response.success:
                    logging.info(f"{container_id} succeeded: {response.message}")
                    print(f"{container_id}: {response.message}")
                else:
                    logging.error(f"{container_id} failed: {response.message}")
                    print(f"Error: {container_id} failed: {response.message}")
                    break
            except grpc.RpcError as e:
                logging.error(f"gRPC error for {container_id}: {e}")
                print(f"gRPC error: {e}")
                break

            current_id = container.get("next_node")

    logging.info("gRPC pipeline completed.")
    print("All containers executed via gRPC.")