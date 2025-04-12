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

    # Search for nearby Yemeni coffee places
    response = gmaps.places_nearby(
        location=(loc['lat'], loc['lon']),
        radius=30000,
        keyword="Yemeni coffee"
    )

    for place in response.get('results', []):
        place_id = place['place_id']
        
        # Fetch detailed place information using the place_id
        place_details = gmaps.place(place_id=place_id)
        
        # Extract desired data
        details = place_details.get('result', {})
        
        results.append({
            "name": place["name"],
            "address": details.get("vicinity", ""),
            "lat": place["geometry"]["location"]["lat"],
            "lon": place["geometry"]["location"]["lng"],
            "county": loc['county'],
            "rating": details.get("rating", None),  # Average rating
            "user_ratings_total": details.get("user_ratings_total", None),  # Total number of user ratings
            "price_level": details.get("price_level", None),  # Price level (1 to 4 scale)
            "reviews": details.get("reviews", []),  # User reviews
            "business_status": details.get("business_status", None),  # Open or closed
            "hours": details.get("opening_hours", {}).get("weekday_text", None)  # Business hours
        })
        
    time.sleep(2)  # Respect API rate limits

# Remove duplicates (some businesses may appear in overlapping areas)
df_shops = pd.DataFrame(results).drop_duplicates(subset=["name", "lat", "lon"])

# Function to determine if a business is successful based on the metrics
def determine_successful_businesses(df):
    def is_successful(row):
        score = 0
        
        # Rating: 1 if >= 4, else 0
        if row['rating'] >= 4:
            score += 1
        
        # User Ratings Total: 1 if > 100 reviews, else 0
        if row['user_ratings_total'] > 100:
            score += 1
        
        # Price Level: 1 if price level is 2 or 3 (balanced range), else 0
        if row['price_level'] in [2, 3]:
            score += 1
        
        # Reviews: Check for positive reviews (simplified logic for illustration)
        positive_keywords = ['good', 'excellent', 'great', 'awesome']
        if any(keyword in row['reviews'] for keyword in positive_keywords):
            score += 1
        
        # Business Status: 1 if OPEN, else 0
        if row['business_status'] == 'OPEN':
            score += 1
        
        # Hours: 1 if open for more than 12 hours, else 0
        try:
            start_time, end_time = row['hours'][0].split(' - ')  # Assuming weekday_text is a list
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
            if end_hour - start_hour > 12:
                score += 1
        except:
            pass
        
        # Determine success: If score >= threshold (e.g., 4), it's successful
        return 1 if score >= 3 else 0

    # Apply the function to each row and add the new column 'isSuccessful'
    df['isSuccessful'] = df.apply(is_successful, axis=1)
    
    return df

# Apply the function to determine success of each business
df_shops = determine_successful_businesses(df_shops)

# Save the data to a CSV file
df_shops.to_csv("yemeniCoffeeShops_with_success.csv", index=False)
print("✅ Data saved to yemeniCoffeeShops_with_success.csv")
