import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests
import json
import pandas as pd
import random

# Function to sign in with email and password
def sign_in_with_email_and_password(email, password):
    api_key = "AIzaSyAWiX27N7dvOFT5S0DayXHK97Y6oeql06A"
    url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={api_key}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    return response.json()

# Function to sign up with email and password
def sign_up_with_email_and_password(email, password, username=""):
    api_key = "AIzaSyAWiX27N7dvOFT5S0DayXHK97Y6oeql06A"
    rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    if username:
        payload["displayName"] = username
    payload = json.dumps(payload)

    response = requests.post(rest_api_url, data=payload, headers={"Content-Type": "application/json"})
    response.raise_for_status()
    return response.json()

# Streamlit app setup
#st.set_page_config(page_title="Authentication", page_icon="🔑", layout="wide")

# Managing page navigation through URL query parameters
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["login"])[0]

def login_page():
    st.sidebar.page_link('Hello.py', label='Home')
    st.sidebar.page_link('pages/Login.py', label='Login')
    with st.empty():
        st.header(":red[Login]")
    login_email = st.text_input("Email", placeholder="example@gmail.com", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Log In"):

        # try:
        #     user_info = sign_in_with_email_and_password(login_email, login_password)
        #     st.success("Logged in successfully!")
        #     #st.experimental_set_query_params(page="input")
            switch_page("InputPage")
        # except requests.exceptions.HTTPError as e:
        #     error_message = e.response.json()
        #     st.error(f"Login failed: {error_message.get('error', {}).get('message', 'Unknown error')}")
        # except Exception as e:
        #     st.error(f"An error occurred: {e}")
    
    if st.button("Go to Register"):
        st.experimental_set_query_params(page="register")

def register_page():
    st.sidebar.page_link('Hello.py', label='Home')
    st.header(":red[Register]")
    first_name = st.text_input("First Name", key="first_name")
    last_name = st.text_input("Last Name", key="last_name")
    username = st.text_input("Username", key="register_username")
    register_email = st.text_input("Email", key="register_email")
    register_password = st.text_input("Password", type="password", key="register_password")

    if st.button("Register"):
        # try:
        #     user_info = sign_up_with_email_and_password(register_email, register_password, username)
            st.success(f"User {register_email} registered successfully!")
        #     st.experimental_set_query_params(page="login")
        # except requests.exceptions.HTTPError as e:
        #     error_message = e.response.json()
        #     st.error(f"Signup failed: {error_message.get('error', {}).get('message', 'Unknown error')}")
        # except Exception as e:
        #     st.error(f"An error occurred: {e}")
    
    if st.button("Back to Login"):
        st.experimental_set_query_params(page="login")

def input_page():
    # inputpage.py


    
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
            "Select Meal Time", ("Breakfast", "Lunch", "Dinner"), index=0, horizontal=True
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
            # Navigate to meal options page
            st.session_state["page"] = "meal_options"

    # Display meal options
    elif st.session_state["page"] == "meal_options":
        display_meal_options()

    # Display recommendations if generated
    elif st.session_state["page"] == "recommendation":
        if st.session_state["recommendations"]:
            st.subheader('Recommended Foods:')
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
            if st.button("Remove Recommendations"):
                st.session_state["generated"] = False
                st.session_state["recommendations"] = None
                st.session_state["page"] = "input"
        with col2:
            if st.button("Back to Meal Options"):
                st.session_state["page"] = "meal_options"


# Page navigation based on the query parameter
if page == "login":
    login_page()
elif page == "register":
    register_page()
elif page == "input":
    input_page()
else:
    st.title("Unknown Page")
    st.write("This page does not exist.")
