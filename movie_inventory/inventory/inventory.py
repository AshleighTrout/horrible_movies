import requests
import logging
import os

class Inventory:

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ.get('API_KEY')}"
    }

    urls = {
        "get_streaming_providers": "https://api.themoviedb.org/3/watch/providers/movie?language=en-US"
    }

    def __init__(self):
        self.inventory = []

    def get_streaming_providers(self):
        providers = {}
        url = self.urls["get_streaming_providers"]
        response = requests.get(url, headers=self.headers)

        provider_objects = response.json()["results"]

        for provider in provider_objects:
            providers[provider["provider_name"]] = {
                "provider_id": provider["provider_id"]
            }

        logging.info(f"Found {len(providers)} providers")

        return providers

    def collect_inventory(self):
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    inventory = Inventory()
    inventory.get_streaming_providers()