import streamlit as st
from chatbot import get_travel_plan, get_options_from_dataset, tourism_df

def main():
    st.markdown(
        '''
        
<style>
body {
    font-family: 'Helvetica', sans-serif;
    background-color: #f4f4f9;
    color: #333;
}
h1 {
    color: #5a5a8f;
}
.stButton > button {
    background-color: #5a5a8f;
    color: white;
    border-radius: 5px;
    padding: 10px 24px;
}
.stTextInput, .stSelectbox, .stMultiselect, .stSlider {
    border-radius: 5px;
}
.stTextInput > div > div > input, .stSelectbox > div > div > select, .stMultiselect > div > div > select, .stSlider > div > div > input[type="range"] {
    border: 1px solid #5a5a8f;
}
</style>

        ''',
        unsafe_allow_html=True
    )

    st.title('Travel Buddy: Your Personalized London Tour Guide 🇬🇧')
    st.header("Let's plan your trip to London!")

    place_types = get_options_from_dataset('tourism')
    cuisines = get_options_from_dataset('restaurants')
    accommodation_types = get_options_from_dataset('accommodations')

    with st.form(key='my_form'):
        place_preference = st.multiselect('Places to visit', place_types, help='Select the types of places you would like to visit')
        cuisine_preference = st.multiselect('Cuisine preference', cuisines, help='Choose your preferred types of cuisine')
        accommodation_preference = st.selectbox('Accommodation type', accommodation_types, help='Select your preferred type of accommodation')
        diet_preference = st.radio('Vegetarian options?', ['Yes', 'No'], help='Specify if you need vegetarian options')
        stay_duration = st.number_input('Duration of Stay (days)', min_value=1, max_value=30, value=3, help='Enter the number of days you plan to stay')
        budget_preference = st.slider('Budget range per night', 0, 1000, (50, 300), help='Adjust your budget range per night')
        submit_button = st.form_submit_button('Plan My Trip')

        if submit_button:
            with st.spinner('Generating your travel plan...'):
                travel_plan = get_travel_plan(place_preference, cuisine_preference, accommodation_preference, diet_preference, budget_preference, stay_duration)
                st.success('Travel plan generated successfully!')
                st.write(travel_plan)

    with st.sidebar:
        st.header('Travel Tips')
        st.markdown('* Make sure to check the weather forecast.')
        st.markdown("* Don't forget to try traditional British dishes!")
        st.markdown('* Keep local emergency numbers handy.')

if __name__ == '__main__':
    main()

# Importing necessary functions from updated chatbot.py
from chatbot import recommend_transportation, recommend_destinations

# Adding a section in the Streamlit app for the budget-based transportation recommendation
st.header("Transportation Recommendation Based on Your Budget")
budget = st.number_input("Enter your budget for transportation:", min_value=0.0, format="%.2f")
if st.button("Recommend Transportation"):
    transportation = recommend_transportation(budget)
    st.write("Recommended Mode of Transportation:", transportation)

# Adding a section for recommending multiple destinations based on user preferences
st.header("Explore Multiple Destinations Based on Your Preferences")
destination_types = st.multiselect("Select the types of places you are interested in:", tourism_df['Type'].unique().tolist())
number_of_destinations = st.slider("Select how many destinations you want to explore:", 1, 5, 2)
if st.button("Recommend Destinations"):
    if destination_types:
        destinations = recommend_destinations(destination_types, number_of_destinations)
        for destination in destinations:
            st.write(f"Name: {destination[0]}, Type: {destination[1]}, Location: {destination[2]}")
    else:
        st.write("Please select at least one type of destination.")
