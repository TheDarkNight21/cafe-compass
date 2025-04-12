import folium
import pandas as pd
import branca
from folium.plugins import MarkerCluster
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import DBSCAN

def create_yemeni_coffee_success_map_with_predictions(
    neighborhood_data, 
    known_shop_locations, 
    model_predictions,  # New: Predicted success probabilities for new locations
    output_path="success_map_with_predictions.html"
):
    # Create color scale from red (low) to green (high)
    colormap = branca.colormap.LinearColormap(
        colors=['red', 'yellow', 'green'],
        vmin=model_predictions['predicted_success_prob'].min(),
        vmax=model_predictions['predicted_success_prob'].max()
    )
    colormap.caption = 'Predicted Success Probability'

    # Create the map centered in Southeast Michigan
    m = folium.Map(location=[42.3, -83.1], zoom_start=9)

    # Plot neighborhoods with success_score as color (existing data)
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

    # Plot known Yemeni coffee shops (existing data)
    for _, row in known_shop_locations.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=row['name'],
            icon=folium.Icon(color='blue', icon='coffee', prefix='fa')
        ).add_to(m)

    # Plot predicted success zones (new potential locations)
    for _, row in model_predictions.iterrows():
        success_prob = row['predicted_success_prob']
        success_color = colormap(success_prob)  # Use the color scale based on prediction

        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            popup=folium.Popup(f"Predicted Success Probability: {success_prob:.2f}<br>City: {row['City']}", parse_html=True),
            color=success_color,
            fill=True,
            fill_color=success_color,
            fill_opacity=0.6
        ).add_to(m)

    # Add the legend (color scale for predicted success probability)
    colormap.add_to(m)

    # Save the map to an HTML file
    m.save(output_path)
    print(f"✅ Interactive map with predictions saved to: {output_path}")

# Assuming you have the model's predictions stored in a dataframe with lat, lon, and predicted_success_prob columns
# Example: model_predictions = pd.DataFrame(...)

# Call the function with necessary data (Make sure to load the model predictions properly)
create_yemeni_coffee_success_map_with_predictions(
    neighborhood_data=pd.read_csv("C:/Users/Owner/Desktop/code/cafe-compass/csvFiles/final_scored_data.csv"),
    known_shop_locations=pd.read_csv("C:/Users/Owner/Desktop/code/cafe-compass/csvFiles/yemeniCoffeeShopsWithSuccess.csv"),
    model_predictions=pd.read_csv("C:/Users/Owner/Desktop/code/cafe-compass/csvFiles/final_scored_with_predictions.csv."),  # Assuming this file contains lat, lon, and predicted_success_prob
    output_path="C:/Users/Owner/Desktop/code/cafe-compass/yemeni_coffee_success_map_with_predictions.html"
)
