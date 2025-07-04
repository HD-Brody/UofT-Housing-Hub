import os
import requests
import openrouteservice
from dotenv import load_dotenv


def get_travel_details(coords: tuple, mode = 'foot-walking', destination = (-79.39559, 43.662571)) -> tuple[float]:
    '''
    Return tuple containing travel distance in kilometers and duration in minutes based on the mode of transportation between address and destination.
    By default, mode of transportation is walking and destination is UofT front campus.
    '''
    # Load environment variables from .env file
    load_dotenv()  

    api_key = os.getenv("ORS_API_KEY")

    client = openrouteservice.Client(key=api_key)

    route = client.directions(coordinates=(coords, destination), profile='foot-walking',format='geojson')

    duration_seconds = route['features'][0]['properties']['summary']['duration']
    distance_meters = route['features'][0]['properties']['summary']['distance']

    return round(duration_seconds/60, 1), round(distance_meters/1000, 2)


def get_coordinates(address: str) -> tuple:
    # Load environment variables from .env file
    load_dotenv()  

    api_key = os.getenv("ORS_API_KEY")

    url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": api_key,
        "text": address,
        "boundary.country": "CA",
        "focus.point.lat": 43.662571,
        "focus.point.lon": -79.39559
    }

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise if status code != 200

    data = response.json()
    features = data.get("features", [])
    if not features:
        raise ValueError(f"No results found for address: {address}")

    coords = features[0]['geometry']['coordinates']  # [lon, lat]
    return coords


if __name__ == '__main__':
    test_address = "601 - 280 DUNDAS Street W , Toronto - Kensington-Chinatown"
    print(get_coordinates(test_address))