import pandas as pd
import requests
import geopandas as gpd


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

#county_mapping = build_county_mapping("C:/Users/Owner/Desktop/code/cafe-compass/data collection/dataFiles/tl_2024_26_tabblock20.shp")

def add_county_id_to_csv(input_csv: str, output_csv: str) -> None:
    """
    Adds a 'county_id' column to a CSV based on tract numbers by matching with the block-level TIGER/Line file.

    Args:
        input_csv: Path to the CSV missing county info (must have 'tract_number' column).
        output_csv: Path to save the new CSV with 'county_id' column.
    """
    try:
        # Load the input CSV
        df = pd.read_csv(input_csv, dtype=str)

        # Load the TIGER/Line CSV
        tiger_df = pd.read_csv(
            'C:/Users/Owner/Desktop/code/cafe-compass/data collection/vertopal.com_tl_2024_26_tabblock20.csv',
            dtype=str
        )

        # Prepare a lookup dictionary from tract number to county ID
        tract_to_county = tiger_df.drop_duplicates(subset=['BLOCKCE20,C,4']) \
                                  .set_index('BLOCKCE20,C,4')['COUNTYFP20,C,3'].to_dict()

        # Add county_id to each row
        df['county_id'] = df['Tract Code (id)'].map(tract_to_county)

        # Notify if some rows didn't get matched
        unmatched = df['county_id'].isna().sum()
        if unmatched > 0:
            print(f"⚠️ {unmatched} rows did not match a county ID.")

        # Save the updated CSV
        df.to_csv(output_csv, index=False)
        print(f"✅ Saved updated CSV with county IDs to {output_csv}")

    except Exception as e:
        print(f"❌ Error processing county IDs: {e}")


def add_rent_data(input_csv_path, output_csv_path):
    """
    Adds average rent data (per sqft) to a CSV using county FIPS code (county_id).
    
    Args:
        input_csv_path (str): Path to input CSV with a 'county_id' column (e.g., "082").
        output_csv_path (str): Path to save the enhanced CSV.
    """

    try:
        # Load your dataset
        df = pd.read_csv(input_csv_path, dtype={'county_id': str})
        df['county_id'] = df['county_id'].str.zfill(3)
    except Exception as e:
        print(f"❌ Failed to load input CSV: {e}")
        return

    # USDA API URL — this should be checked if it actually provides what you need
    USDA_API_URL = (
        "https://api.ers.usda.gov/data/arms/surveydata"
        "?api_key=nBB2gbkg6qGHQ0oS5aKlgdlqhhd7dSwnW3WVbQMR"
        "&variable=RENT&year=2023&state=MI"
    )

    # Step 1: Fetch rent data from USDA API
    try:
        response = requests.get(USDA_API_URL)
        response.raise_for_status()
        rent_data = response.json()
        
        print("🔍 USDA API Response Keys:", rent_data.keys())
        print("🧾 Sample Data:", rent_data.get("data", [{}])[0])


        # Check structure
        if "data" not in rent_data:
            print("❌ Unexpected USDA API response format.")
            return

        rent_df = pd.DataFrame(rent_data["data"])

        # Ensure required columns exist
        if not {'county_code', 'value'}.issubset(rent_df.columns):
            print("❌ USDA rent data missing required fields.")
            return

        rent_df = rent_df[['county_code', 'value']].copy()
        rent_df.rename(columns={'value': 'avg_rent_per_sqft'}, inplace=True)
        rent_df['county_id'] = rent_df['county_code'].astype(str).str.zfill(3)

    except Exception as e:
        print(f"❌ Failed to fetch USDA rent data: {e}")
        return

    # Step 2: Merge rent data
    try:
        df = pd.merge(df, rent_df[['county_id', 'avg_rent_per_sqft']], on='county_id', how='left')
    except Exception as e:
        print(f"❌ Failed during merge operation: {e}")
        return

    # Step 3: Save to output CSV
    try:
        df.to_csv(output_csv_path, index=False)
        print(f"✅ Rent data added successfully. Output saved to {output_csv_path}")
    except Exception as e:
        print(f"❌ Failed to save output CSV: {e}")


#add_county_id_to_csv(
    #input_csv="C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv",
    #output_csv="C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv"
#)

print("County IDs added successfully.")
# Usage
add_rent_data("C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv", 
              "C:/Users/Owner/Desktop/code/cafe-compass/data collection/completeCafeCompassData.csv")