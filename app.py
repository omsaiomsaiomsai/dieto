import streamlit as st
import pandas as pd
import numpy as np
import torch
import os
import random
from auth import login, signup, is_authenticated, logout, get_current_user
from data_preprocessing import load_data, preprocess_data
from food_recommendation import generate_meal_plan
from model import FoodRecommendationModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration with theme options
st.set_page_config(
    page_title="Personalized Food Recommendation System",
    page_icon="🍎",
    layout="wide"
)

# Functions to recommend exercises and yoga poses
def recommend_exercises(health_conditions, age, gender, bmi, activity_level):
    """
    Recommend exercises based on user's health profile
    
    Args:
        health_conditions (list): List of user's health conditions
        age (int): User's age
        gender (str): User's gender
        bmi (float): User's BMI
        activity_level (float): User's activity level factor
        
    Returns:
        list: List of recommended exercises
    """
    # Load exercise data using OS-agnostic path
    exercises_df = load_data(os.path.join('data', 'exercises.csv'))
    exercise_list = exercises_df['exercise_name'].tolist()
    
    # Determine intensity based on health conditions, age, and BMI
    intensity = "moderate"
    
    if age > 65:
        intensity = "low"
    elif age < 30 and bmi < 25 and activity_level > 1.5:
        intensity = "high"
    
    # Check for health conditions that may require low-intensity exercises
    low_intensity_conditions = [
        "Heart Disease", "Hypertension", "Asthma", "Arthritis", 
        "Osteoporosis", "Recent Surgery", "Chronic Pain"
    ]
    
    if any(condition in health_conditions for condition in low_intensity_conditions):
        intensity = "low"
    
    # Filter exercises by intensity (if we had intensity column)
    recommended_exercises = []
    
    # For demo purposes, we'll just recommend a subset of exercises
    # In a real app, we would filter by intensity and target areas based on health conditions
    if intensity == "low":
        low_intensity_options = [
            "Walking", "Swimming", "Yoga", "Tai Chi", "Gentle Stretching", 
            "Water Aerobics", "Stationary Cycling", "Chair Exercises"
        ]
        # Keep only the exercises that are in our dataset
        valid_options = [ex for ex in low_intensity_options if ex in exercise_list]
        recommended_exercises = valid_options[:min(4, len(valid_options))]
    
    elif intensity == "moderate":
        moderate_intensity_options = [
            "Brisk Walking", "Cycling", "Swimming", "Dancing", "Hiking", 
            "Tennis", "Resistance Training", "Yoga", "Pilates"
        ]
        valid_options = [ex for ex in moderate_intensity_options if ex in exercise_list]
        recommended_exercises = valid_options[:min(4, len(valid_options))]
    
    else:  # high intensity
        high_intensity_options = [
            "Running", "HIIT", "CrossFit", "Weightlifting", "Basketball", 
            "Soccer", "Spinning", "Kickboxing", "Mountain Biking"
        ]
        valid_options = [ex for ex in high_intensity_options if ex in exercise_list]
        recommended_exercises = valid_options[:min(4, len(valid_options))]
    
    # If we couldn't find enough exercises in our categories, add some random ones
    if len(recommended_exercises) < 3:
        remaining_count = 3 - len(recommended_exercises)
        remaining_exercises = [e for e in exercise_list if e not in recommended_exercises]
        if remaining_exercises:
            recommended_exercises.extend(random.sample(remaining_exercises, min(remaining_count, len(remaining_exercises))))
    
    return recommended_exercises

