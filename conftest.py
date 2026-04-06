import pytest
import grpc
import Impactyn.Contracts.RuntimeService.V1_pb2_grpc as RuntimeService_V1_pb2_grpc
from config import settings

@pytest.fixture(scope="module")
def grpc_stub():
    """
    This fixture creates the gRPC connection once per test module.
    It uses the HOST defined in your config/settings.py.
    """
    # 1. Setup the secure channel
    credentials = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel(settings.HOST, credentials)

    # 2. Create the stub
    stub = RuntimeService_V1_pb2_grpc.RuntimeServiceStub(channel)

    # 3. Provide the stub to the tests
    yield stub

    # 4. Cleanup (Runs after all tests in the module are finished)
    channel.close()