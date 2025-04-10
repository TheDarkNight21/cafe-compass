from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt

def get_city_coffee_interest(city_name: str, show_plot: bool = False):
    # Connect to Google Trends
    pytrends = TrendReq(hl='en-US', tz=360)

    # Build coffee-related intent keywords
    kw_list = [
        f"yemeni coffee {city_name}",
        f"study cafe {city_name}",
        f"chill cafe {city_name}",
        f"coffee shop {city_name}",
        f"best cafe {city_name}"
    ]

    # Build and send the payload
    pytrends.build_payload(
        kw_list,
        geo='US',  # Nationwide search scope
        timeframe='2018-01-01 2023-12-31'
    )

    # Get interest over time
    data = pytrends.interest_over_time()
    if 'isPartial' in data.columns:
        data = data.drop(columns=['isPartial'])

    # Calculate average interest per keyword
    averages = data.mean().round(2).to_dict()

    # Optionally show a trend plot
    if show_plot:
        plt.figure(figsize=(14, 6))
        for keyword in data.columns:
            plt.plot(data.index, data[keyword], label=keyword)
        plt.title(f'Coffee & Cafe Search Trends (2018–2023) – {city_name}')
        plt.xlabel('Date')
        plt.ylabel('Interest (0–100)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return averages

#print(get_city_coffee_interest("Detroit", show_plot=False))
print(get_city_coffee_interest("West Dearborn", show_plot=False))