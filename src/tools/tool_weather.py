import os
from typing import Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()


def tool_get_weather(location: str = 'Sofia, Bulgaria') -> Dict[str, Any]:
    """A tool to get the current weather information."""
    api_key = os.environ.get('WEATHER_API_KEY')

    if not api_key:
        raise Exception("WEATHER_API_KEY environment variable is not set")

    url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': location,
        'aqi': 'no'
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            error_data = response.json()
            raise Exception(f"Weather API error: {error_data.get('error', {}).get('message', 'Unknown error')}")

        data = response.json()

        # Extract relevant information
        result = {
            'location': f"{data['location']['name']}, {data['location']['country']}",
            'temperature': data['current']['temp_c'],
            'conditions': data['current']['condition']['text']
        }

        return result

    except requests.RequestException as e:
        raise Exception(f"Failed to fetch weather data: {str(e)}")

