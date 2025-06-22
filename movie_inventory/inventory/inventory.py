import requests
import logging
import os

class Inventory:

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ.get('API_KEY')}"
    }

    urls = {
        "get_streaming_providers": "https://api.themoviedb.org/3/watch/providers/movie?",
        "get_movies_per_provider": "https://api.themoviedb.org/3/discover/movie?"
    }

    def __init__(self):
        self.inventory = []

    def get_streaming_providers(self):
        providers = {}
        url = self.urls["get_streaming_providers"]
        params = {"language": "en-US"}
        response = requests.get(url, headers=self.headers, params=params)

        provider_objects = response.json()["results"]

        for provider in provider_objects:
            providers[provider["provider_name"]] = {
                "provider_id": provider["provider_id"]
            }

        logging.info(f"Found {len(providers)} providers")

        return providers

    def get_movies_per_provider(self, provider_name):
        collected_movies = []
        params = {
            "language": "en-US",
            "with_watch_providers": provider_name,
            "include_video": False,
            "include_adult": False
        }
        url = self.urls["get_movies_per_provider"]
        response = requests.get(url, headers=self.headers, params=params)
        collected_movies = response.json()["results"]
        total_pages = response.json()["total_pages"]
        for page in range(2, total_pages + 1):
            logging.info(f"Getting page {page} of {total_pages}")
            params["page"] = page
            response = requests.get(url, headers=self.headers, params=params)
            logging.info(f"Received {len(response.json()['results'])} movies. {len(collected_movies)} collected so far.")
            collected_movies.extend(response.json()["results"])

        return collected_movies

    def collect_inventory(self):
        return 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    inventory = Inventory()
    movies = inventory.get_movies_per_provider("Netflix")

    for movie in movies:
        print(movie)