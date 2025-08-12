# src/orchestrator/grpc_executor.py
from __future__ import annotations
from typing import Dict, Optional, Any, List
import logging
import os, sys
import grpc

# Ensure root on sys.path so "proto" imports work from anywhere
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.orchestrator.rpc.container_registry import REGISTRY

log = logging.getLogger(__name__)

class GrpcExecutionError(Exception):
    pass

REQUIRED_KEYS = {"id", "command", "input_file", "output_file"}

def validate_containers(containers: List[Dict[str, Any]]):
    for c in containers:
        missing = REQUIRED_KEYS - c.keys()
        if missing:
            raise ValueError(f"Container '{c.get('id','[unknown]')}' missing keys: {missing}")

def execute_container(
    container_name: str,
    input_file: str,
    output_file: str,
    params: Optional[Dict[str, str]] = None,
    timeout_sec: float = 30.0,
) -> Dict[str, Any]:
    """
    Execute a job on the target container via gRPC using the registry.
    Returns normalized dict: {"ok": bool, "message": str}
    """
    if container_name not in REGISTRY:
        raise GrpcExecutionError(f"Container '{container_name}' not found in registry")

    entry = REGISTRY[container_name]
    stub, build_request = entry.factory()
    request = build_request(input_file=input_file, output_file=output_file, params=params)

    log.debug("Execute -> %s at %s:%s | input=%s output=%s params=%s",
              container_name, entry.host, entry.port, input_file, output_file, params)

    try:
        response = stub.Execute(request, timeout=timeout_sec)  # per proto
    except grpc.RpcError as e:
        code = e.code()
        details = e.details() or str(e)
        log.error("gRPC error calling %s: %s (%s)", container_name, details, code)
        raise GrpcExecutionError(f"gRPC {code}: {details}") from e

    # Your ExecuteResponse fields are: success (bool), message (string)
    ok = getattr(response, "success", False)
    message = getattr(response, "message", "")
    return {"ok": ok, "message": message}

def execute_workflow(config: Dict[str, Any]) -> None:
    """
    Optional: drive a simple chain using the config/JSON structure you've used elsewhere.
    Expects:
      config = {
        "start_node": "eir-preprocessor",
        "containers": [
            {"id": "eir-preprocessor", "input_file": "...", "output_file": "...", "next_node": "analyzer-square"},
            {"id": "analyzer-square",  "input_file": "...", "output_file": "...", "next_node": null}
        ]
      }
    """
    containers = config.get("containers", [])
    container_map = {c["id"]: c for c in containers}
    validate_containers(containers)

    current_id = config.get("start_node")
    if not current_id:
        raise ValueError("Missing 'start_node' in workflow config")

    while current_id:
        c = container_map.get(current_id)
        if not c:
            raise ValueError(f"Container '{current_id}' not found in config")

        res = execute_container(
            container_name=c["id"],
            input_file=c["input_file"],
            output_file=c["output_file"],
            params=c.get("params", {}),
            timeout_sec=float(c.get("timeout_sec", 30)),
        )

        if not res["ok"]:
            log.error("%s failed: %s", c["id"], res["message"])
            raise GrpcExecutionError(f"{c['id']} failed: {res['message']}")

        log.info("%s OK: %s", c["id"], res["message"])
        current_id = c.get("next_node")

    log.info("gRPC pipeline completed.")
