# src/orchestrator/rpc/container_stub.py
from typing import Dict, Optional
from .grpc_executor import execute_container

def execute(
    container_name: str,
    input_file: str,
    output_file: str,
    params: Optional[Dict[str, str]] = None,
    timeout_sec: float = 30.0,
):
    """
    Integration stub: call this from higher-level code instead of raw gRPC.
    """
    return execute_container(
        container_name=container_name,
        input_file=input_file,
        output_file=output_file,
        params=params or {},
        timeout_sec=timeout_sec,
    )