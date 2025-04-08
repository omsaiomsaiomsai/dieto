import streamlit as st
import pandas as pd
import random
from streamlit_navigation_bar import st_navbar
from streamlit import session_state as ss


st.sidebar.page_link('Hello.py', label='Home')
#st.set_page_config(page_title="Custom Food Recommendation", page_icon="🔍", layout="wide")

# List of foods with their nutritional values
foods = [
    {'Name': 'Bitter Gourd (Karela)', 'Calories': 17, 'FatContent': 0.2, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 13, 'CarbohydrateContent': 3.7, 'FiberContent': 2.8, 'SugarContent': 0, 'ProteinContent': 1},
    {'Name': 'Fenugreek Leaves (Methi)', 'Calories': 49, 'FatContent': 0.9, 'SaturatedFatContent': 0.2, 'CholesterolContent': 0, 'SodiumContent': 7, 'CarbohydrateContent': 6.8, 'FiberContent': 2.7, 'SugarContent': 0, 'ProteinContent': 4},
    {'Name': 'Indian Gooseberry (Amla)', 'Calories': 44, 'FatContent': 0.6, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 1, 'CarbohydrateContent': 10, 'FiberContent': 4.3, 'SugarContent': 0, 'ProteinContent': 1},
    {'Name': 'Green Gram (Moong Dal)', 'Calories': 347, 'FatContent': 1.2, 'SaturatedFatContent': 0.3, 'CholesterolContent': 0, 'SodiumContent': 15, 'CarbohydrateContent': 63, 'FiberContent': 16, 'SugarContent': 7, 'ProteinContent': 24},
    {'Name': 'Round Gourd (Tinda)', 'Calories': 21, 'FatContent': 0.2, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 3, 'CarbohydrateContent': 4.1, 'FiberContent': 1.2, 'SugarContent': 2.1, 'ProteinContent': 0.8},
    {'Name': 'Spinach (Palak)', 'Calories': 23, 'FatContent': 0.4, 'SaturatedFatContent': 0.1, 'CholesterolContent': 0, 'SodiumContent': 79, 'CarbohydrateContent': 3.6, 'FiberContent': 2.2, 'SugarContent': 0.4, 'ProteinContent': 2.9},
    {'Name': 'Bottle Gourd (Lauki)', 'Calories': 15, 'FatContent': 0.1, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 2, 'CarbohydrateContent': 3.4, 'FiberContent': 1.2, 'SugarContent': 2.2, 'ProteinContent': 0.6},
    {'Name': 'Drumstick (Moringa)', 'Calories': 64, 'FatContent': 1.4, 'SaturatedFatContent': 0.3, 'CholesterolContent': 0, 'SodiumContent': 9, 'CarbohydrateContent': 11.2, 'FiberContent': 2.1, 'SugarContent': 0, 'ProteinContent': 9.4},
    {'Name': 'Cabbage', 'Calories': 25, 'FatContent': 0.1, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 18, 'CarbohydrateContent': 5.8, 'FiberContent': 2.5, 'SugarContent': 3.2, 'ProteinContent': 1.3},
    {'Name': 'Cauliflower', 'Calories': 25, 'FatContent': 0.3, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 30, 'CarbohydrateContent': 5, 'FiberContent': 2, 'SugarContent': 2, 'ProteinContent': 2},
    {'Name': 'Tomato', 'Calories': 18, 'FatContent': 0.2, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 5, 'CarbohydrateContent': 3.9, 'FiberContent': 1.2, 'SugarContent': 2.6, 'ProteinContent': 0.9},
    {'Name': 'Cucumber', 'Calories': 16, 'FatContent': 0.1, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 2, 'CarbohydrateContent': 3.6, 'FiberContent': 0.5, 'SugarContent': 1.7, 'ProteinContent': 0.7},
    {'Name': 'Radish', 'Calories': 16, 'FatContent': 0.1, 'SaturatedFatContent': 0, 'CholesterolContent': 0, 'SodiumContent': 39, 'CarbohydrateContent': 3.4, 'FiberContent': 1.6, 'SugarContent': 1.9, 'ProteinContent': 0.7},
    {'Name': 'Bengal Gram (Chana Dal)', 'Calories': 360, 'FatContent': 5.3, 'SaturatedFatContent': 0.5, 'CholesterolContent': 0, 'SodiumContent': 24, 'CarbohydrateContent': 60, 'FiberContent': 18, 'SugarContent': 10, 'ProteinContent': 19},
    {'Name': 'Black Gram (Urad Dal)', 'Calories': 341, 'FatContent': 1.6, 'SaturatedFatContent': 0.5, 'CholesterolContent': 0, 'SodiumContent': 38, 'CarbohydrateContent': 58.99, 'FiberContent': 18.3, 'SugarContent': 1.1, 'ProteinContent': 25.21}
]


