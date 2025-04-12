# Cafe Compass - Predicting Yemeni Coffee Shop Success

**Cafe Compass** is a data-driven project designed to predict the success of Yemeni coffee shops using machine learning. By analyzing geographic and demographic data, the project identifies neighborhoods with the highest potential for new coffee shop openings. This tool helps entrepreneurs and investors find optimal locations for Yemeni coffee shops based on a range of features, such as population density, nearby amenities, and socio-economic factors.

## Project Overview

This project uses data from various sources, including demographic information, geographic features, and data from known Yemeni coffee shops, to build a predictive model. The model uses machine learning techniques (Random Forest) to predict the success of new coffee shop locations in different neighborhoods.

### Features of the Project:
1. **Geographic and Demographic Data**: Geographic and demographic features are collected to evaluate neighborhood suitability, such as population density, median household income, and proximity to amenities.
2. **Reverse Geocoding**: The project uses the **Geopy** library to perform reverse geocoding and convert latitude and longitude coordinates into human-readable addresses (city, county).
3. **Machine Learning Model**: A Random Forest classifier is trained to predict the success of a Yemeni coffee shop based on features such as pedestrian score, nearby restaurants, and mosque density.
4. **Custom Features**: Several custom features like restaurant-to-coffee ratio, coffee shop density, and affordability index are created to better evaluate potential success.
5. **Data Cleaning and Normalization**: The dataset is cleaned, normalized, and transformed to ensure consistency and prepare it for the machine learning model.

## Project Structure

Here’s a breakdown of the project files:

- `cafe_compass/`
  - `csvFiles/`
    - `completeCafeCompassData.csv`: Raw input data with geographic, demographic, and restaurant/coffee shop features.
    - `cleaned_normalized_data.csv`: Cleaned and normalized version of the dataset ready for analysis.
    - `yemeniCoffeeShopsWithSuccess.csv`: Known Yemeni coffee shop data with success labels.
    - `final_scored_with_predictions.csv`: Final dataset with predicted success probabilities for each neighborhood.
  - `scripts/`
    - `data_preprocessing.py`: Script to clean, normalize, and prepare the data for analysis.
    - `model_training.py`: Script to train the Random Forest model and make predictions.
    - `geocoding.py`: Script for reverse geocoding latitudes and longitudes into cities and counties.
  - `README.md`: Project description and instructions.

## Setup and Installation

### Prerequisites

To run this project, you need Python 3.x and the following libraries:

- pandas
- scikit-learn
- geopy
- matplotlib
- numpy

### Installation Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/cafe-compass.git
    cd cafe-compass
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Ensure you have the necessary data files in the `csvFiles/` directory:
    - `completeCafeCompassData.csv`
    - `yemeniCoffeeShopsWithSuccess.csv`

### Running the Project

To run the project, follow these steps:

1. Clean and preprocess the data:

    ```bash
    python scripts/data_preprocessing.py
    ```

2. Train the model and predict success probabilities:

    ```bash
    python scripts/model_training.py
    ```

3. View the results:

    The final results will be saved in `final_scored_with_predictions.csv`. This file contains the neighborhoods with predicted success probabilities for opening a Yemeni coffee shop.

## How It Works

1. **Data Cleaning**: Raw data is cleaned, missing values are handled, and categorical features (like city and county names) are standardized.
2. **Feature Engineering**: Custom features such as restaurant-to-coffee ratio, coffee shop density, and potential demand index are created to enhance the model's predictive power.
3. **Reverse Geocoding**: Latitude and longitude values are converted to city and county names, which are standardized for use in the model.
4. **Model Training**: A Random Forest classifier is used to train a predictive model based on historical success data from Yemeni coffee shops. The model predicts the success probability for new coffee shop locations.
5. **Predictions**: After training, the model assigns a success probability to each neighborhood, helping identify the best locations for opening a Yemeni coffee shop.

## Results

The final output includes a CSV file with each neighborhood's predicted success probability. This can be used to evaluate potential areas for opening a new Yemeni coffee shop, based on factors such as local demographics, amenities, and the presence of similar businesses.

## Contributing

If you would like to contribute to this project, feel free to fork the repository and submit a pull request. Any improvements, bug fixes, or additional features are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **Geopy**: For reverse geocoding.
- **Scikit-learn**: For the machine learning model.
- **Pandas and Numpy**: For data manipulation and analysis.

---

### Notes:

- Replace `your-username` with your actual GitHub username in the `git clone` command.
- Add the appropriate details in the **Acknowledgements** section if you're using any external resources, libraries, or datasets.
- Feel free to customize the `README.md` file to reflect any additional details that may be relevant to your project.

Let me know if you'd like to modify any part of this!
