import folium
from folium.plugins import MarkerCluster
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import DBSCAN
import numpy as np

import folium
import pandas as pd
import branca

def create_yemeni_coffee_success_map(neighborhood_data, known_shop_locations, output_path="success_map.html"):
    # Create color scale from red (low) to green (high)
    colormap = branca.colormap.LinearColormap(
        colors=['red', 'yellow', 'green'],
        vmin=neighborhood_data['success_score'].min(),
        vmax=neighborhood_data['success_score'].max()
    )
    colormap.caption = 'Yemeni Coffee Shop Success Score'

    # Create the map centered in Southeast Michigan
    m = folium.Map(location=[42.3, -83.1], zoom_start=9)

    # Plot neighborhoods with success_score as color
    for _, row in neighborhood_data.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=6,
            popup=folium.Popup(f"Score: {row['success_score']:.2f}<br>City: {row['City']}", parse_html=True),
            color=colormap(row['success_score']),
            fill=True,
            fill_color=colormap(row['success_score']),
            fill_opacity=0.8
        ).add_to(m)

    # Plot known Yemeni coffee shops
    for _, row in known_shop_locations.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=row['name'],
            icon=folium.Icon(color='blue', icon='coffee', prefix='fa')
        ).add_to(m)

    # Add the legend
    colormap.add_to(m)

    # Save to an HTML file
    m.save(output_path)
    print(f"✅ Interactive map saved to: {output_path}")

    

create_yemeni_coffee_success_map(
    neighborhood_data=pd.read_csv("C:/Users/Owner/Desktop/code/cafe-compass/final_scored_data.csv"),
    known_shop_locations=pd.read_csv("C:/Users/Owner/Desktop/code/cafe-compass/yemeni_coffee_shops_se_mi.csv"),
    output_path="C:/Users/Owner/Desktop/code/cafe-compass/yemeni_coffee_success_map.html"
)

