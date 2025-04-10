import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
google_key = os.getenv("GOOGLE_MAPS_API_KEY")

if not google_key:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

def call_google_api(origin, destinations, mode):
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': origin,
        'destinations': '|'.join(destinations),
        'mode': mode,
        'key': google_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    durations = []
    if data['status'] == 'OK':
        for element in data['rows'][0]['elements']:
            durations.append(element['duration']['value'] / 60)  # Convert to minutes
    return durations


def find_nearby_places(lat, lon, place_type, radius=5000):
    """
    Use Google Places API to find nearby places of a certain type.
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "type": place_type,
        "key": google_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    places = []
    if data['status'] == 'OK':
        for place in data.get('results', []):
            location = place['geometry']['location']
            places.append({
                "name": place['name'],
                "latitude": location['lat'],
                "longitude": location['lng'],
                "address": place.get('vicinity')
            })
    return places


def filter_places_by_travel_time(origin_lat, origin_lon, places, walking_limit, driving_limit):
    origin = f"{origin_lat},{origin_lon}"
    walkable = []
    drivable = []

    for i in range(0, len(places), 25):
        batch = places[:25]
        destinations = [f"{place['latitude']},{place['longitude']}" for place in batch]

        walking_durations = call_google_api(origin, destinations, 'walking')
        driving_durations = call_google_api(origin, destinations, 'driving')
        
        for j, place in enumerate(batch):
            walk_time = walking_durations[j] if j < len(walking_durations) else None
            drive_time = driving_durations[j] if j < len(driving_durations) else None

            if walk_time is not None and walk_time <= walking_limit:
                walkable.append({**place, "walking_time_minutes": walk_time})
            if drive_time is not None and drive_time <= driving_limit:
                drivable.append({**place, "driving_time_minutes": drive_time})

    return {
        "walkable_count": len(walkable),
        "drivable_count": len(drivable),
        "walkable": walkable,
        "drivable": drivable,
        "timestamp": datetime.now()
    }



def get_restaurants_within_distance(lat, lon, walking_time_minutes=15, driving_time_minutes=10):
    restaurants = find_nearby_places(lat, lon, "restaurant")
    return filter_places_by_travel_time(lat, lon, restaurants, walking_time_minutes, driving_time_minutes)


def get_mosques_within_distance(lat, lon, walking_time_minutes=15, driving_time_minutes=10):
    mosques = find_nearby_places(lat, lon, "mosque")
    return filter_places_by_travel_time(lat, lon, mosques, walking_time_minutes, driving_time_minutes)


def get_coffee_shops_within_distance(lat, lon, walking_time_minutes=15, driving_time_minutes=10):
    coffee_shops = find_nearby_places(lat, lon, "coffee shop")
    return filter_places_by_travel_time(lat, lon, coffee_shops, walking_time_minutes, driving_time_minutes)

if __name__ == "__main__":
    lat, lon = 42.3223,-83.1763
    print(get_restaurants_within_distance(lat, lon))