# Function to get random food data
def get_random_food_data():
    return random.sample(foods, min(5, len(foods)))

# Function to display meal options
def display_meal_options():
    st.header(":green[Choose Your Meal]")
    meal_choice = st.radio(
        "Select Meal Time",
        ("Breakfast", "Lunch", "Dinner"),
        index=0,
        horizontal=True
    )
    if meal_choice:
        st.success(f"You selected: {meal_choice}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Input Page"):
            st.session_state["page"] = "input"
    with col2:
        if st.button("Suggest Food"):
            st.session_state["selected_meal"] = meal_choice
            st.session_state["recommendations"] = get_random_food_data()
            st.session_state["page"] = "recommendation"

# Function to display workout options
def display_workout_options():
    st.header(":green[Recommended Workout]")
    
    st.markdown(
        """
        <div style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 10px; margin-bottom: 10px;">
            <h3 style="color: blue;">Cardio Exercises</h3>
            <ul>
                <li><b>Running:</b> 30 minutes<br>Benefits: Improves cardiovascular health, burns calories.</li>
                <li><b>Cycling:</b> 30 minutes<br>Benefits: Strengthens legs, enhances stamina.</li>
                <li><b>Jump Rope:</b> 15 minutes<br>Benefits: Improves coordination, burns calories quickly.</li>
            </ul>
        </div>
        <div style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 10px; margin-bottom: 10px;">
            <h3 style="color: blue;">Strength Training</h3>
            <ul>
                <li><b>Push-ups:</b> 3 sets of 15 reps<br>Benefits: Strengthens chest, shoulders, and arms.</li>
                <li><b>Squats:</b> 3 sets of 20 reps<br>Benefits: Builds leg muscles, improves core strength.</li>
                <li><b>Planks:</b> 3 sets of 1 minute<br>Benefits: Enhances core stability, improves posture.</li>
            </ul>
        </div>
       
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Input Page"):
            st.session_state["page"] = "input"
    with col2:
        if st.button("Back to Options"):
            st.session_state["page"] = "options"

# Function to display meditation options
def display_meditation_options():
    st.header(":green[Recommended Meditation Practices]")
    
    st.markdown(
        """
        <div style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 10px; margin-bottom: 10px;">
            <h3 style="color: blue;">Guided Meditation</h3>
            <ul>
                <li><b>Mindfulness Meditation:</b> 10 minutes<br>Benefits: Reduces stress, enhances focus.</li>
                <li><b>Body Scan Meditation:</b> 15 minutes<br>Benefits: Promotes relaxation, enhances body awareness.</li>
            </ul>
        </div>
        <div style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 10px; margin-bottom: 10px;">
            <h3 style="color: blue;">Breathing Exercises</h3>
            <ul>
                <li><b>Deep Breathing:</b> 5 minutes<br>Benefits: Calms the mind, reduces anxiety.</li>
                <li><b>Box Breathing:</b> 5 minutes<br>Benefits: Balances the nervous system, increases mindfulness.</li>
            </ul>
        </div>
        <div style="box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); padding: 10px;">
            <h3 style="color: blue;">Visualizations</h3>
            <ul>
                <li><b>Positive Imagery:</b> 10 minutes<br>Benefits: Enhances mood, reduces stress.</li>
                <li><b>Gratitude Visualization:</b> 10 minutes<br>Benefits: Promotes positive thinking, improves well-being.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Input Page"):
            st.session_state["page"] = "input"
    with col2:
        if st.button("Back to Options"):
            st.session_state["page"] = "options"

# Main Application
if "page" not in st.session_state:
    st.session_state["page"] = "input"

if st.session_state["page"] == "input":
    st.header(":red[Input Page]")
    col1, col2 = st.columns(2)
    age = col1.number_input("Age", step=1)
    weight = col1.number_input("Weight", step=1)
    eating_preference = col1.selectbox("Eating Preference", ["Veg", "Non-Veg"])
    region = col1.text_input("Region")
    gender = col2.selectbox("Gender", ["MALE", "FEMALE", "OTHERS"])
    height = col2.number_input("Height (in m)")
    generic_disease = col2.text_input("Generic Disease")
    allergies = col2.text_input("Allergies")
    food_type = st.text_input("Food Type")
    next_clicked = st.button("Next")
    if next_clicked:
        # Store inputs in session state
        st.session_state["age"] = age
        st.session_state["weight"] = weight
        st.session_state["eating_preference"] = eating_preference
        st.session_state["region"] = region
        st.session_state["gender"] = gender
        st.session_state["height"] = height
        st.session_state["generic_disease"] = generic_disease
        st.session_state["allergies"] = allergies
        st.session_state["food_type"] = food_type
        # Navigate to options page
        st.session_state["page"] = "options"

elif st.session_state["page"] == "options":
    st.header(":blue[Choose an Option]")
    option_choice = st.radio(
        "Select Option",
        ("Meal", "Workout", "Meditation"),
        index=0,
        horizontal=True
    )
    if option_choice:
        st.success(f"You selected: {option_choice}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Recommendation"):
            if option_choice == "Meal":
                st.session_state["page"] = "meal_options"
            elif option_choice == "Workout":
                st.session_state["page"] = "workout_options"
            elif option_choice == "Meditation":
                st.session_state["page"] = "meditation_options"
    with col2:
        if st.button("Back to Input Page"):
            st.session_state["page"] = "input"

elif st.session_state["page"] == "meal_options":
    display_meal_options()

elif st.session_state["page"] == "workout_options":
    display_workout_options()

elif st.session_state["page"] == "meditation_options":
    display_meditation_options()

elif st.session_state["page"] == "recommendation":
    if st.session_state["recommendations"]:
        # Check if recommendations are not None
        st.header(":green[Recommended Foods:]")
        for food in st.session_state["recommendations"]:
            with st.expander(f"**{food['Name']}**"):
                st.write(f"Calories: {food['Calories']}")
                st.write(f"Fat: {food['FatContent']}g")
                st.write(f"Saturated Fat: {food['SaturatedFatContent']}g")
                st.write(f"Cholesterol: {food['CholesterolContent']}mg")
                st.write(f"Sodium: {food['SodiumContent']}mg")
                st.write(f"Carbohydrates: {food['CarbohydrateContent']}g")
                st.write(f"Fiber: {food['FiberContent']}g")
                st.write(f"Sugars: {food['SugarContent']}g")
                st.write(f"Protein: {food['ProteinContent']}g")
    else:
        st.error("No recommendations available.")
    col1, col2 = st.columns(2)
    with col1:
        # Add a button to remove recommendations
        if st.button("Remove Recommendations"):
            st.session_state["generated"] = False
            st.session_state["recommendations"] = None
            st.session_state["page"] = "input"
    with col2:
        if st.button("Back to Meal Options"):
            st.session_state["page"] = "meal_options"