def recommend_yoga_poses(health_conditions, age, bmi):
    """
    Recommend yoga poses based on user's health profile
    
    Args:
        health_conditions (list): List of user's health conditions
        age (int): User's age
        bmi (float): User's BMI
        
    Returns:
        list: List of recommended yoga poses
    """
    # Load yoga poses data using OS-agnostic path
    yoga_df = load_data(os.path.join('data', 'yoga_poses.csv'))
    yoga_list = yoga_df['pose_name'].tolist()
    
    # Determine difficulty based on age and BMI
    difficulty = "intermediate"
    
    if age > 60 or bmi > 30:
        difficulty = "beginner"
    elif age < 30 and bmi < 25:
        difficulty = "advanced"
    
    # Check for health conditions that may require gentle yoga
    gentle_yoga_conditions = [
        "Heart Disease", "Hypertension", "Arthritis", "Back Pain", 
        "Osteoporosis", "Recent Surgery", "Chronic Pain"
    ]
    
    if any(condition in health_conditions for condition in gentle_yoga_conditions):
        difficulty = "beginner"
    
    # Filter yoga poses by difficulty (if we had difficulty column)
    recommended_poses = []
    
    # For demo purposes, we'll just recommend a subset of poses
    # In a real app, we would filter by difficulty and benefits related to health conditions
    if difficulty == "beginner":
        beginner_poses = [
            "Mountain Pose", "Child's Pose", "Cat-Cow Stretch", "Corpse Pose",
            "Easy Pose", "Bridge Pose", "Tree Pose", "Legs Up The Wall"
        ]
        valid_options = [pose for pose in beginner_poses if pose in yoga_list]
        recommended_poses = valid_options[:min(3, len(valid_options))]
    
    elif difficulty == "intermediate":
        intermediate_poses = [
            "Downward-Facing Dog", "Warrior I", "Warrior II", "Triangle Pose",
            "Plank Pose", "Cobra Pose", "Half Moon Pose", "Eagle Pose"
        ]
        valid_options = [pose for pose in intermediate_poses if pose in yoga_list]
        recommended_poses = valid_options[:min(3, len(valid_options))]
    
    else:  # advanced
        advanced_poses = [
            "Headstand", "Handstand", "Crow Pose", "Side Plank", "King Pigeon Pose",
            "Wheel Pose", "Firefly Pose", "Lotus Pose"
        ]
        valid_options = [pose for pose in advanced_poses if pose in yoga_list]
        recommended_poses = valid_options[:min(3, len(valid_options))]
    
    # If we couldn't find enough poses in our categories, add some random ones
    if len(recommended_poses) < 3:
        remaining_count = 3 - len(recommended_poses)
        remaining_poses = [p for p in yoga_list if p not in recommended_poses]
        if remaining_poses:
            recommended_poses.extend(random.sample(remaining_poses, min(remaining_count, len(remaining_poses))))
    
    return recommended_poses



# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"

# Load data
@st.cache_data
def load_application_data():
    # Load all required datasets using OS-agnostic paths
    food_data = load_data(os.path.join('data', 'food_nutrients.csv'))
    health_conditions = load_data(os.path.join('data', 'health_conditions.csv'))
    exercises = load_data(os.path.join('data', 'exercises.csv'))
    yoga_poses = load_data(os.path.join('data', 'yoga_poses.csv'))
    
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

