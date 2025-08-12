# src/orchestrator/dummy_grpc_server.py

import grpc
from concurrent import futures
import time
import logging
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from proto import energy_pipeline_pb2, energy_pipeline_pb2_grpc


class DummyExecutorServicer(energy_pipeline_pb2_grpc.ContainerExecutorServicer):
    def Execute(self, request, context):
        logging.info(f"Received ExecuteRequest: {request.input_file} -> {request.output_file}")
        print(f"[DUMMY SERVER] Processing {request.input_file} → {request.output_file}")
        # Fake success response
        return energy_pipeline_pb2.ExecuteResponse(
            success=True,
            message=f"Dummy processed {request.input_file} to {request.output_file}"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    energy_pipeline_pb2_grpc.add_ContainerExecutorServicer_to_server(DummyExecutorServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("[DUMMY SERVER] gRPC server running on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("[DUMMY SERVER] Shutting down")
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()