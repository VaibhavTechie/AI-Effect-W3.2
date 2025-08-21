# Corrected server.py for the Energy Analyzer Service

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
        log_prefix = "[Analyzer]"
        log.info(f"{log_prefix} Received request: input='{request.input_file}', output='{request.output_file}'")
        
        try:
            input_path = request.input_file
            output_path = request.output_file

            # The analyzer reads the CSV generated in the previous step
            log.info(f"{log_prefix} Reading data from '{input_path}'...")
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            df = pd.read_csv(input_path)
            
            # Perform some analysis (placeholder logic, but now on the data from the file)
            df['efficiency'] = (df['power_consumption'] / (df['voltage'] * df['current'])).round(3)
            df['anomaly_detected'] = df['efficiency'] < 0.1
            
            log.info(f"{log_prefix} Analysis complete. Preparing protobuf message...")
            
            # Create the protobuf message structure required for the next step
            report_data = energy_pb2.ProcessedDataReport()
            for _, row in df.iterrows():
                processed_item = report_data.processed.add()
                processed_item.timestamp = row['timestamp']
                processed_item.household_id = row['household_id']
                processed_item.power = float(row['power_consumption'])
                processed_item.efficiency = float(row['efficiency'])
                processed_item.anomaly_detected = bool(row['anomaly_detected'])

            # Serialize the protobuf message and write it to the output file
            with open(output_path, "wb") as f:
                f.write(report_data.SerializeToString())

            message = f"Successfully analyzed {len(df)} records and saved to {request.output_file}"
            log.info(message)
            return energy_pb2.ExecuteResponse(success=True, message=message)

        except Exception as e:
            error_message = f"{log_prefix} Failed to execute: {e}"
            log.error(error_message, exc_info=True)
            return energy_pb2.ExecuteResponse(success=False, message=error_message)

def serve(port: int = 50052):
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
    log.info(f"Analyzer gRPC service listening on :{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()