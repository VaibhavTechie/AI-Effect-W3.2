# Corrected Dockerfile for the Energy Generator Service

FROM python:3.9-slim
WORKDIR /app
RUN mkdir /data

# Set the PYTHONPATH to include the root and generated directories for correct imports
ENV PYTHONPATH=/app:/app/generated

# Install Python dependencies
COPY docker/energy-generator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary source code and proto files into the container
COPY energy_generator/ ./energy_generator/
COPY proto/ ./proto/
COPY generated/ ./generated/
# The 'src' folder (our placeholder) is also needed for the original code's imports to resolve
COPY src/ ./src/

EXPOSE 50051

# Run the server using the correct module path
CMD ["python", "-u", "-m", "energy_generator.server"]

# Healthcheck to ensure the gRPC service is responsive
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD \
  python -c "import grpc,sys; from grpc_health.v1 import health_pb2_grpc,health_pb2; \
c=grpc.insecure_channel('localhost:50051'); s=health_pb2_grpc.HealthStub(c); \
sys.exit(0 if s.Check(health_pb2.HealthCheckRequest()).status==1 else 1)"