# Navigation bar
def render_navigation():
    with st.sidebar:
        st.image(os.path.join(os.path.dirname(__file__), "generated-icon.png"), width=100)
        st.title("FoodWise AI")
        
        # Set permanent light mode
        st.markdown("""
        <style>
            .stApp {
                background-color: #FFFFFF;
                color: #262730;
            }
            .st-bq {
                background-color: #F0F8FF;
            }
            .st-c0 {
                color: #262730;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation options based on authentication state
        if st.session_state.authenticated:
            st.write(f"Welcome, {st.session_state.user_data.get('email', 'User')}")
            
            # Navigation menu
            nav_options = ["Home", "Generate Meal Plan", "About", "Logout"]
            
            for nav in nav_options:
                if nav == "Logout":
                    if st.sidebar.button("Logout", key="nav_logout"):
                        if logout():
                            st.session_state.authenticated = False
                            st.session_state.user_data = None
                            st.session_state.meal_plan = None
                            st.session_state.current_page = "home"
                            st.rerun()
                else:
                    nav_key = nav.lower().replace(" ", "_")
                    if st.sidebar.button(nav, key=f"nav_{nav_key}"):
                        st.session_state.current_page = nav_key
                        st.rerun()
        else:
            # Login/Signup buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login", key="nav_login", use_container_width=True):
                    st.session_state.current_page = "login"
                    st.rerun()
            with col2:
                if st.button("Sign Up", key="nav_signup", use_container_width=True):
                    st.session_state.current_page = "signup"
                    st.rerun()
            
            # Other navigation for non-logged in users
            if st.sidebar.button("About", key="nav_about"):
                st.session_state.current_page = "about"
                st.rerun()
            
            if st.sidebar.button("Home", key="nav_home"):
                st.session_state.current_page = "home"
                st.rerun()

# Authentication pages
def render_login_page():
    st.title("Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                with st.spinner("Logging in..."):
                    success, user = login(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_data = user
                        st.session_state.current_page = "home"
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {user}")
    
    st.write("Don't have an account?")
    if st.button("Sign Up", key="go_to_signup"):
        st.session_state.current_page = "signup"
        st.rerun()

def render_signup_page():
    st.title("Create an Account")
    
    with st.form("signup_form"):
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password", 
                               help="Password must be at least 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("Create Account", use_container_width=True)
        
        if submit_button:
            if not email or not password or not confirm_password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match!")
            else:
                with st.spinner("Creating your account..."):
                    success, user_or_error = signup(email, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_data = user_or_error
                        st.session_state.current_page = "home"
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error creating account: {user_or_error}")
    
    st.write("Already have an account?")
    if st.button("Login", key="go_to_login"):
        st.session_state.current_page = "login"
        st.rerun()

# Main app page
def render_meal_plan_page():
    st.title("🍎 Generate Your Personalized Meal Plan")
    
    # Create two columns - one for inputs, one for results
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Your Health Profile")
        
        # Health conditions selection
        health_conditions_list = data['health_conditions']['condition'].tolist()
        selected_conditions = st.multiselect(
            "Select your health conditions (if any):",
            options=health_conditions_list
        )
        
        # Dietary preferences section
        st.subheader("Dietary Preferences")
        
        # Dietary restrictions
        dietary_restrictions = ["Vegetarian", "Vegan", "Pescatarian", "Gluten-Free", "Dairy-Free", 
                                "Keto", "Paleo", "Low Carb", "Low Fat", "Low Sodium"]
        selected_diet = st.multiselect(
            "Select your dietary preferences:",
            options=dietary_restrictions
        )
        
        # Foods to avoid
        food_categories = ["Red Meat", "Poultry", "Seafood", "Eggs", "Dairy", "Gluten", 
                           "Nuts", "Soy", "Shellfish", "Spicy Foods", "Processed Foods", "Added Sugar"]
        avoided_foods = st.multiselect(
            "Select foods you want to avoid:",
            options=food_categories
        )
        
        # Additional custom foods to avoid
        custom_avoided_foods = st.text_input("Any other specific foods you want to avoid? (comma-separated)")
        
        # Additional information
        st.subheader("Personal Information")
        age = st.slider("Age", 18, 100, 30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
        height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1)
        
        # Calculate BMI
        bmi = weight / ((height/100) ** 2)
        
        activity_levels = {
            "Sedentary (little or no exercise)": 1.2,
            "Lightly active (light exercise/sports 1-3 days/week)": 1.375,
            "Moderately active (moderate exercise/sports 3-5 days/week)": 1.55,
            "Very active (hard exercise/sports 6-7 days a week)": 1.725,
            "Super active (very hard exercise, physical job or training twice a day)": 1.9
        }
        
        activity_level = st.selectbox("Activity Level", list(activity_levels.keys()))
        activity_factor = activity_levels[activity_level]
        
        # Calculate daily calorie needs using Harris-Benedict equation
        if gender == "Male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        daily_calories = bmr * activity_factor
        
        # Summary of health information
        st.subheader("Health Summary")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("BMI", f"{bmi:.1f}")
            # Interpret BMI
            if bmi < 18.5:
                st.info("Underweight")
            elif 18.5 <= bmi < 25:
                st.success("Normal weight")
            elif 25 <= bmi < 30:
                st.warning("Overweight")
            else:
                st.error("Obese")
        
        with col_b:
            st.metric("Daily Calories", f"{daily_calories:.0f} kcal")
        
        # Generate meal plan button
        if st.button("Generate Meal Plan", type="primary"):
            with st.spinner("Generating your personalized meal plan..."):
                # Prepare input data for model
                # Process custom avoided foods from text input
                custom_foods_list = []
                if custom_avoided_foods:
                    custom_foods_list = [food.strip() for food in custom_avoided_foods.split(',') if food.strip()]
                
                # Generate recommended exercises and yoga poses based on user's health profile
                recommended_exercises = recommend_exercises(selected_conditions, age, gender, bmi, activity_factor)
                recommended_yoga = recommend_yoga_poses(selected_conditions, age, bmi)
                
                input_data = {
                    'health_conditions': selected_conditions,
                    'exercises': recommended_exercises,
                    'yoga_poses': recommended_yoga,
                    'dietary_preferences': selected_diet,
                    'avoided_foods': avoided_foods + custom_foods_list,
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
                    # Force the right column to display the meal plan
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating meal plan: {e}")
    
    # Right column for displaying meal plan
    with col2:
        if st.session_state.meal_plan:
            # Create main tabs for Food, Exercise, and Yoga
            main_tabs = st.tabs(["Food Recommendations", "Exercise Recommendations", "Yoga Recommendations"])
            
            # Food recommendations tab
            with main_tabs[0]:
                st.header("Your Personalized Meal Plan")
                
                # Create tabs for each meal
                meals = ["Breakfast", "Lunch", "Dinner", "Snacks"]
                meal_tabs = st.tabs(meals)
                
                for i, tab in enumerate(meal_tabs):
                    with tab:
                        meal_type = meals[i].lower()
                        if meal_type in st.session_state.meal_plan:
                            meal_items = st.session_state.meal_plan[meal_type]
                            
                            for item in meal_items:
                                with st.container(border=True):
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
                
                # Display total nutritional breakdown in the food tab
                st.subheader("Daily Nutritional Summary")
                
                # Calculate total nutrition
                total_calories = 0
                total_protein = 0
                total_carbs = 0
                total_fat = 0
                
                # Only include meal types (breakfast, lunch, dinner, snacks) in nutritional calculations
                food_meal_types = ['breakfast', 'lunch', 'dinner', 'snacks']
                
                for meal_type in food_meal_types:
                    if meal_type in st.session_state.meal_plan:
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
            
            # Exercise recommendations tab
            with main_tabs[1]:
                st.header("Recommended Exercises")
                st.write("Based on your health profile, these exercises are recommended for you:")
                
                if 'exercises' in st.session_state.meal_plan:
                    recommended_exercises = st.session_state.meal_plan['exercises']
                    
                    # Display recommended exercises
                    for i, exercise in enumerate(recommended_exercises):
                        with st.container(border=True):
                            st.subheader(f"{i+1}. {exercise}")
                            
                            # Look up exercise information from dataset if available
                            exercise_info = data['exercises'][data['exercises']['exercise_name'] == exercise]
                            if not exercise_info.empty and 'description' in exercise_info.columns:
                                st.write(exercise_info.iloc[0]['description'])
                            else:
                                # Default descriptions based on exercise type
                                if "walking" in exercise.lower():
                                    st.write("A low-impact exercise that's excellent for cardiovascular health and weight management.")
                                elif "swimming" in exercise.lower():
                                    st.write("Great full-body workout that's gentle on the joints while improving cardiovascular fitness.")
                                elif "yoga" in exercise.lower():
                                    st.write("Combines physical postures, breathing exercises, and meditation to improve flexibility and reduce stress.")
                                elif "cycling" in exercise.lower():
                                    st.write("Excellent for improving cardiovascular fitness while being easy on the joints.")
                                elif "running" in exercise.lower():
                                    st.write("High-impact cardio exercise that's excellent for burning calories and improving stamina.")
                                elif "weight" in exercise.lower() or "resistance" in exercise.lower():
                                    st.write("Helps build muscle strength and bone density while improving metabolic rate.")
                                else:
                                    st.write("A beneficial exercise for your health profile. Regular practice will help improve your fitness.")
                else:
                    st.info("No specific exercise recommendations generated.")
                
                # General exercise advice based on health conditions
                st.subheader("General Exercise Advice")
                if any(condition in selected_conditions for condition in ["Diabetes", "Hypertension", "Heart Disease"]):
                    st.warning("Always consult your doctor before starting any exercise program. Start slowly and gradually increase intensity.")
                
                if "Arthritis" in selected_conditions:
                    st.warning("Focus on low-impact exercises and avoid activities that cause pain in your joints.")
                
                st.write("Aim for at least 150 minutes of moderate-intensity exercise per week, spread across multiple days.")
            
            # Yoga recommendations tab
            with main_tabs[2]:
                st.header("Recommended Yoga Poses")
                st.write("Based on your health profile, these yoga poses are recommended for you:")
                
                if 'yoga_poses' in st.session_state.meal_plan:
                    recommended_yoga = st.session_state.meal_plan['yoga_poses']
                    
                    # Display recommended yoga poses
                    for i, pose in enumerate(recommended_yoga):
                        with st.container(border=True):
                            st.subheader(f"{i+1}. {pose}")
                            
                            # Look up yoga pose information from dataset if available
                            pose_info = data['yoga_poses'][data['yoga_poses']['pose_name'] == pose]
                            if not pose_info.empty and 'description' in pose_info.columns:
                                st.write(pose_info.iloc[0]['description'])
                            else:
                                # Default descriptions based on pose names
                                if "mountain" in pose.lower():
                                    st.write("A foundational standing pose that improves posture and body awareness.")
                                elif "child" in pose.lower():
                                    st.write("A resting pose that gently stretches the lower back and promotes relaxation.")
                                elif "warrior" in pose.lower():
                                    st.write("A standing pose that builds strength and stamina in the legs and core.")
                                elif "triangle" in pose.lower():
                                    st.write("Stretches and strengthens the legs, spine, and sides of the torso.")
                                elif "tree" in pose.lower():
                                    st.write("A balancing pose that strengthens the legs and core while improving focus.")
                                elif "down" in pose.lower() and "dog" in pose.lower():
                                    st.write("An inversion that strengthens the arms, shoulders, and legs while stretching the hamstrings.")
                                else:
                                    st.write("A beneficial yoga pose for your health profile. Regular practice will improve flexibility and well-being.")
                else:
                    st.info("No specific yoga pose recommendations generated.")
                
                # General yoga advice
                st.subheader("General Yoga Advice")
                st.write("Start with a few minutes of yoga daily and gradually increase duration as your body adapts.")
                st.write("Focus on your breath and move mindfully, never forcing your body into uncomfortable positions.")
                
                if any(condition in selected_conditions for condition in ["Back Pain", "Arthritis", "Osteoporosis"]):
                    st.warning("Be gentle with your practice and use props for support when needed. Avoid poses that cause pain.")


# Home page
def render_home_page():
    st.title("🍎 Personalized Food Recommendation System")
    
    # Welcome message based on authentication state
    if st.session_state.authenticated:
        st.write(f"## Welcome back, {st.session_state.user_data.get('email', 'User')}!")
        st.write("Ready to create your personalized meal plan? Use the navigation menu to get started.")
        
        # Quick access button to generate meal plan
        if st.button("Generate My Meal Plan", key="quick_meal_plan", type="primary"):
            st.session_state.current_page = "generate_meal_plan"
            st.rerun()
    else:
        st.write("""
        ## Welcome to dieto! 
        
        This application helps you create personalized meal plans based on your health conditions, 
        exercise routines, and yoga practices.
        
        ### Features:
        - Personalized food recommendations
        - Meal planning based on health conditions
        - Nutritional information and health benefits
        - Support for various dietary needs
        
        Please log in or sign up to get started!
        """)
        
        # Login/Signup buttons in main area
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="main_login", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()
        with col2:
            if st.button("Sign Up", key="main_signup", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
    
    # Features section
    st.subheader("Why Use Our System?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🥗 Personalized")
        st.write("Get meal recommendations tailored to your specific health needs and activity level.")
    
    with col2:
        st.markdown("### 💪 Health-Focused")
        st.write("Recommendations based on scientific nutritional principles for various health conditions.")
    
    with col3:
        st.markdown("### 📊 Comprehensive")
        st.write("Complete nutritional breakdown and health benefits for each recommendation.")

# About page
def render_about_page():
    st.title("About dieto")
    
    st.write("""
    ## Our Mission
    
    dieto was created to help people make better food choices based on their unique health profiles, 
    exercise routines, and lifestyle factors. We believe that nutrition should be personalized, because
    everyone's body has different needs.
    
    ## How It Works
    
    Our system uses a sophisticated machine learning algorithm to analyze your health conditions, 
    exercise patterns, yoga practices, and other personal metrics to generate meal plans that are 
    specifically tailored to your needs.
    
    1. **Input Your Information**: Tell us about your health conditions, exercises, and yoga practices.
    2. **Generate Recommendations**: Our AI analyzes your data and creates a personalized meal plan.
    3. **View Nutritional Breakdown**: See comprehensive nutritional information for each meal.
    4. **Understand Health Benefits**: Learn how each food item benefits your specific health conditions.
    
    ## Data Privacy
    
    We take your privacy seriously. All personal information is securely stored and never shared with third parties.
    
    ## Contact Us
    
    Have questions or feedback? Contact our team at support@foodwiseai.com
    """)

# Main application flow
def main():
    # Render navigation sidebar
    render_navigation()
    
    # Render current page based on session state
    if st.session_state.current_page == "login":
        render_login_page()
    elif st.session_state.current_page == "signup":
        render_signup_page()
    elif st.session_state.current_page == "generate_meal_plan":
        if st.session_state.authenticated:
            render_meal_plan_page()
        else:
            st.warning("Please log in to generate a meal plan")
            render_login_page()
    elif st.session_state.current_page == "about":
        render_about_page()
    else:  # Default to home
        render_home_page()

if __name__ == "__main__":
    main()
