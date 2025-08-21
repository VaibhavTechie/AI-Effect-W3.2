# Corrected server.py for the Energy Generator Service

import os
import time
import logging
import grpc
import pandas as pd
from concurrent import futures

# Correctly import from the 'generated' and placeholder 'src' packages
from generated import energy_pb2, energy_pb2_grpc
from src.common.grpc_logging import ServerLoggingInterceptor # This will import our placeholder
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s")
log = logging.getLogger(__name__)

# The class name MUST match the one from the shared .proto contract
class ContainerExecutorServicer(energy_pb2_grpc.ContainerExecutorServicer):

    # The method name MUST match the one from the shared .proto contract
    def Execute(self, request, context):
        log_prefix = "[Generator]"
        log.info(f"{log_prefix} Received request. Will generate to '{request.output_file}'")
        try:
            # Correctly construct the full path inside the container
            output_path = request.output_file
            
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(request.output_file), exist_ok=True)

            data = {
                'timestamp': [f"2025-01-01T00:00:{i:02d}Z" for i in range(10)],
                'household_id': [f"HH-{i%3}" for i in range(10)],
                'power_consumption': [120.5 + i for i in range(10)],
                'voltage': [230.0] * 10,
                'current': [5.1 + (i*0.1) for i in range(10)],
            }
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            message = f"Successfully generated synthetic data to {request.output_file}"
            log.info(message)
            return energy_pb2.ExecuteResponse(success=True, message=message)
        except Exception as e:
            error_message = f"{log_prefix} Failed to execute: {e}"
            log.error(error_message, exc_info=True)
            return energy_pb2.ExecuteResponse(success=False, message=error_message)

def serve(port: int = 50051):
    # We remove the interceptor as the code for it is missing
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Register our CORRECTED service
    energy_pb2_grpc.add_ContainerExecutorServicer_to_server(ContainerExecutorServicer(), server)

    # Health check setup remains the same
    health_serv = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_serv, server)
    health_serv.set("", health_pb2.HealthCheckResponse.SERVING)
    
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    log.info(f"Generator gRPC service listening on :{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()