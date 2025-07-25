import requests
import logging
from datetime import datetime
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

    MIN_YEAR = 1900
    MAX_YEAR = datetime.now().year

    def __init__(self):
        self.inventory = []
        self.providers = ["Netflix"]
        self.weighted_constants = {}
        self.average_rating = 0
        self.average_review_count = 0
        self.collected_records = 0


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

    def initial_request(self, provider_name):
        params = {
            "language": "en-US",
            "with_watch_providers": provider_name,
            "include_video": False,
            "include_adult": False
        }
        url = self.urls["get_movies_per_provider"]
        response = requests.get(url, headers=self.headers, params=params)
        total_pages = response.json()["total_pages"]
        logging.info(f"Collected {total_pages} for Provider: {provider_name}")
        if total_pages > 500:
            return True
        else:
            return False

    def compute_popularity(self, provider_name):
        print(1)

    def average_primer(self, results, provider_name):
        for result in results:

            #update global constants
            self.average_rating += result['vote_average']
            self.average_review_count += result['vote_count']
            self.collected_records += 1

            #update provider constants
            self.weighted_constants[provider_name]["average_rating"] += result['vote_average']
            self.weighted_constants[provider_name]["average_review_count"] += result['vote_count']
            self.weighted_constants[provider_name]["collected_records"] += 1


    def finalize_provider_bayesian_constants(self, provider_name):
        self.weighted_constants[provider_name]["average_rating"] = self.weighted_constants[provider_name]["average_rating"] / self.weighted_constants[provider_name]["collected_records"]
        self.weighted_constants[provider_name]["average_review_count"] =self.weighted_constants[provider_name]["average_review_count"] / self.weighted_constants[provider_name]["collected_records"]

    def finalize_global_bayesian_constants(self):
        self.average_rating = self.average_rating / self.collected_records
        self.average_review_count = self.average_review_count / self.collected_records

    def fragmented_inventory(self, provider_name):
        collected_movies = []
        params = {
            "language": "en-US",
            "with_watch_providers": provider_name,
            "include_video": False,
            "include_adult": False
        }
        url = self.urls["get_movies_per_provider"]

        for year in range(self.MIN_YEAR, self.MAX_YEAR + 1):
            for month in range(1, 12):
                params["primary_release_date.gte"] = f"{year}-{month}-01",
                params["primary_release_date.lte"] = f"{year}-{month + 1}-01"
                try:
                    response = requests.get(url, headers=self.headers, params=params)
                    output = response.json()["results"]
                    collected_movies.append(output)
                    logging.info(f"Collected {len(output)} movies for Provider: {provider_name} across {year}-{month} to {year}-{month+1}")
                    self.average_primer(output, provider_name)
                except Exception as e:
                    logging.error(f"Failed to collect {provider_name} for {year}-{month}-01 to {year}-{month + 1}-01 :: {e}")

        return collected_movies

    def generate_inventory(self):
        result = {}
        for provider in self.providers:
            self.weighted_constants[provider] = {
                "average_rating": 0,
                "average_review_count": 0,
                "collected_records": 0,
            }
            fragmentation_flag = self.initial_request(provider)
            if fragmentation_flag:
                result[provider] = self.fragmented_inventory(provider)
            else:
                result[provider] = self.get_movies_per_provider(provider)
            self.finalize_provider_bayesian_constants(provider)
        self.finalize_global_bayesian_constants()
        logging.info(f"Average Rating = {self.average_rating}\nAverage Review Count = {self.average_review_count}\nCollected Records = {self.collected_records}")
        return result

    def get_movies_per_provider(self, provider_name):
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
            self.average_primer(response.json()["results"], provider_name)
        return collected_movies


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    inventory = Inventory()
    inventory.generate_inventory()