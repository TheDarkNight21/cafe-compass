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

# Example usage:
df_features = add_custom_features(df_prepared)
df_features.to_csv("features_added_data.csv", index=False)