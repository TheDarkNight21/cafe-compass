import pandas as pd
from datetime import datetime
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
google_key = os.getenv("GOOGLE_MAPS_API_KEY")

if not google_key:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")

# API call functions (provided in your code)
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
        batch = places[i:i+25]
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
    coffee_shops = find_nearby_places(lat, lon, "cafe")
    return filter_places_by_travel_time(lat, lon, coffee_shops, walking_time_minutes, driving_time_minutes)

def update_nearby_places_counts(input_csv, output_csv):
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Iterate through each row and update counts
    for index, row in df.iterrows():
        # Skip if no centroid coordinates available
        if pd.isna(row['Center of Tract']):
            print(f"Skipping Tract {row['Tract Code (id)']} - no centroid coordinates")
            continue
            
        # Skip if counts already exist (uncomment if you want to skip already processed rows)
        # if (pd.notna(row['# of Nearby Mosques']) and 
        #     pd.notna(row['# of Nearby Restaurants']) and 
        #     pd.notna(row['# of Nearby Coffee Shops'])):
        #     continue
            
        try:
            # Parse latitude and longitude from Center of Tract
            lat, lon = map(float, row['Center of Tract'].split(','))
            
            print(f"Processing Tract {row['Tract Code (id)']} at {lat},{lon}")
            
            # Get counts for each place type with error handling
            try:
                mosques = get_mosques_within_distance(lat, lon)
                df.at[index, '# of Nearby Mosques'] = mosques['drivable_count']
            except Exception as e:
                print(f"Error getting mosques for Tract {row['Tract Code (id)']}: {str(e)}")
                df.at[index, '# of Nearby Mosques'] = 0
            
            try:
                restaurants = get_restaurants_within_distance(lat, lon)
                df.at[index, '# of Nearby Restaurants'] = restaurants['drivable_count']
            except Exception as e:
                print(f"Error getting restaurants for Tract {row['Tract Code (id)']}: {str(e)}")
                df.at[index, '# of Nearby Restaurants'] = 0
            
            try:
                coffee_shops = get_coffee_shops_within_distance(lat, lon)
                df.at[index, '# of Nearby Coffee Shops'] = coffee_shops['drivable_count']
            except Exception as e:
                print(f"Error getting coffee shops for Tract {row['Tract Code (id)']}: {str(e)}")
                df.at[index, '# of Nearby Coffee Shops'] = 0
            
            # Save progress after each tract (in case of interruption)
            df.to_csv(output_csv, index=False)
            print(f"Updated Tract {row['Tract Code (id)']}")
            
            # Add delay to avoid hitting API rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing Tract {row['Tract Code (id)']}: {str(e)}")
            continue
    
    print(f"Updated data saved to {output_csv}")


#print(updated_csv)
#input_csv = "C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv"  # Use the file with centroids
#output_csv = "C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv"
#update_nearby_places_counts(input_csv, output_csv)