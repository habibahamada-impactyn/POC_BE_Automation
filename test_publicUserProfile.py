import grpc
import Impactyn.Contracts.RuntimeService.V1_pb2 as RuntimeService_V1_pb2
import Impactyn.Contracts.RuntimeService.V1_pb2_grpc as RuntimeService_V1_pb2_grpc
import Impactyn.Contracts.UserProfiles.V1_pb2 as UserProfiles_V1_pb2
import pytest

HOST = 'staging.impactyn.io:530'
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJJbXBhY3R5bi5DcmVkZW50aWFsIjoidHlwZS9jcmVkZW50aWFscy9ucy9zbXMvbmFtZS8yMDEwMDc3MTIzNjNfYWJlMDBiYjAwOTIyZmVkOSIsIkltcGFjdHluLkRldmljZUlkIjoiNjc2OGRmMDAtOTgyMy1hYjVmLTllMGItYTMyNTVjMDMyNGU2IiwiSW1wYWN0eW4uRGV2aWNlTmFtZSI6IjE0RDM2NUVELTQ4ODYtNDkzNi1BM0ExLUZERUQ5OTJGNjA2NyIsIkltcGFjdHluLklkZW50aXR5IjoidHlwZS9pZGVudGl0aWVzL25zL2ZhYWUwN2NjNTI5MTVkYjBiZWM1M2NjNjY2OGVmY2ViX2Y1OGYwMDg4OGM4MGI2ZDgvbmFtZS9kZWZhdWx0IiwiSW1wYWN0eW4uVG9rZW5UeXBlIjoiaWRlbnRpdHkuYWNjZXNzIiwiSW1wYWN0eW4uUm9sZSI6WyJDZ1p3ZFdKc2FXTWFEQWpzbmJuT0JoRGd4WmExQXc9PSIsIkNnUjFjMlZ5RWpGbVlXRmxNRGRqWXpVeU9URTFaR0l3WW1Wak5UTmpZelkyTmpobFptTmxZbDltTlRobU1EQTRPRGhqT0RCaU5tUTRHZ3dJN0oyNXpnWVE0TVdXdFFNPSJdLCJuYmYiOjE3NzI1MzYzMDAsImV4cCI6MTc3NTEyODMwMCwiaWF0IjoxNzcyNTM2MzAwLCJpc3MiOiJJbXBhY3R5bi5JZGVudGl0eSIsImF1ZCI6IkltcGFjdHluLkZyb250ZG9vciJ9.23Q0gU5gSJ0WkOeJCMrJ4aDc-WfBmFALpoimwrdG1M0"
CLIENT_VERSION = "impactyn.iosapp/2.0.25"


@pytest.fixture
def grpc_stub():
    # 1. Create SSL credentials (this uses the standard trusted certificates on your Mac)
    credentials = grpc.ssl_channel_credentials()
    # 2. Use secure_channel with those credentials
    channel = grpc.secure_channel(HOST, credentials)
    return RuntimeService_V1_pb2_grpc.RuntimeServiceStub(channel)


def test_public_user_profile(grpc_stub):
    metadata = [
        ('x-impactyn-client-version', CLIENT_VERSION),
        ('authorization', AUTH_TOKEN)
    ]
    # Create a request for the public user profile
    request = RuntimeService_V1_pb2.GetRequest(
        apiVersion="V1",
        namespace="d8bb8494c5bed03dccdfb6976ca9c6a1_af7b47a2218aab7c",
        resource="UserProfiles",
        name="default",
        view="Public"
    )

    # Call the GetPublicUserProfile method
    response = grpc_stub.Get(request, metadata=metadata)


    profile = UserProfiles_V1_pb2.PublicUserProfile()
    profile.ParseFromString(response.content)

    # 4. Assertion
    # Assert that the response is not empty and contains expected fields
    assert response is not None
    # Check if headers were returned (map/dict in Python)
    assert "Impactyn.Client.ContentType" in response.headers

    print(f"Received {len(response.content)} bytes of data")

    print(f"Raw Content (Hex): {response.content.hex()[:50]}...")
    # Verify that we actually got data
    assert len(response.content) > 0

    # 3. Detailed Assertions
    assert profile.DisplayName in "habeba "
    assert profile.Followers == 1
    print(f"\n--- Decoded Profile Data ---")
    print(f"Display Name: {profile.DisplayName}")
    print(f"Bio: {profile.Bio}")
    print(f"Followers: {profile.Followers}")


if __name__ == "__main__":
    # To run without pytest:
    # python test_impactyn_get.py
    pytest.main([__file__, "-s"])

