import os
import requests
import json
import dotenv

dotenv.load_dotenv()

API_KEY = os.getenv("EIA_API_KEY")
BASE_URL = "https://api.eia.gov/v2"

def fetch_metadata(route: str) -> dict:
    """
    Fetch metadata for a given EIA APIv2 route.
    :param route: e.g., "petroleum/pri/gnd"
    :return: JSON metadata as a dictionary
    """
    if not API_KEY:
        raise RuntimeError("Set EIA_API_KEY environment variable first.")

    url = f"{BASE_URL}/{route}"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def fetch_facet_values(route: str, facet: str) -> dict:
    """
    Fetch available values for a specific facet in a route.
    :param route: e.g., "petroleum/pri/gnd"
    :param facet: e.g., "product"
    :return: JSON facet values as a dictionary
    """
    if not API_KEY:
        raise RuntimeError("Set EIA_API_KEY environment variable first.")

    url = f"{BASE_URL}/{route}/facet/{facet}"
    params = {"api_key": API_KEY}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    try:
        # Fetch metadata for petroleum prices
        route = "petroleum/pri/gnd"
        metadata = fetch_metadata(route)
        print("Metadata:")
        print(json.dumps(metadata, indent=2))

        # Fetch available facets (from metadata)
        facets = metadata["response"].get("facets", [])
        print("\nAvailable Facets:")
        for facet in facets:
            print(f"- {facet['id']}: {facet['description']}")

        # Fetch values for a specific facet (e.g., product)
        facet = "product"
        facet_values = fetch_facet_values(route, facet)
        print(f"\nValues for Facet '{facet}':")
        for value in facet_values["response"]["facets"]:
            print(f"- {value['id']}: {value['name']} ({value['alias']})")

    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        print("No response available to display.")
    except Exception as e:
        print(f"Error: {e}")