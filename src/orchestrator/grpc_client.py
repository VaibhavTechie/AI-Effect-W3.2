# grpc_client.py
import grpc
import energy_pipeline_pb2
import energy_pipeline_pb2_grpc

def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = energy_pipeline_pb2_grpc.ContainerExecutorStub(channel)

    request = energy_pipeline_pb2.ExecuteRequest(
        input_file="/data/energy_data.csv",
        output_file="/data/output1.json"
    )

    response = stub.Execute(request)
    print("Success:", response.success)
    print("Message:", response.message)

if __name__ == "__main__":
    run()
