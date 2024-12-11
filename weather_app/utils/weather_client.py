import requests
import logging
from typing import Any, Dict
from dotenv import load_dotenv
import os
from weather_app.utils.logger import configure_logger


load_dotenv()


class WeatherClient:
    """
    A client for fetching weather data from an external API.
    """
    def __init__(self, base_url: str = "https://api.openweathermap.org/data/2.5/weather"):
        """
        Initializes the WeatherClient.

        Args:
            api_key (str): The API key for accessing the weather service.
            base_url (str): The base URL of the weather service API.
        """
        self.api_key = os.getenv("API_KEY")
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        configure_logger(self.logger)

    def get_weather(self, location_name: str) -> Dict[str, Any]:
        """
        Fetches weather data for a given location.

        Args:
            location_name (str): The name of the location (e.g., city name).

        Returns:
            Dict[str, Any]: A dictionary containing weather data for the location.

        Raises:
            ValueError: If the API request fails or the location is not found.
        """
        self.logger.info("Fetching weather data for location: %s", location_name)

        try:
            # Construct the API request URL
            params = {
                "q": location_name,
                "appid": self.api_key,
                "units": "metric",  # Use "imperial" for Fahrenheit
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse and return the weather data
            weather_data = response.json()
            self.logger.info("Weather data for %s: %s", location_name, weather_data)
            return {
                "location": weather_data.get("name"),
                "temperature": weather_data["main"]["temp"],
                "description": weather_data["weather"][0]["description"],
                "humidity": weather_data["main"]["humidity"],
                "wind_speed": weather_data["wind"]["speed"],
            }

        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to fetch weather data for %s: %s", location_name, str(e))
            raise ValueError(f"Error fetching weather data for location '{location_name}': {str(e)}")

        except KeyError as e:
            self.logger.error("Unexpected response structure: %s", str(e))
            raise ValueError("Unexpected response structure from weather API")

