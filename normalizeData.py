import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def clean_and_prepare_dataset(file_path: str, output_path: str = "cleaned_normalized_data.csv") -> pd.DataFrame:
    # Load dataset
    df = pd.read_csv(file_path)
    
    # Drop any rows with missing values
    df.dropna(inplace=True)

    # Convert Percent People in Poverty to decimal (e.g., 25% -> 0.25)
    df['Percent People in Poverty'] = df['Percent People in Poverty'] / 100

    # Categorize Median Income into brackets
    df['income_bracket'] = pd.cut(df['Median Household Income'], 
                                  bins=[0, 35000, 60000, 100000, float('inf')],
                                  labels=['Low', 'Middle', 'Upper-Middle', 'High'])

    # Categorize Population Density into brackets
    df['density_bracket'] = pd.cut(df['Population Density (Persons/Acre)'],
                                   bins=[0, 5, 20, 50, float('inf')],
                                   labels=['Low', 'Moderate', 'Dense', 'Very Dense'])

    # Columns to normalize (excluding ID, lat/lon, categorical fields)
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
    
    # Normalize using Min-Max Scaling
    scaler = MinMaxScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # Save cleaned & normalized data
    df.to_csv(output_path, index=False)

    return df

def add_custom_features(df: pd.DataFrame) -> pd.DataFrame:
    # Prevent divide-by-zero issues with a small epsilon
    epsilon = 1e-6

    # restaurant_to_coffee_ratio: indicates market saturation or opportunity
    df['restaurant_to_coffee_ratio'] = df['# of Nearby Restaurants'] / (df['# of Nearby Coffee Shops'] + epsilon)

    # coffee_shop_density: shows how packed the area is with coffee shops
    df['coffee_shop_density'] = df['# of Nearby Coffee Shops'] / (df['Population Density (Persons/Acre)'] + epsilon)

    # potential_demand_index: proxies for foot traffic and transit access
    df['potential_demand_index'] = (
        df['pedestrian_score'] + 
        df['transit_stops'] + 
        df['Population Density (Persons/Acre)']
    ) / (df['# of Nearby Coffee Shops'] + epsilon)

    # mosque_index: potential cultural alignment
    df['mosque_index'] = df['# of Nearby Mosques'] / (df['Population Density (Persons/Acre)'] + epsilon)

    # affordability_index: indicates disposable income, normalized economic well-being
    df['affordability_index'] = df['Median Household Income'] / (df['Percent People in Poverty'] + epsilon)

    return df


def calculate_success_score(df: pd.DataFrame) -> pd.DataFrame:
    # Optional: normalize features again before scoring (if not already scaled 0–1)
    features_to_scale = [
        'mosque_index', 
        'potential_demand_index', 
        'affordability_index', 
        'pedestrian_score', 
        'coffee_shop_density'
    ]

    # Normalize these features to 0–1 range
    scaler = MinMaxScaler()
    df[features_to_scale] = scaler.fit_transform(df[features_to_scale])

    # Compute success score using weighted formula
    df['success_score'] = (
        0.30 * df['mosque_index'] +
        0.25 * df['potential_demand_index'] +
        0.20 * df['affordability_index'] +
        0.15 * df['pedestrian_score'] +
        0.10 * (1 - df['coffee_shop_density'])  # inverse of saturation
    )

    # Sort neighborhoods by highest success score (optional)
    df.sort_values(by='success_score', ascending=False, inplace=True)

    return df

# Example usage:
# df_scored = calculate_success_score(df_features)


# Example usage:
df_prepared = clean_and_prepare_dataset("C:/Users/Owner/Desktop/code/cafe-compass/completeCafeCompassData.csv")
df_features = add_custom_features(df_prepared)
df_scored = calculate_success_score(df_features)

df_scored.to_csv("final_scored_data.csv", index=False)
print(df_scored[['Tract Code (id)', 'City', 'success_score']].head(10))