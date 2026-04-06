import grpc
import Impactyn.Contracts.RuntimeService.V1_pb2 as RuntimeService_V1_pb2
import Impactyn.Contracts.FeedTemplate.V1_pb2 as FeedTemplate_V1_pb2
import pytest
import json
from config import settings

def load_test_data():
    with open('data/feed_expectations.json') as f:
        return json.load(f)

@pytest.mark.parametrize("feed_key", load_test_data().keys())
def test_feed_templates(grpc_stub, feed_key):

    # 1. Get Data for this specific iteration
    all_data = load_test_data()
    test_env = all_data[feed_key]
    requestData = test_env["request"]
    expectedResult = test_env["expectations"]

    token = settings.AUTH_TOKEN if test_env["auth_type"] == "valid_token" else settings.INVALID_TOKEN

    metadata = [
        ('x-impactyn-client-version', settings.CLIENT_VERSION),
        ('authorization', token)
    ]
    # Create a request for the Feed Template
    request = RuntimeService_V1_pb2.GetRequest(
        apiVersion="V1",
        namespace=requestData["namespace"],
        resource=requestData["resource"],
        name=requestData["name"],
        view=requestData["view"],
    )

    # Handle Expected SUCCESS vs Expected FAILURE
    if expectedResult["expected_status"] == "OK":
        # Standard positive test
        response = grpc_stub.Get(request, metadata=metadata)
        assert response is not None
        print(f"Successfully accessed {feed_key}")

        #Get the feed response which is feed and parse it
        Home = FeedTemplate_V1_pb2.GetFeedResponse()
        Home.ParseFromString(response.content)

       #Get feedItems which are the sections of the feed and parse them
        FeedSections = Home.Feed
       #assert the number of sections in the feed
        assert len(FeedSections.Items) > expectedResult["min_sections"], f"Found {len(FeedSections.Items)} Sections"

       # Loop through each section and print the title and number of items in that section
        for i, section_item in enumerate(FeedSections.Items):

          assert section_item.Type == "section", f"Item {i} is {section_item.Type}, not a Section!"
          assert len(section_item.PropertyBag)>0 , f"Item {i} 's property bag is empty!"
          section_props = FeedTemplate_V1_pb2.SectionItemProperties()
          section_props.ParseFromString(section_item.PropertyBag)

          print(f"\nSECTION {i+1}: '{section_props.Title}' (Rank: {section_props.Rank})")
          print(f"  └─ Contains {len(section_props.Items)} sub-items")

          # 5. Iterate through nested items inside the Section (Hero, Banner, etc.)
          for j, sub_item in enumerate(section_props.Items):
             print(f"     item [{j}] Type: {sub_item.Type}")

             assert sub_item.Type in expectedResult["allowed_item_types"], f"Item {j} 's type is not allowed!"
             # --- DYNAMIC PARSING BASED ON TYPE ---
             if sub_item.Type == "hero":
                hero = FeedTemplate_V1_pb2.HeroItemProperties()
                hero.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Hero Title: {hero.Title}")
                resourceToken = hero.Resource
                resourceID    = resourceToken.resourceId
                resourceType = resourceID.resourceType
                print(f"        >> Hero Resource Type: {resourceType}")
                print(f"        >> Hero Resource ID namespace: {resourceID.namespace}")
                print(f"        >> Hero Resource ID name: {resourceID.name}")

             elif sub_item.Type == "banner":
                banner = FeedTemplate_V1_pb2.BannerItemProperties()
                banner.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Banner Badge: {banner.BadgeText}")
                resourceToken = banner.Resource
                resourceID    = resourceToken.resourceId
                resourceType  = resourceID.resourceType
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
                resourceID    = resourceToken.resourceId
                resourceType  = resourceID.resourceType
                print(f"        >> Cover Resource Type: {resourceType}")
                print(f"        >> Cover Resource ID namespace: {resourceID.namespace}")
                print(f"        >> Cover Resource ID name: {resourceID.name}")

             elif sub_item.Type == "shop":
                shop = FeedTemplate_V1_pb2.ShopItemProperties()
                shop.ParseFromString(sub_item.PropertyBag)
                print(f"        >> Shop Title: {shop.Title}")
                resourceToken = shop.Resource
                resourceID    = resourceToken.resourceId
                resourceType  = resourceID.resourceType
                print(f"        >> Shop Resource Type: {resourceType}")
                print(f"        >> Shop Resource ID namespace: {resourceID.namespace}")
                print(f"        >> Shop Resource ID name: {resourceID.name}")

             elif sub_item.Type == "user":
                user = FeedTemplate_V1_pb2.UserItemProperties()
                user.ParseFromString(sub_item.PropertyBag)
                print(f"        >> User Title: {user.Title}")
                resourceToken = user.Resource
                resourceID    = resourceToken.resourceId
                resourceType  = resourceID.resourceType
                print(f"        >> User Resource Type: {resourceType}")
                print(f"        >> User Resource ID namespace: {resourceID.namespace}")
                print(f"        >> User Resource ID name: {resourceID.name}")

             elif sub_item.Type == "review":
                review = FeedTemplate_V1_pb2.ReviewItemProperties()
                review.ParseFromString(sub_item.PropertyBag)
                print(f"        >> review Title: {review.Title}")
                resourceToken = review.Resource
                resourceID    = resourceToken.resourceId
                resourceType  = resourceID.resourceType
                print(f"        >> review Resource Type: {resourceType}")
                print(f"        >> review Resource ID namespace: {resourceID.namespace}")
                print(f"        >> review Resource ID name: {resourceID.name}")

    else:
        # NEGATIVE TEST: Assert that it RAISES an error
        with pytest.raises(grpc.RpcError) as e:
            grpc_stub.Get(request, metadata=metadata)

        # Verify the error code is exactly UNAUTHENTICATED
        assert e.value.code() == grpc.StatusCode.UNAUTHENTICATED

        # Optionally verify the error message (details)
        assert "Received http2 header with status: 401" in e.value.details()

        print(f"Confirmed: Access denied as expected for {feed_key}")



if __name__ == "__main__":
    # To run
    # pytest tests/test_feed.py -s
    pytest.main([__file__, "-s"])

