# src/orchestrator/dummy_grpc_server.py
import time
from concurrent import futures

import grpc
from src import energy_pipeline_pb2, energy_pipeline_pb2_grpc
from .logging_config import setup_logging

# JSON logger → stdout + logs/execution_log.log
log = setup_logging("orchestrator-grpc-server")


class DummyExecutor(energy_pipeline_pb2_grpc.ContainerExecutorServicer):
    def Execute(self, request, context):
        start = time.perf_counter()
        log.info(
            "execute_request",
            extra={"status": "start", "input_file": request.input_file, "output_file": request.output_file},
        )
        msg = f"Dummy processed {request.input_file} to {request.output_file}"
        duration_ms = int((time.perf_counter() - start) * 1000)
        log.info("execute_response", extra={"status": "success", "duration_ms": duration_ms})
        return energy_pipeline_pb2.ExecuteResponse(success=True, message=msg)


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    energy_pipeline_pb2_grpc.add_ContainerExecutorServicer_to_server(DummyExecutor(), server)
    server.add_insecure_port("[::]:50051")
    log.info("server_start", extra={"status": "start"})
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
