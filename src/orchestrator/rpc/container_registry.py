# src/orchestrator/rpc/container_registry.py
from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional
import os, sys, grpc

# Ensure root on sys.path for "proto" imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from proto import energy_pipeline_pb2, energy_pipeline_pb2_grpc

@dataclass
class ServiceEntry:
    host: str
    port: int
    factory: Callable[[], Any]  # returns (stub, build_request)

def _factory(host: str, port: int):
    def make():
        channel = grpc.insecure_channel(f"{host}:{port}")
        stub = energy_pipeline_pb2_grpc.ContainerExecutorStub(channel)
        def build_request(input_file: str, output_file: str, params: Optional[Dict[str, str]] = None):
            # params not in proto; kept for API symmetry
            return energy_pipeline_pb2.ExecuteRequest(
                input_file=input_file,
                output_file=output_file
            )
        return stub, build_request
    return make

# Hardcoded registry — extend as you add real services
REGISTRY: Dict[str, ServiceEntry] = {
    # logical container name : endpoint + factory
    "eir-preprocessor": ServiceEntry(host="localhost", port=50051, factory=_factory("localhost", 50051)),
    "analyzer-square":  ServiceEntry(host="localhost", port=50052, factory=_factory("localhost", 50052)),
    "analyzer-cube":    ServiceEntry(host="localhost", port=50053, factory=_factory("localhost", 50053)),
}
