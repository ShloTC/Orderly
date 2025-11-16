import requests
import os
import json
from datetime import datetime, timedelta
import re


class GameMetadataRetriever:
    def __init__(self, api_key):
        """
        Initialize the metadata retriever with RAWG API key

        :param api_key: RAWG API key
        """
        self.api_key = api_key
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".orderly", "game_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _check_cache(self, game_name):
        """
        Check if game metadata is in local cache

        :param game_name: Name of the game
        :return: Cached metadata or None
        """
        cache_file = os.path.join(self.cache_dir, f"{game_name.lower().replace(' ', '_')}_metadata.json")

        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                if datetime.now() - datetime.fromisoformat(cache_data['cached_at']) < timedelta(days=30):
                    return cache_data['metadata']
        return None

    def _save_to_cache(self, game_name, metadata):
        """
        Save game metadata to local cache

        :param game_name: Name of the game
        :param metadata: Metadata to cache
        """
        cache_file = os.path.join(self.cache_dir, f"{game_name.lower().replace(' ', '_')}_metadata.json")

        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'metadata': metadata
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=4)

    def get_cover_url(self, game_name):
        """
        Retrieve cover URL for a given game

        :param game_name: Name of the game
        :return: Cover URL or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False  # Disable SSL verification
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            return game.get('background_image', '')

        except requests.RequestException as e:
            print(f"Error retrieving game cover URL: {e}")
            return None

    def get_description(self, game_name):
        """
        Retrieve description for a given game

        :param game_name: Name of the game
        :return: Game description or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            game_id = game['id']

            game_details_response = requests.get(
                f"https://api.rawg.io/api/games/{game_id}",
                params={'key': self.api_key},
                verify=False
            )
            game_details = game_details_response.json()

            return game_details.get('description_raw', 'No description available')

        except requests.RequestException as e:
            print(f"Error retrieving game description: {e}")
            return None

    def get_genres(self, game_name):
        """
        Retrieve genres for a given game

        :param game_name: Name of the game
        :return: List of genres or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            return [genre['name'] for genre in game.get('genres', [])]

        except requests.RequestException as e:
            print(f"Error retrieving game genres: {e}")
            return None

    def get_platforms(self, game_name):
        """
        Retrieve platforms for a given game

        :param game_name: Name of the game
        :return: List of platforms or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            return [platform['platform']['name'] for platform in game.get('platforms', [])]

        except requests.RequestException as e:
            print(f"Error retrieving game platforms: {e}")
            return None

    def get_release_date(self, game_name):
        """
        Retrieve release year for a given game

        :param game_name: Name of the game
        :return: Release year or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            release_date = game.get('released')
            return release_date[:4] if release_date else 'Unknown'

        except requests.RequestException as e:
            print(f"Error retrieving game release date: {e}")
            return None

    def get_rating(self, game_name):
        """
        Retrieve rating for a given game

        :param game_name: Name of the game
        :return: Rating or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            return game.get('rating', 0)

        except requests.RequestException as e:
            print(f"Error retrieving game rating: {e}")
            return None

    def get_metacritic(self, game_name):
        """
        Retrieve Metacritic score for a given game

        :param game_name: Name of the game
        :return: Metacritic score or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            return game.get('metacritic', 'N/A')

        except requests.RequestException as e:
            print(f"Error retrieving game Metacritic score: {e}")
            return None

    def get_website(self, game_name):
        """
        Retrieve website URL for a given game

        :param game_name: Name of the game
        :return: Website URL or None if not found
        """
        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    search_params['search'] = game_name_no_numbers
                    search_response = requests.get(
                        "https://api.rawg.io/api/games",
                        params=search_params,
                        verify=False
                    )
                    search_data = search_response.json()

                if not search_data.get('results'):
                    return None

            game = search_data['results'][0]
            game_id = game['id']

            game_details_response = requests.get(
                f"https://api.rawg.io/api/games/{game_id}",
                params={'key': self.api_key},
                verify=False
            )
            game_details = game_details_response.json()

            return game_details.get('website', '')

        except requests.RequestException as e:
            print(f"Error retrieving game website: {e}")
            return None

    def retrieve_game_metadata(self, game_name):
        """
        Retrieve metadata for a given game with retry logic and improved SSL handling

        :param game_name: Name of the game
        :return: Dictionary of game metadata
        """
        cached_metadata = self._check_cache(game_name)
        if cached_metadata:
            return cached_metadata

        try:
            search_params = {
                'key': self.api_key,
                'search': game_name,
                'page_size': 1
            }
            search_response = requests.get(
                "https://api.rawg.io/api/games",
                params=search_params,
                verify=False  # Disable SSL verification
            )
            search_data = search_response.json()

            if not search_data.get('results'):
                if re.search(r'\d+', game_name):
                    print(f"No results for '{game_name}'. Retrying without numbers.")
                    game_name_no_numbers = re.sub(r'\d+', '', game_name).strip()
                    return self.retrieve_game_metadata(game_name_no_numbers)

                return {
                    'name': game_name,
                    'found': False
                }

            game = search_data['results'][0]
            if not isinstance(game.get('id'), (str, int)):
                raise ValueError(f"Invalid game ID: {game.get('id')}")

            game_id = game['id']
            game_details_response = requests.get(
                f"https://api.rawg.io/api/games/{game_id}",
                params={'key': self.api_key},
                verify=False
            )
            game_details = game_details_response.json()

            metadata = {
                'name': game.get('name', game_name),
                'found': True,
                'description': game_details.get('description_raw', 'No description available'),
                'genres': [genre['name'] for genre in game.get('genres', [])],
                'platforms': [platform['platform']['name'] for platform in game.get('platforms', [])],
                'release_date': game.get('released', 'Unknown')[:4],
                'cover_url': game.get('background_image', ''),
                'rating': game.get('rating', 0),
                'metacritic': game.get('metacritic', 'N/A'),
                'website': game_details.get('website', '')
            }

            self._save_to_cache(game_name, metadata)
            return metadata

        except requests.RequestException as e:
            print(f"Error retrieving game metadata: {e}")
            return {
                'name': game_name,
                'found': False,
                'error': str(e)
            }
        except ValueError as e:
            print(f"Value error encountered: {e}")
            return {
                'name': game_name,
                'found': False,
                'error': str(e)
            }


if __name__ == "__main__":
    API_KEY = "74206afbba5d4287927acbdd696485f3"
    retriever = GameMetadataRetriever(API_KEY)

    game_name = "Bloons TD 6"

    # Example of using retrieve_game_metadata
    metadata = retriever.retrieve_game_metadata(game_name)
    if isinstance(metadata, dict) and metadata.get('found'):
        print("Game metadata retrieved successfully:")
        print(json.dumps(metadata, indent=2))
    else:
        print(f"Game metadata for '{game_name}' could not be retrieved.")

    # Example of using get_cover_url
    cover_url = retriever.get_cover_url(game_name)
    if cover_url:
        print(f"\nCover URL for {game_name}: {cover_url}")
    else:
        print(f"Could not find cover URL for {game_name}")

if __name__ == "__main__":
    API_KEY = "74206afbba5d4287927acbdd696485f3"
    retriever = GameMetadataRetriever(API_KEY)

    game_name = "Bloons TD 6"
    metadata = retriever.retrieve_game_metadata(game_name)
    if isinstance(metadata, dict) and metadata.get('found'):
        print("Game metadata retrieved successfully:")
        print(json.dumps(metadata, indent=2))
    else:
        print(f"Game metadata for '{game_name}' could not be retrieved.")
