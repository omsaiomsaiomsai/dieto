import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import streamlit as st

def load_data(file_path):
    """
    Load data from CSV file
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: Loaded data
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        raise Exception(f"Error loading {file_path}: {e}")

def preprocess_data(input_data, food_data):
    """
    Preprocess input data for the ML model
    
    Args:
        input_data (dict): User inputs including health conditions, exercises, etc.
        food_data (pandas.DataFrame): Food data with nutritional information
        
    Returns:
        tuple: (X_tensor, food_features_tensor, food_indices)
    """
    # Extract health conditions, exercises, and yoga practices
    health_conditions = input_data.get('health_conditions', [])
    exercises = input_data.get('exercises', [])
    yoga_poses = input_data.get('yoga_poses', [])
    
    # Create numerical features
    numerical_features = [
        input_data.get('age', 30),
        input_data.get('weight', 70),
        input_data.get('height', 170),
        input_data.get('bmi', 24),
        input_data.get('activity_level', 1.2),
        input_data.get('daily_calories', 2000)
    ]
    
    # Normalize numerical features
    scaler = StandardScaler()
    numerical_features_norm = scaler.fit_transform(np.array(numerical_features).reshape(1, -1))
    
    # Create binary features for health conditions, exercises, and yoga
    # In a real application, we would use a predefined set of all possible conditions/exercises/yoga
    # For simplicity, we'll use the provided ones
    all_health_conditions = health_conditions
    all_exercises = exercises
    all_yoga_poses = yoga_poses
    
    # Create binary vectors (one-hot encoding)
    health_condition_features = [1 if cond in health_conditions else 0 for cond in all_health_conditions]
    exercise_features = [1 if ex in exercises else 0 for ex in all_exercises]
    yoga_features = [1 if yoga in yoga_poses else 0 for yoga in all_yoga_poses]
    
    # Gender encoding (0 for Male, 1 for Female, 0.5 for Other)
    gender_encoding = 0 if input_data.get('gender', 'Male') == 'Male' else (1 if input_data.get('gender', 'Male') == 'Female' else 0.5)
    
    # Combine all features
    combined_features = (
        numerical_features_norm.flatten().tolist() + 
        [gender_encoding] + 
        health_condition_features + 
        exercise_features + 
        yoga_features
    )
    
    # Convert to tensor
    X_tensor = torch.FloatTensor(combined_features)
    
    # Process food data (extract relevant features for recommendation)
    food_features = extract_food_features(food_data)
    food_features_tensor = torch.FloatTensor(food_features)
    
    # Return processed data
    return X_tensor, food_features_tensor, list(range(len(food_data)))

def extract_food_features(food_data):
    """
    Extract relevant features from food data
    
    Args:
        food_data (pandas.DataFrame): Food data with nutritional information
        
    Returns:
        list: Extracted features for each food item
    """
    # Extract numerical features
    numerical_cols = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar']
    numerical_features = food_data[numerical_cols].values
    
    # Normalize numerical features
    scaler = StandardScaler()
    numerical_features_norm = scaler.fit_transform(numerical_features)
    
    # For categorical features like food category, meal type, etc.
    # In a real application, we would use one-hot encoding
    # For simplicity, we'll just use the numerical features
    
    return numerical_features_norm.tolist()

def create_input_vector(conditions, exercises, yoga, age, gender, weight, height, bmi, activity_level):
    """
    Create an input vector for the ML model
    
    Args:
        conditions (list): Selected health conditions
        exercises (list): Selected exercises
        yoga (list): Selected yoga poses
        age (int): User's age
        gender (str): User's gender
        weight (float): User's weight in kg
        height (float): User's height in cm
        bmi (float): User's BMI
        activity_level (float): User's activity level factor
        
    Returns:
        torch.Tensor: Input vector for the ML model
    """
    # Create vector similar to the preprocessing function
    numerical_features = [age, weight, height, bmi, activity_level]
    
    # Normalize numerical features
    scaler = StandardScaler()
    numerical_features_norm = scaler.fit_transform(np.array(numerical_features).reshape(1, -1))
    
    # Create binary features for health conditions, exercises, and yoga
    health_condition_features = [1] * len(conditions)
    exercise_features = [1] * len(exercises)
    yoga_features = [1] * len(yoga)
    
    # Gender encoding
    gender_encoding = 0 if gender == 'Male' else (1 if gender == 'Female' else 0.5)
    
    # Combine all features
    combined_features = (
        numerical_features_norm.flatten().tolist() + 
        [gender_encoding] + 
        health_condition_features + 
        exercise_features + 
        yoga_features
    )
    
    # Convert to tensor
    return torch.FloatTensor(combined_features)
