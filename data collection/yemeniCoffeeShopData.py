import googlemaps
import pandas as pd
import time
from dotenv import load_dotenv
import os

load_dotenv()

googlemapsKey = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps = googlemaps.Client(key=googlemapsKey)

search_points = [
    {"county": "Wayne", "city": "Dearborn", "lat": 42.3223, "lon": -83.1763},
    {"county": "Oakland", "city": "Troy", "lat": 42.6056, "lon": -83.1499},
    {"county": "Macomb", "city": "Warren", "lat": 42.5145, "lon": -83.0147},
    {"county": "Washtenaw", "city": "Ann Arbor", "lat": 42.2808, "lon": -83.7430},
    {"county": "Monroe", "city": "Monroe", "lat": 41.9164, "lon": -83.3977},
    {"county": "Livingston", "city": "Howell", "lat": 42.6073, "lon": -83.9294},
    {"county": "St. Clair", "city": "Port Huron", "lat": 42.9709, "lon": -82.4249}
]

results = []

for loc in search_points:
    print(f"Searching around {loc['city']}, {loc['county']} County...")
    response = gmaps.places_nearby(
        location=(loc['lat'], loc['lon']),
        radius=30000,
        keyword="Yemeni coffee"
    )

    for place in response.get('results', []):
        results.append({
            "name": place["name"],
            "address": place.get("vicinity", ""),
            "lat": place["geometry"]["location"]["lat"],
            "lon": place["geometry"]["location"]["lng"],
            "county": loc['county']
        })

    time.sleep(2)  # Respect API rate limits

# Remove duplicates (some businesses may appear in overlapping areas)
df_shops = pd.DataFrame(results).drop_duplicates(subset=["name", "lat", "lon"])
df_shops.to_csv("yemeni_coffee_shops_se_mi.csv", index=False)
print("✅ Data saved to yemeni_coffee_shops_se_mi.csv")
