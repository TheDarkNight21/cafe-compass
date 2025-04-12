import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
import re
from geopy.geocoders import Nominatim

# Function to extract the city from the address field
geolocator = Nominatim(user_agent="cafe_compass")

# Global cache dictionary
geocode_cache = {}

def extract_city(lat, lon):
    """Extract the city based on latitude and longitude using reverse geocoding"""
    key = (round(lat, 5), round(lon, 5))
    if key in geocode_cache:
        return geocode_cache[key].get('city', '')

    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        location = geolocator.reverse((lat, lon), language='en')
        if location:
            address_components = location.raw.get('address', {})
            geocode_cache[key] = address_components
            return address_components.get('city', '')
    return ""

def extract_county(lat, lon):
    """Extract the county based on latitude and longitude using reverse geocoding"""
    key = (round(lat, 5), round(lon, 5))
    if key in geocode_cache:
        return geocode_cache[key].get('county', '')

    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        location = geolocator.reverse((lat, lon), language='en')
        if location:
            address_components = location.raw.get('address', {})
            geocode_cache[key] = address_components
            return address_components.get('county', '')
    return ""


def clean_city_name(city):
    """Normalize city names by removing unwanted suffixes and punctuation."""
    if isinstance(city, str):
        city = city.lower().strip()  # Convert to lowercase and remove extra spaces
        city = re.sub(r'\s*twp$', '', city)  # Remove 'twp' (township) suffix
        city = re.sub(r'\s*\(.*\)', '', city)  # Remove text inside parentheses
    return city

def clean_county_name(county):
    """Standardize county names: lowercase, strip, remove 'county' suffix."""
    if isinstance(county, str):
        county = county.lower().strip()
        county = county.replace("county", "").lower().strip()
    return county


# Clean and prepare the dataset
def clean_and_prepare_dataset(file_path: str, output_path: str = "cleaned_normalized_data.csv") -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df.dropna(inplace=True)

    # Convert Percent People in Poverty to decimal
    df['Percent People in Poverty'] = df['Percent People in Poverty'] / 100

    # Create income brackets
    df['income_bracket'] = pd.cut(df['Median Household Income'], 
                                  bins=[0, 35000, 60000, 100000, float('inf')], 
                                  labels=['Low', 'Middle', 'Upper-Middle', 'High'])

    # Create density brackets
    df['density_bracket'] = pd.cut(df['Population Density (Persons/Acre)'],
                                   bins=[0, 5, 20, 50, float('inf')],
                                   labels=['Low', 'Moderate', 'Dense', 'Very Dense'])

    # Normalize the numeric columns
    numeric_cols = [
        "Median Age", 
        "Median Household Income", 
        "Percent People in Poverty", 
        "Population Density (Persons/Acre)", 
        "# of Nearby Restaurants", 
        "# of Nearby Coffee Shops", 
        "# of Nearby Mosques", 
        "transit_stops", 
        "pedestrian_score"
    ]

    scaler = MinMaxScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    
    df['City'] = df['City'].apply(clean_city_name)
    
    print("applying counties.")
    df['county'] = df.apply(lambda row: extract_county(row['lat'], row['lon']), axis=1)
    df['county'] = df['county'].astype(str).str.lower().str.strip()

    df.reset_index(drop=True, inplace=True)
    df.to_csv(output_path, index=False)

    return df

# Add custom features to the dataset
def add_custom_features(df: pd.DataFrame) -> pd.DataFrame:
    epsilon = 1e-6
    df['restaurant_to_coffee_ratio'] = df['# of Nearby Restaurants'] / (df['# of Nearby Coffee Shops'] + epsilon)
    df['coffee_shop_density'] = df['# of Nearby Coffee Shops'] / (df['Population Density (Persons/Acre)'] + epsilon)
    df['potential_demand_index'] = (
        df['pedestrian_score'] + 
        df['transit_stops'] + 
        df['Population Density (Persons/Acre)']
    ) / (df['# of Nearby Coffee Shops'] + epsilon)
    df['mosque_index'] = df['# of Nearby Mosques'] / (df['Population Density (Persons/Acre)'] + epsilon)
    df['affordability_index'] = df['Median Household Income'] / (df['Percent People in Poverty'] + epsilon)
    return df

