import geopandas as gpd


import geopandas as gpd

def get_tract_centroid(tract_number, county_number):
    # Load shapefile
    gdf = gpd.read_file("data collection/tl_2024_26_tabblock20.shp")
    
    # Filter for the given County and Tract
    tract = gdf[(gdf["COUNTYFP20"] == county_number) & (gdf["BLOCKCE20"] == tract_number)].copy()
    
    # Project to a UTM coordinate system (optional step for area/centroid calcs)
    tracts_proj = tract.to_crs(epsg=32616)
    
    # Dissolve to get single geometry for the tract
    tract_dissolved = tracts_proj.dissolve()
    
    # Convert back to WGS84 (lat/lon)
    tract_dissolved_wgs = tract_dissolved.to_crs(epsg=4326)
    
    # Get representative point (in lat/lon)
    rep_point = tract_dissolved_wgs.geometry.representative_point()
    
    # Extract lat and lon
    lon, lat = rep_point.iloc[0].x, rep_point.iloc[0].y
    
    return lat, lon

# Example usage:
tract_number = "4018"
county_number = "161"
lat, lon = get_tract_centroid(tract_number, county_number)
print(f'{lat}, {lon}')
