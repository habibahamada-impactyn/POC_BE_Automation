import grpc
import Impactyn.Contracts.RuntimeService.V1_pb2 as RuntimeService_V1_pb2
import Impactyn.Contracts.RuntimeService.V1_pb2_grpc as RuntimeService_V1_pb2_grpc
import Impactyn.Contracts.FeedTemplate.V1_pb2 as FeedTemplate_V1_pb2
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
        resource="FeedTemplates",
        namespace="template.home",
        name="EG",
        view="default",
    )

    # Call the GetPublicUserProfile method
    response = grpc_stub.Get(request, metadata=metadata)


    #Get the feed response which is feed and parse it
    Home = FeedTemplate_V1_pb2.GetFeedResponse()
    Home.ParseFromString(response.content)

    #Get feedItems which are the sections of the feed and parse them
    FeedSections = Home.Feed
    #assert the number of sections in the feed
    assert len(FeedSections.Items) == 20, f"Expected 20 sections, but found {len(FeedSections.Items)}"

    # Loop through each section and print the title and number of items in that section
    for i, section_item in enumerate(FeedSections.Items):
        #print(f"\nProcessing item of type '{section_item.Type}'")

        assert section_item.Type == "section", f"Item {i} is {section_item.Type}, not a Section!"
        section_props = FeedTemplate_V1_pb2.SectionItemProperties()
        section_props.ParseFromString(section_item.PropertyBag)

        print(f"\nSECTION {i+1}: '{section_props.Title}' (Rank: {section_props.Rank})")
        print(f"  └─ Contains {len(section_props.Items)} sub-items")

        # 5. Iterate through nested items inside the Section (Hero, Banner, etc.)
        for j, sub_item in enumerate(section_props.Items):
            print(f"     item [{j}] Type: {sub_item.Type}")

            # --- DYNAMIC PARSING BASED ON TYPE ---
            if sub_item.Type == "hero":
                hero = FeedTemplate_V1_pb2.HeroItemProperties()
                hero.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Hero Title: {hero.Title}")
                resourceToken = hero.Resource
                resourceID = resourceToken.resourceId
                resourceType = resourceID.resourceType
                print(f"        >> Hero Resource Type: {resourceType}")
                print(f"        >> Hero Resource ID namespace: {resourceID.namespace}")
                print(f"        >> Hero Resource ID name: {resourceID.name}")

            elif sub_item.Type == "banner":
                banner = FeedTemplate_V1_pb2.BannerItemProperties()
                banner.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Banner Badge: {banner.BadgeText}")
                resourceToken = banner.Resource
                resourceID = resourceToken.resourceId
                resourceType = resourceID.resourceType
                print(f"        >> Banner Resource Type: {resourceType}")
                print(f"        >> Banner Resource ID namespace: {resourceID.namespace}")
                print(f"        >> Banner Resource ID name: {resourceID.name}")

            elif sub_item.Type == "category":
                cat = FeedTemplate_V1_pb2.CategoryItemProperties()
                cat.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Category Route: {cat.Route}")
                print(f"        >> Category Title: {cat.Title}")

            elif sub_item.Type == "cover":
                cover = FeedTemplate_V1_pb2.CoverItemProperties()
                cover.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Cover Title: {cover.Title}")
                resourceToken = cover.Resource
                resourceID = resourceToken.resourceId
                resourceType = resourceID.resourceType
                print(f"        >> Cover Resource Type: {resourceType}")
                print(f"        >> Cover Resource ID namespace: {resourceID.namespace}")
                print(f"        >> Cover Resource ID name: {resourceID.name}")

            elif sub_item.Type == "shop":
                shop = FeedTemplate_V1_pb2.ShopItemProperties()
                shop.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Shop Title: {shop.Title}")
                resourceToken = shop.Resource
                resourceID = resourceToken.resourceId
                resourceType = resourceID.resourceType
                print(f"        >> Shop Resource Type: {resourceType}")
                print(f"        >> Shop Resource ID namespace: {resourceID.namespace}")
                print(f"        >> Shop Resource ID name: {resourceID.name}")

            elif sub_item.Type == "user":
                user = FeedTemplate_V1_pb2.UserItemProperties()
                user.ParseFromString(sub_item.PropertyBag)
                print(f"        >> User Title: {user.Title}")
                resourceToken = user.Resource
                resourceID = resourceToken.resourceId
                resourceType = resourceID.resourceType
                print(f"        >> User Resource Type: {resourceType}")
                print(f"        >> User Resource ID namespace: {resourceID.namespace}")
                print(f"        >> User Resource ID name: {resourceID.name}")

            elif sub_item.Type == "review":
                review = FeedTemplate_V1_pb2.ReviewItemProperties()
                review.ParseFromString(sub_item.PropertyBag)
                print(f"        >> review Title: {review.Title}")
                resourceToken = review.Resource
                resourceID = resourceToken.resourceId
                resourceType = resourceID.resourceType
                print(f"        >> review Resource Type: {resourceType}")
                print(f"        >> review Resource ID namespace: {resourceID.namespace}")
                print(f"        >> review Resource ID name: {resourceID.name}")

if __name__ == "__main__":
    # To run without pytest:
    # python test_impactyn_get.py
    pytest.main([__file__, "-s"])

