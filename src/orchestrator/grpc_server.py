# src/orchestrator/grpc_server.py

import grpc
from concurrent import futures
import time
import logging

import energy_pipeline_pb2
import energy_pipeline_pb2_grpc

from executor_grpc import execute_container_grpc  # gRPC-specific executor

class ContainerExecutorService(energy_pipeline_pb2_grpc.ContainerExecutorServicer):
    def Execute(self, request, context):
        input_path = request.input_file
        output_path = request.output_file

        logging.info(f"Received gRPC request: input={input_path}, output={output_path}")
        try:
            success, message = execute_container_grpc(input_path, output_path)
            return energy_pipeline_pb2.ExecuteResponse(success=success, message=message)
        except Exception as e:
            logging.error(f"Execution failed: {e}")
            return energy_pipeline_pb2.ExecuteResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    energy_pipeline_pb2_grpc.add_ContainerExecutorServicer_to_server(ContainerExecutorService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("gRPC Server started on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        logging.info("gRPC Server stopped.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    serve()
