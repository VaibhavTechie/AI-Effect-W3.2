# src/orchestrator/grpc_client.py
import grpc
from src import energy_pipeline_pb2, energy_pipeline_pb2_grpc
from .logging_config import setup_logging

def main() -> None:
    # JSON logger to stdout + logs/execution_log.log
    log = setup_logging("orchestrator-grpc-client")
    log.info("process_start")

    try:
        # Connect to the local gRPC server
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = energy_pipeline_pb2_grpc.ContainerExecutorStub(channel)

            # Example request (dummy server echoes success)
            req = energy_pipeline_pb2.ExecuteRequest(
                input_file="/data/energy_data.csv",
                output_file="/data/output1.json"
            )

            log.info("execute_request", extra={"status": "start"})
            resp = stub.Execute(req, timeout=5.0)
            print(f"Success: {resp.success}")
            print(f"Message: {resp.message}")
            log.info("execute_request_done", extra={"status": "success"})

    except grpc.RpcError as e:
        # Nice error if server isn't reachable, etc.
        code = getattr(e, "code", lambda: "UNKNOWN")()
        details = getattr(e, "details", lambda: str(e))()
        print(f"gRPC error: {code} - {details}")
        log.error("execute_request_failed", extra={"status": "failure", "grpc_code": str(code), "details": details})

if __name__ == "__main__":
    main()
