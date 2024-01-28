import pandas as pd
import random
# Load the datasets
accommodations_df = pd.read_excel('acco.xlsx')
restaurants_df = pd.read_excel('London_Restaurants_Dataset.xlsx')
tourism_df = pd.read_excel('London_Tourism_Dataset.xlsx')

def get_options_from_dataset(dataset_name):
    if dataset_name == 'tourism':
        return tourism_df['Type'].unique().tolist()
    elif dataset_name == 'restaurants':
        return restaurants_df['Cuisine'].unique().tolist()
    elif dataset_name == 'accommodations':
        return accommodations_df['Type'].unique().tolist()

def parse_price_range(price_range):
    if '-' in price_range:
        low, high = price_range.replace('£', '').split(' - ')
        return int(low), int(high)
    else:
        value = int(price_range.replace('£', ''))
        return value, value

def filter_based_on_budget(df, budget_range, price_column):
    budget_low, budget_high = budget_range
    def budget_filter(x):
        low, high = parse_price_range(x)
        return low <= budget_high and high >= budget_low
    return df[df[price_column].apply(budget_filter)]

def format_itinerary_item(item_type, item_data, emoji):
    if item_data is None:
        return f"No {item_type} found that matches your preferences. {emoji}\n"
    
    name = item_data.get('Name', 'Unknown')
    details = '\n'.join(f"{key}: {value}" for key, value in item_data.items() if key != 'Name')
    return f"{emoji} {item_type} - {name}:\n{details}\n\n"

def get_unique_suggestions(df, previous_choices, category_name):
    return df[~df[category_name].isin(previous_choices)]

def calculate_daily_budget(attraction, restaurant, accommodation_price):
    attraction_fee = 0 if attraction['Entrance Fee'] == 'Free' else int(attraction['Entrance Fee'].replace('£', ''))
    restaurant_cost = restaurant['Price Range'].count('£') * 10  # Assuming average meal cost based on price range symbol count
    total_daily_cost = attraction_fee + restaurant_cost + accommodation_price
    return total_daily_cost

def get_travel_plan(place_preferences, cuisine_preferences, accommodation_preference, diet_preference, budget_preference, stay_duration):
    # Ensure that place_preferences and cuisine_preferences are list-like
    place_preferences = [place_preferences] if isinstance(place_preferences, str) else place_preferences
    cuisine_preferences = [cuisine_preferences] if isinstance(cuisine_preferences, str) else cuisine_preferences

    # Filter accommodations based on preference and budget
    filtered_accommodations = filter_based_on_budget(accommodations_df[accommodations_df['Type'].isin([accommodation_preference])], budget_preference, 'Price Range per Night')
    if filtered_accommodations.empty:
        return "Sorry, we couldn't find any accommodations that match your preferences. Please try adjusting your preferences."
    
    accommodation_choice = filtered_accommodations.sample().iloc[0].to_dict()
    accommodation_price_per_night = sum(parse_price_range(accommodation_choice['Price Range per Night'])) / 2
    
    # Apply filtering based on the user's list of place and cuisine preferences
    filtered_attractions = tourism_df[tourism_df['Type'].isin(place_preferences)]
    filtered_restaurants = restaurants_df[restaurants_df['Cuisine'].isin(cuisine_preferences)]
    
    if diet_preference == 'Yes':
        filtered_restaurants = filtered_restaurants[filtered_restaurants['Vegetarian-Friendly'] == 'Yes']

    chosen_attractions = []
    chosen_restaurants = []

    itinerary_str = "📅 Here's your exciting travel itinerary! 🌍✈️🎒\n\n"
    total_budget = 0

    for day in range(1, stay_duration + 1):
        unique_attractions = get_unique_suggestions(filtered_attractions, chosen_attractions, 'Name')
        unique_restaurants = get_unique_suggestions(filtered_restaurants, chosen_restaurants, 'Name')

        if unique_attractions.empty or unique_restaurants.empty:
            return f"Sorry, we couldn't find enough options to fill your itinerary for {stay_duration} days. Please try adjusting your preferences."

        attraction_choice = unique_attractions.sample().iloc[0].to_dict()
        restaurant_choice = unique_restaurants.sample().iloc[0].to_dict()

        chosen_attractions.append(attraction_choice['Name'])
        chosen_restaurants.append(restaurant_choice['Name'])

        daily_budget = calculate_daily_budget(attraction_choice, restaurant_choice, accommodation_price_per_night)
        total_budget += daily_budget

        itinerary_str += f"Day {day}:\n"
        itinerary_str += format_itinerary_item('Attraction', attraction_choice, '🏛️')
        itinerary_str += format_itinerary_item('Restaurant', restaurant_choice, '🍴')
        if day == 1:  # Add accommodation details only on the first day
            itinerary_str += format_itinerary_item('Accommodation', accommodation_choice, '🛌')
        itinerary_str += f"Estimated budget for the day: £{daily_budget}\n\n"

    itinerary_str += f"💷 Total estimated budget for your trip: £{total_budget}\n"
    itinerary_str += "We hope you have a fantastic journey! Bon Voyage! 🚢"

    return itinerary_str
    
# Rest of the chatbot.py code can go here if any

def recommend_transportation(budget):
    if budget <= 0:
        return "Sorry, you might need to increase your budget to travel."
    elif budget <= 50:
        return "With this budget, consider walking or cycling."
    elif budget <= 100:
        return "Your budget fits well for public transport like buses or trains."
    else:
        return "You can comfortably use a car or a taxi within this budget."

def recommend_destinations(preferred_types, number_of_destinations=2):
    filtered_df = tourism_df[tourism_df['Type'].isin(preferred_types)]
    if number_of_destinations > len(filtered_df):
        number_of_destinations = len(filtered_df)
    recommended_destinations = random.sample(filtered_df.to_dict('records'), number_of_destinations)
    return [(destination['Name'], destination['Type'], destination['Location'], destination['Description']) for destination in recommended_destinations]
