# Corrected server.py for the Report Generator Service

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
        log_prefix = "[Reporter]"
        log.info(f"{log_prefix} Received request: input='{request.input_file}', output='{request.output_file}'")
        
        try:
            input_path = request.input_file
            output_path = request.output_file

            # The reporter reads the binary protobuf data from the analyzer step
            log.info(f"{log_prefix} Reading protobuf data from '{input_path}'...")
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")

            report_data = energy_pb2.ProcessedDataReport()
            with open(input_path, "rb") as f:
                report_data.ParseFromString(f.read())
            
            log.info(f"{log_prefix} Read {len(report_data.processed)} processed records.")

            # Convert the protobuf data into a list of dictionaries for easy DataFrame creation
            data_list = []
            for item in report_data.processed:
                data_list.append({
                    'timestamp': item.timestamp,
                    'household_id': item.household_id,
                    'power': item.power,
                    'efficiency': item.efficiency,
                    'anomaly_detected': item.anomaly_detected,
                })
            df = pd.DataFrame(data_list)
            
            # Save the final report as a CSV to the path specified by the orchestrator
            df.to_csv(output_path, index=False)
            log.info(f"{log_prefix} Successfully generated final report at '{output_path}'")

            message = f"Successfully generated report with {len(df)} records to {request.output_file}"
            return energy_pb2.ExecuteResponse(success=True, message=message)

        except Exception as e:
            error_message = f"{log_prefix} Failed to execute: {e}"
            log.error(error_message, exc_info=True)
            return energy_pb2.ExecuteResponse(success=False, message=error_message)

def serve(port: int = 50053):
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
    log.info(f"Reporter gRPC service listening on :{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()