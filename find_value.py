import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
import yfinance as yf

# Configure logging to show only ERROR level messages
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variable
MONGODB_URI = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['asteroids']
asteroids_collection = db['asteroids']

# Define the market values and their corresponding tickers or custom values
market_values = {
    'gold': 'GC=F',
    'silver': 'SI=F',
    'copper': 'HG=F',
    'platinum': 'PL=F',
    'palladium': 'PA=F',
    'hydrogen': 10,  # Custom market value in $ per kg
    'helium': 15     # Custom market value in $ per kg
}

# Fetch the current market value for each commodity
commodity_values = {}
for commodity, ticker_or_value in market_values.items():
    if isinstance(ticker_or_value, str):
        ticker_data = yf.Ticker(ticker_or_value)
        history = ticker_data.history(period='7d')
        if not history.empty:
            commodity_values[commodity] = history['Close'].iloc[0] / 0.0283495  # Convert from $/oz to $/kg
        else:
            logging.error(f"{ticker_or_value}: possibly delisted; no price data found (period='7d')")
            commodity_values[commodity] = 0  # Set a default value or handle as needed
    else:
        # Use custom market values for elements without tickers
        commodity_values[commodity] = ticker_or_value

def assess_asteroid_value(asteroid: dict):
    """
    This function assesses the value of an asteroid based on its elements and their market values.
    It updates the asteroid's value in the MongoDB collection.

    Parameters:
    asteroid (dict): The asteroid document.

    Returns:
    int: The total value of the asteroid, or None if the asteroid is not found.
    """

    total_value = 0  # Initialize total_value
    for element in asteroid['elements']:
        element_name = element['name'].lower()
        mass_kg = element['mass_kg']
        # logging.info(f"{element_name}: {mass_kg} kg")
        if element_name in commodity_values:
            value = mass_kg * commodity_values[element_name]
            total_value += value

    # Ensure total_value does not exceed the maximum limit for 8-byte integers
    max_int_8_byte = 2**63 - 1
    if total_value > max_int_8_byte:
        total_value = max_int_8_byte

    total_value = round(total_value)  # Round the total value to the nearest whole number
    logging.info(f"Updating asteroid '{asteroid['full_name']}' with value: {total_value:,}")
    asteroids_collection.update_one({'_id': asteroid['_id']}, {'$set': {'value': total_value}})
    return total_value

def assess_element_values(elements: list, commodity_values: dict):
    """
    This function assesses the value of a list of elements based on their market values.

    Parameters:
    elements (list): The list of elements.
    commodity_values (dict): The dictionary containing the market values of the elements.

    Returns:
    float: The total value of the elements.
    """
    total_value = 0  # Initialize total_value
    for element in elements:
        element_name = element['name'].lower()
        mass_kg = element['mass_kg']
        if element_name in commodity_values:
            value = mass_kg * commodity_values[element_name]
            total_value += value

    total_value = round(total_value)  # Round the total value to the nearest whole number
    return total_value

def update_asteroids_without_value():
    """
    This function finds all asteroids in the MongoDB collection where the 'value' field does not exist,
    is 0, or is None. It assesses the value of each asteroid and updates the 'value' field.

    Returns:
    None
    """
    asteroids = asteroids_collection.find({'$or': [{'value': {'$exists': False}}, {'value': 0}, {'value': None}]})
    for asteroid in asteroids:
        value = assess_asteroid_value(asteroid)
        if value is not None:
            logging.info(f"Value of asteroid '{asteroid['full_name']}' updated successfully: {value:,}")
        else:
            logging.error(f"Asteroid '{asteroid['full_name']}' not found or market value not available.")

if __name__ == "__main__":
    # Test the assess_element_values function
    sample_elements = [
        {'name': 'gold', 'mass_kg': 10},
        {'name': 'silver', 'mass_kg': 20},
        {'name': 'hydrogen', 'mass_kg': 30},
        {'name': 'helium', 'mass_kg': 40}
    ]
    total_value = assess_element_values(sample_elements, commodity_values)
    print(f"Total value of sample elements: ${total_value:,}")

    # Update asteroids without value
    update_asteroids_without_value()