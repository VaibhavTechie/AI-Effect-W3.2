# src/orchestrator/grpc_executor.py

import grpc
import logging
import os

from proto import energy_pipeline_pb2, energy_pipeline_pb2_grpc

def execute_workflow(containers, server_address="localhost:50051"):
    # Setup gRPC channel
    with grpc.insecure_channel(server_address) as channel:
        stub = energy_pipeline_pb2_grpc.ContainerExecutorStub(channel)

        for container in containers:
            input_file = container.get("input_file", "")
            output_file = container.get("output_file", "")
            container_id = container.get("id", "unknown")

            logging.info(f"[gRPC] Executing {container_id}")
            print(f"[gRPC] Executing {container_id} -> {input_file} -> {output_file}")

            # Build gRPC request
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

    logging.info("gRPC pipeline completed.")
    print("All containers executed via gRPC.")