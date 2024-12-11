import requests
import logging
from typing import Any, Dict
from dotenv import load_dotenv
import os
from logger import configure_logger
from geopy.geocoders import Nominatim



load_dotenv()
def get_lat_long(location_name):
        geolocator = Nominatim(user_agent="my_geocoder")
        location = geolocator.geocode(location_name)

        if location:
            return location.latitude, location.longitude
        else:
            return None



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


    def get_weather(self, location_name: str):
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
            url  = "https://api.openweathermap.org/data/3.0/onecall/overview?"
            # Construct the API request URL
            latlong = get_lat_long(location_name)
            params = {
                "lat": latlong[0],
                "lon": latlong[1],
                "appid": self.api_key,
                "units": "imperial",  # Use "imperial" for Fahrenheit
            }
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse and return the weather data
            
            weather_data = response.json()
            self.logger.info("Weather data for %s fetched", location_name)
            return f"Location: {location_name} \n Date: {weather_data['date']} \n Overview: {weather_data['weather_overview']}"

        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to fetch weather data for %s: %s", location_name, str(e))
            raise ValueError(f"Error fetching weather data for location '{location_name}': {str(e)}")

        except KeyError as e:
            self.logger.error("Unexpected response structure: %s", str(e))
            raise ValueError("Unexpected response structure from weather API")
        
    def get_daily_forecast(self, location_name: str):
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
            url  = "https://api.openweathermap.org/data/3.0/onecall?"
            # Construct the API request URL
            latlong = get_lat_long(location_name)
            params = {
                "lat": latlong[0],
                "lon": latlong[1],
                "appid": self.api_key,
                "exclude": "current,minutely,hourly",
                "units": "imperial",  # Use "imperial" for Fahrenheit
            }
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse and return the weather data
            
            weather_data = response.json()
            self.logger.info("Weather data for %s fetched", location_name)
            return f"Location: {location_name} \n High: {weather_data['daily'][0]['temp']['max']}F \n Low: {weather_data['daily'][0]['temp']['min']}F \n Humidity: {weather_data['daily'][0]['humidity']}% \n Weather: {weather_data['daily'][0]['weather'][0]['description']} \n Alerts: {weather_data['alerts'][0]['description']}"

        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to fetch weather data for %s: %s", location_name, str(e))
            raise ValueError(f"Error fetching weather data for location '{location_name}': {str(e)}")

        except KeyError as e:
            self.logger.error("Unexpected response structure: %s", str(e))
            raise ValueError("Unexpected response structure from weather API")
        
    
    def get_hourly_forecast(self, location_name: str):
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
            url  = "https://api.openweathermap.org/data/3.0/onecall?"
            # Construct the API request URL
            latlong = get_lat_long(location_name)
            params = {
                "lat": latlong[0],
                "lon": latlong[1],
                "appid": self.api_key,
                "exclude": "current,minutely,daily",
                "units": "imperial",  # Use "imperial" for Fahrenheit
            }
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse and return the weather data
            
            weather_data = response.json()
            self.logger.info("Weather data for %s fetched", location_name)
            return f"Location: {location_name} \n High: {weather_data['hourly'][0]['temp']['max']}F \n Low: {weather_data['hourly'][0]['temp']['min']}F \n Humidity: {weather_data['hourly'][0]['humidity']}% \n Weather: {weather_data['hourly'][0]['weather'][0]['description']} \n Alerts: {weather_data['alerts'][0]['description']}"

        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to fetch weather data for %s: %s", location_name, str(e))
            raise ValueError(f"Error fetching weather data for location '{location_name}': {str(e)}")

        except KeyError as e:
            self.logger.error("Unexpected response structure: %s", str(e))
            raise ValueError("Unexpected response structure from weather API")
        
    def get_date_forecast(self, location_name: str, date: str):
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
            url  = "https://api.openweathermap.org/data/3.0/onecall/day_summary?"
            # Construct the API request URL
            latlong = get_lat_long(location_name)
            params = {
                "lat": latlong[0],
                "lon": latlong[1],
                "appid": self.api_key,
                "date": date,
                "units": "imperial",  # Use "imperial" for Fahrenheit
            }
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse and return the weather data
            
            weather_data = response.json()
            self.logger.info("Weather data for %s fetched", location_name)
            return f"Location: {location_name} \n Date: {weather_data['date']} (YYYY-MM-DD) \n High: {weather_data['temperature']['max']}F \n Low: {weather_data['temperature']['min']}F \n Precipitation: {weather_data['precipitation']['total']} inches \n Humidity: {weather_data['humidity']['afternoon']}%"

        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to fetch weather data for %s: %s", location_name, str(e))
            raise ValueError(f"Error fetching weather data for location '{location_name}': {str(e)}")

        except KeyError as e:
            self.logger.error("Unexpected response structure: %s", str(e))
            raise ValueError("Unexpected response structure from weather API")

#if __name__ == "__main__":
    #client = WeatherClient()
    #print(client.get_date_forecast("New York City","2024-9-10"))