# Label neighborhoods based on known Yemeni coffee shop data
def label_success_from_known_shops(df: pd.DataFrame, known_shop_data_path: str) -> pd.DataFrame:
    known_shops = pd.read_csv(known_shop_data_path)

    # Extract and clean city and county info using reverse geocoding (cached)
    print("Reverse geocoding cities for Yemeni coffee shops...")
    known_shops['City'] = known_shops.apply(lambda row: extract_city(row['lat'], row['lon']), axis=1)
    known_shops['City'] = known_shops['City'].apply(clean_city_name)

    print("Overwriting counties for Yemeni coffee shops using reverse geocoding...")
    known_shops['county'] = known_shops.apply(lambda row: extract_county(row['lat'], row['lon']), axis=1)
    known_shops['county'] = known_shops['county'].astype(str).str.lower().str.strip()

    # Debug before merging
    print("== Unique counties in known_shops ==")
    print(known_shops['county'].drop_duplicates().sort_values())
    
    print(df.columns)

    print("\n== Unique counties in prepared df ==")
    print(df['county'].drop_duplicates().sort_values())

    # Merge
    df = df.merge(
        known_shops[['City', 'county', 'isSuccessful']],
        on=['City', 'county'],
        how='left'
    )

    # Post-merge diagnostics
    print("\nRows before merge:", len(df))
    print("Rows after merge:", len(df))
    print("Non-NaN isSuccessful count:", df['isSuccessful'].notna().sum())
    print("NaNs in isSuccessful:", df['isSuccessful'].isna().sum())

    print("\nTop unmatched (NaN) entries after merge:")
    print(df[df['isSuccessful'].isna()][['City', 'county']].value_counts().head(10))
    
    df['isSuccessful'] = df['isSuccessful'].replace(0, 1)

    return df



# Train a model to predict success based on labeled data
def train_success_prediction_model(df: pd.DataFrame) -> pd.DataFrame:
    features = [
        'mosque_index', 
        'potential_demand_index', 
        'affordability_index', 
        'pedestrian_score', 
        'coffee_shop_density',
        '# of Nearby Coffee Shops'
    ]

    X = df[features]
    df['isSuccessful'] = df_labeled['isSuccessful'].fillna(0)
    y = df['isSuccessful']
    

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Predict success probability for all areas
    if hasattr(clf, "predict_proba"):
        df['predicted_success_prob'] = clf.predict_proba(X)[:, 1]
    else:
        df['predicted_success_prob'] = clf.predict(X)

    return df

def add_city_column_to_yemeni_shops(csv_path: str, output_path: str):
    # Read CSV file
    df = pd.read_csv(csv_path)

    # Add a city column based on reverse geocoding
    df['city'] = df.apply(lambda row: extract_city(row['lat'], row['lon']), axis=1)
    
    # Optionally, you could also clean up or normalize city names as before
    df['city'] = df['city'].apply(clean_city_name)

    # Save the updated dataframe
    df.to_csv(output_path, index=False)
    print(f"Updated CSV saved to {output_path}")

    return df

# Run the entire processing pipeline
raw_data_path = "C:/Users/Owner/Desktop/code/cafe-compass/csvFiles/completeCafeCompassData.csv"
cleaned_data_path = "C:/Users/Owner/Desktop/code/cafe-compass/csvFiles/cleaned_normalized_data.csv"
yemeni_data_path = "C:/Users/Owner/Desktop/code/cafe-compass/csvFiles/yemeniCoffeeShopsWithSuccess.csv"

# Step 1: Clean and Normalize the data
#df_prepared = clean_and_prepare_dataset(raw_data_path)
print("step 1 done")
df_prepared = pd.read_csv(cleaned_data_path)

# Step 2: Add custom features
df_features = add_custom_features(df_prepared)
print("step 2 done")

df_test = pd.read_csv(yemeni_data_path, usecols=['city','county', 'isSuccessful'])
print("step 3 done")

# Step 3: Label neighborhoods based on known Yemeni coffee shops
df_labeled = label_success_from_known_shops(df_features, yemeni_data_path)
print("step 4 done")
print(df_labeled.columns)
print(df_labeled['isSuccessful'].value_counts())

# Step 4: Train a Random Forest model and predict success probabilities
df_scored = train_success_prediction_model(df_labeled)
print("step 5 done")

# Step 5: Save the final dataset with predicted success probabilities
df_scored.to_csv("final_scored_with_predictions.csv", index=False)
print("step 6 done")

# Output top 10 neighborhoods with highest predicted success probability
print(df_scored[['Tract Code (id)', 'City', 'predicted_success_prob']].sort_values(by='predicted_success_prob', ascending=False).head(10))
