from tqdm import tqdm
import pandas as pd
import geopandas as gpd
import requests
import osmnx as ox
import time


def parse_lat_lon(coord):
    try:
        if pd.isna(coord):
            return None, None
        coord_str = str(coord)
        lat, lon = map(float, coord_str.split(','))
        return lat, lon
    except Exception as e:
        print(f"Failed to parse coordinate: {coord} – {e}")
        return None, None

def add_mobility_features(input_csv: str, output_csv: str, radius_meters: int = 1609) -> None:
    """
    Enhances a tract-level CSV with mobility features:
    - Number of transit stops within a radius.
    - Pedestrian activity score (walkability + nearby businesses).
    
    Args:
        input_csv: Path to input CSV with columns: ['id', 'lat', 'lon', ...].
        output_csv: Path to save the enhanced CSV.
        radius_meters: Search radius for transit stops (default: 1609m ~ 1 mile).
    """
    df = pd.read_csv(input_csv)
    df[['lat', 'lon']] = df['Center of Tract'].apply(parse_lat_lon).apply(pd.Series)
    geometry = gpd.points_from_xy(df['lon'], df['lat'])
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    gdf['transit_stops'] = 0
    gdf['pedestrian_score'] = 0.0

    # --- 1. Get Transit Stops from OpenStreetMap ---
    print("Fetching transit stops from OSM...")
    for idx, row in tqdm(gdf.iterrows(), total=gdf.shape[0], desc="Transit Stops", unit="tract"):
        if pd.isna(row['lat']) or pd.isna(row['lon']):
            print(f"Skipping tract at index {idx} due to missing coordinates.")
            continue
        try:
            query = f"""
[out:json];
(
  node(around:{radius_meters},{row['lat']},{row['lon']})[highway=bus_stop];
  node(around:{radius_meters},{row['lat']},{row['lon']})[public_transport=stop_position];
);
out count;
"""
            response = requests.get("https://overpass-api.de/api/interpreter", params={"data": query})

            if response.status_code != 200:
                print(f"Bad response ({response.status_code}): {response.text}")
                raise ValueError("Overpass API returned non-200 response.")

            data = response.json()
            count = len(data.get("elements", []))
            gdf.at[idx, 'transit_stops'] = count
        except Exception as e:
            print(f"Error fetching OSM data for index {idx}: {e}")
            gdf.at[idx, 'transit_stops'] = None

        time.sleep(1)

    # --- 2. Calculate Pedestrian Score ---
    print("Calculating pedestrian scores...")
    for idx, row in tqdm(gdf.iterrows(), total=gdf.shape[0], desc="Pedestrian Score", unit="tract"):
        try:
            G = ox.graph_from_point((row['lat'], row['lon']), dist=500, network_type='walk')
            walkability = len(G.nodes) / 100  # Normalized

            business_density = (row['# of Nearby Restaurants'] + row['# of Nearby Coffee Shops']) / 10  # Normalized

            gdf.at[idx, 'pedestrian_score'] = 0.6 * walkability + 0.4 * business_density
        except Exception as e:
            print(f"Error for tract {row.get('Tract Code (id)', 'unknown')}: {e}")
            gdf.at[idx, 'pedestrian_score'] = None

    gdf.drop(columns=['geometry']).to_csv(output_csv, index=False)
    print(f"Saved enhanced data to {output_csv}")


# Example Usage
add_mobility_features("C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv", 
                      "C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv")