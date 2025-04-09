import streamlit as st
import pandas as pd
import numpy as np
import torch
import os
from auth import login, signup, is_authenticated, logout, get_current_user
from data_preprocessing import load_data, preprocess_data
from food_recommendation import generate_meal_plan
from model import FoodRecommendationModel

# Page configuration
st.set_page_config(
    page_title="Personalized Food Recommendation System",
    page_icon="🍎",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None

# Load data
@st.cache_data
def load_application_data():
    # Load all required datasets
    food_data = load_data('data/food_nutrients.csv')
    health_conditions = load_data('data/health_conditions.csv')
    exercises = load_data('data/exercises.csv')
    yoga_poses = load_data('data/yoga_poses.csv')
    
    return {
        'food_data': food_data,
        'health_conditions': health_conditions,
        'exercises': exercises,
        'yoga_poses': yoga_poses
    }

try:
    data = load_application_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Authentication section
def auth_section():
    st.sidebar.title("Authentication")
    
    auth_status = st.sidebar.radio("Select an option", ["Login", "Sign Up", "Logout" if st.session_state.authenticated else None])
    
    if auth_status == "Login":
        with st.sidebar.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                success, user = login(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_data = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
    
    elif auth_status == "Sign Up":
        with st.sidebar.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            submit_button = st.form_submit_button("Sign Up")
            
            if submit_button:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, user_or_error = signup(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_data = user_or_error
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error creating account: {user_or_error}")
    
    elif auth_status == "Logout":
        if logout():
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.session_state.meal_plan = None
            st.success("Logged out successfully!")
            st.rerun()

def main_app():
    st.title("🍎 Personalized Food Recommendation System")
    
    # Sidebar for inputs
    st.sidebar.title("Your Health Profile")
    
    # Health conditions selection
    health_conditions_list = data['health_conditions']['condition'].tolist()
    selected_conditions = st.sidebar.multiselect(
        "Select your health conditions (if any):",
        options=health_conditions_list
    )
    
    # Exercise selection
    exercise_list = data['exercises']['exercise_name'].tolist()
    selected_exercises = st.sidebar.multiselect(
        "Select your exercises:",
        options=exercise_list
    )
    
    # Yoga poses selection
    yoga_list = data['yoga_poses']['pose_name'].tolist()
    selected_yoga = st.sidebar.multiselect(
        "Select your yoga practices:",
        options=yoga_list
    )
    
    # Additional information
    age = st.sidebar.slider("Age", 18, 100, 30)
    gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
    weight = st.sidebar.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
    height = st.sidebar.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
    
    # Calculate BMI
    bmi = weight / ((height/100) ** 2)
    
    activity_levels = {
        "Sedentary (little or no exercise)": 1.2,
        "Lightly active (light exercise/sports 1-3 days/week)": 1.375,
        "Moderately active (moderate exercise/sports 3-5 days/week)": 1.55,
        "Very active (hard exercise/sports 6-7 days a week)": 1.725,
        "Super active (very hard exercise, physical job or training twice a day)": 1.9
    }
    
    activity_level = st.sidebar.selectbox("Activity Level", list(activity_levels.keys()))
    activity_factor = activity_levels[activity_level]
    
    # Calculate daily calorie needs using Harris-Benedict equation
    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    daily_calories = bmr * activity_factor
    
    # Display health information
    st.subheader("Your Health Information")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BMI", f"{bmi:.2f}", help="Body Mass Index")
        
        # Interpret BMI
        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
    
    with col2:
        st.metric("Daily Calorie Need", f"{daily_calories:.0f} kcal")
    
    with col3:
        st.metric("Activity Level", activity_level.split("(")[0])
    
    # Generate meal plan
    if st.button("Generate Meal Plan"):
        with st.spinner("Generating your personalized meal plan..."):
            # Prepare input data for model
            input_data = {
                'health_conditions': selected_conditions,
                'exercises': selected_exercises,
                'yoga_poses': selected_yoga,
                'age': age,
                'gender': gender,
                'weight': weight,
                'height': height,
                'bmi': bmi,
                'activity_level': activity_factor,
                'daily_calories': daily_calories
            }
            
            # Generate meal plan
            try:
                meal_plan = generate_meal_plan(input_data, data['food_data'])
                st.session_state.meal_plan = meal_plan
                st.success("Meal plan generated successfully!")
            except Exception as e:
                st.error(f"Error generating meal plan: {e}")
    
    # Display meal plan if available
    if st.session_state.meal_plan:
        st.header("Your Personalized Meal Plan")
        
        # Create tabs for each meal
        meals = ["Breakfast", "Lunch", "Dinner", "Snacks"]
        tabs = st.tabs(meals)
        
        for i, tab in enumerate(tabs):
            with tab:
                meal_type = meals[i].lower()
                if meal_type in st.session_state.meal_plan:
                    meal_items = st.session_state.meal_plan[meal_type]
                    
                    for item in meal_items:
                        st.subheader(item['name'])
                        
                        # Create columns for details
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Show nutritional information
                            st.caption("Nutritional Information (per serving)")
                            st.info(f"Calories: {item['calories']:.0f} kcal")
                            st.info(f"Protein: {item['protein']:.1f} g")
                            st.info(f"Carbs: {item['carbs']:.1f} g")
                            st.info(f"Fat: {item['fat']:.1f} g")
                        
                        with col2:
                            # Show benefits
                            st.caption("Health Benefits")
                            for benefit in item['benefits']:
                                st.write(f"• {benefit}")
                            
                            # Recommended portion
                            st.caption("Recommended Portion")
                            st.write(item['portion'])
                else:
                    st.write("No recommendations for this meal.")
        
        # Display total nutritional breakdown
        st.subheader("Daily Nutritional Summary")
        
        # Calculate total nutrition
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for meal_type in st.session_state.meal_plan:
            for item in st.session_state.meal_plan[meal_type]:
                total_calories += item['calories']
                total_protein += item['protein']
                total_carbs += item['carbs']
                total_fat += item['fat']
        
        # Display nutritional summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Calories", f"{total_calories:.0f} kcal", 
                      f"{((total_calories/daily_calories)*100)-100:.1f}%" if daily_calories > 0 else "N/A")
        
        with col2:
            st.metric("Total Protein", f"{total_protein:.1f} g", 
                      f"{(total_protein*4/total_calories*100):.1f}% of calories" if total_calories > 0 else "N/A")
        
        with col3:
            st.metric("Total Carbs", f"{total_carbs:.1f} g", 
                      f"{(total_carbs*4/total_calories*100):.1f}% of calories" if total_calories > 0 else "N/A")
        
        with col4:
            st.metric("Total Fat", f"{total_fat:.1f} g", 
                      f"{(total_fat*9/total_calories*100):.1f}% of calories" if total_calories > 0 else "N/A")
        
        # Display recommendations based on health conditions
        if selected_conditions:
            st.subheader("Dietary Recommendations Based on Your Health Conditions")
            for condition in selected_conditions:
                condition_info = data['health_conditions'][data['health_conditions']['condition'] == condition]
                if not condition_info.empty:
                    st.write(f"**{condition}**")
                    st.write(condition_info.iloc[0]['dietary_recommendation'])
                    
                    # Foods to avoid
                    if 'foods_to_avoid' in condition_info.columns and not pd.isna(condition_info.iloc[0]['foods_to_avoid']):
                        st.warning(f"Foods to avoid: {condition_info.iloc[0]['foods_to_avoid']}")

# Main application flow
def main():
    # Display authentication section in the sidebar
    auth_section()
    
    # If user is authenticated, show the main app
    if st.session_state.authenticated:
        main_app()
    else:
        # Show welcome message for non-authenticated users
        st.title("🍎 Personalized Food Recommendation System")
        st.write("""
        Welcome to our Food Recommendation System! This application helps you create personalized meal plans based on your health conditions, exercise routines, and yoga practices.
        
        ### Features:
        - Personalized food recommendations
        - Meal planning based on health conditions
        - Nutritional information and health benefits
        - Support for various dietary needs
        
        Please log in or sign up to get started!
        """)
        
        # Add some information about the benefits
        st.subheader("Why Use Our System?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("### 🥗 Personalized")
            st.write("Get meal recommendations tailored to your specific health needs and activity level.")
        
        with col2:
            st.write("### 💪 Health-Focused")
            st.write("Recommendations based on scientific nutritional principles for various health conditions.")
        
        with col3:
            st.write("### 📊 Comprehensive")
            st.write("Complete nutritional breakdown and health benefits for each recommendation.")

if __name__ == "__main__":
    main()
