import pandas as pd
import geopandas as gpd

# Function: Gets centroid from block-level CSV (your original fallback method)
def get_tract_centroid_from_csv(tract_number, county_number):
    try:
        df = pd.read_csv('C:/Users/Owner/Desktop/code/cafe-compass/data collection/vertopal.com_tl_2024_26_tabblock20.csv', dtype=str)
        match = df[(df['BLOCKCE20,C,4'] == tract_number) &
                   (df['COUNTYFP20,C,3'] == county_number)]
        if match.empty:
            return None
        lat = match.iloc[0]['INTPTLAT20,C,11']
        lon = match.iloc[0]['INTPTLON20,C,12']
        return f"{lat}, {lon}"
    except Exception as e:
        print(f"Error reading from block-level CSV: {str(e)}")
        return None

# Function: Gets centroid from Census 2020 Tract-Level CSV
def get_centroid_from_census_csv(tract_number, county_code, csv_path):
    try:
        df = pd.read_csv(csv_path, dtype=str)
        tract_number = tract_number.zfill(6)
        county_code = county_code.zfill(3)
        match = df[(df['TRACTCE'] == tract_number) & (df['COUNTYFP'] == county_code)]
        if match.empty:
            return None
        lat = match.iloc[0]['LATITUDE']
        lon = match.iloc[0]['LONGITUDE']
        return f"{lat}, {lon}"
    except Exception as e:
        print(f"Error reading from census tract-level CSV: {str(e)}")
        return None

# Function: Build the county mapping from shapefile with manual fallback
def build_county_mapping(shapefile_path):
    county_map = {
        '5': '163', '8005': '163', '8010': '163',
        '5120': '115',
        '6060': '147', '6065': '147', '6070': '147', '6075': '147',
        '6080': '147', '6085': '147', '6090': '147', '6095': '147',
        '6100': '147', '6105': '147', '6110': '147', '6115': '147',
        '6125': '147', '6135': '147', '6140': '147', '6145': '147',
        '6150': '147', '6155': '147', '6160': '147', '6165': '147',
        '7015': '093', '7020': '093', '7025': '093', '7030': '093',
        '7035': '093', '7040': '093', '7045': '093', '7050': '093',
        '7055': '093', '7060': '093', '7065': '093', '7070': '093',
        '7075': '093', '7080': '093', '7085': '093', '7090': '093',
        '7095': '093', '7100': '093',
        '8015': '161',
        '8020': '125'
    }

    try:
        gdf = gpd.read_file(shapefile_path)
        if 'BLOCKCE20' in gdf.columns:
            auto_map = gdf.groupby('BLOCKCE20')['COUNTYFP20'].first().to_dict()
            county_map.update({k: v for k, v in auto_map.items() if k not in county_map and pd.notna(v)})
        if len(county_map) < 100 and 'GEOID20' in gdf.columns:
            gdf['TRACT'] = gdf['GEOID20'].str[5:11].str.lstrip('0')
            auto_map = gdf.groupby('TRACT')['COUNTYFP20'].first().to_dict()
            county_map.update({k: v for k, v in auto_map.items() if k not in county_map and pd.notna(v)})
    except Exception as e:
        print(f"Warning: Could not read shapefile. Error: {e}")

    return {str(k): str(v) for k, v in county_map.items() if v is not None}

# Main function that populates the centroids
def add_centroids_to_csv(input_csv, output_csv, census_csv_path):
    df = pd.read_csv(input_csv)
    county_mapping = build_county_mapping("C:/Users/Owner/Desktop/code/cafe-compass/data collection/dataFiles/tl_2024_26_tabblock20.shp")

    for index, row in df.iterrows():
        tract_id = str(row['Tract Code (id)'])

        if pd.notna(row.get('Center of Tract', None)):
            continue

        county_number = county_mapping.get(tract_id)

        if not county_number:
            print(f"County not found for Tract {tract_id}")
            df.at[index, 'Center of Tract'] = None
            continue

        # Try block-level centroid first
        centroid = get_tract_centroid_from_csv(tract_id, county_number)

        # If block-level fails, fallback to census centroid
        if centroid is None:
            centroid = get_centroid_from_census_csv(tract_id, county_number, census_csv_path)

        if centroid:
            print(f"Tract {tract_id}: {centroid}")
            df.at[index, 'Center of Tract'] = centroid
        else:
            print(f"Tract {tract_id}: Could not determine centroid")
            df.at[index, 'Center of Tract'] = None

    df.to_csv(output_csv, index=False)
    print(f"Saved updated data to {output_csv}")

# Call with your paths
add_centroids_to_csv(
    input_csv="C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData2.csv",
    output_csv="C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv",
    census_csv_path="C:/Users/Owner/Desktop/code/cafe-compass/data collection/CenPop2020_Mean_TR26.csv"
)


    

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