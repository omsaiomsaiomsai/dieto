import pandas as pd
import numpy as np
import torch
import random
from model import FoodRecommendationModel
from data_preprocessing import preprocess_data
import streamlit as st

# Initialize recommendation model
@st.cache_resource
def get_recommendation_model():
    """
    Initialize and return the food recommendation model
    
    Returns:
        FoodRecommendationModel: PyTorch model for food recommendation
    """
    # Define model parameters
    input_size = 50  # This should match the size of your input features
    hidden_size = 128
    output_size = 64  # Feature embedding size
    
    # Create and return model
    model = FoodRecommendationModel(input_size, hidden_size, output_size)
    return model

def generate_meal_plan(input_data, food_data):
    """
    Generate a personalized meal plan based on user input
    
    Args:
        input_data (dict): User inputs including health conditions, exercises, etc.
        food_data (pandas.DataFrame): Food data with nutritional information
        
    Returns:
        dict: Meal plan with breakfast, lunch, dinner, and snacks
    """
    # Initialize model
    model = get_recommendation_model()
    
    # Preprocess data
    user_features, food_features, food_indices = preprocess_data(input_data, food_data)
    
    # Get recommendations
    with torch.no_grad():
        user_embedding = model(user_features)
        food_embeddings = torch.stack([model(f) for f in food_features])
        
        # Calculate similarity scores
        similarity = torch.nn.functional.cosine_similarity(user_embedding.unsqueeze(0), food_embeddings)
        
        # Get top recommendations for each meal type
        meal_plan = {}
        
        # Filter food by meal type and sort by similarity
        breakfast_foods = food_data[food_data['meal_type'].str.contains('breakfast', case=False, na=False)]
        lunch_foods = food_data[food_data['meal_type'].str.contains('lunch', case=False, na=False)]
        dinner_foods = food_data[food_data['meal_type'].str.contains('dinner', case=False, na=False)]
        snack_foods = food_data[food_data['meal_type'].str.contains('snack', case=False, na=False)]
        
        # In a real system, we would use the similarity scores to rank foods
        # For this prototype, we'll select random foods from each category
        
        # Create meal plan
        meal_plan['breakfast'] = generate_meal_items(breakfast_foods, input_data, 2)
        meal_plan['lunch'] = generate_meal_items(lunch_foods, input_data, 3)
        meal_plan['dinner'] = generate_meal_items(dinner_foods, input_data, 3)
        meal_plan['snacks'] = generate_meal_items(snack_foods, input_data, 2)
        
        # Include recommended exercises and yoga poses in the meal plan
        if 'exercises' in input_data:
            meal_plan['exercises'] = input_data['exercises']
        
        if 'yoga_poses' in input_data:
            meal_plan['yoga_poses'] = input_data['yoga_poses']
        
        return meal_plan

def generate_meal_items(foods_df, user_data, num_items=2):
    """
    Generate meal items for a specific meal type
    
    Args:
        foods_df (pandas.DataFrame): Food data filtered by meal type
        user_data (dict): User input data
        num_items (int): Number of items to include in the meal
        
    Returns:
        list: List of meal items with nutritional information
    """
    # Get user's preferences and restrictions
    health_conditions = user_data.get('health_conditions', [])
    dietary_preferences = user_data.get('dietary_preferences', [])
    avoided_foods = user_data.get('avoided_foods', [])
    daily_calories = user_data.get('daily_calories', 2000)
    
    # Filter foods based on health conditions and dietary preferences
    filtered_foods = foods_df.copy()
    
    # Handle dietary preferences
    if 'Vegetarian' in dietary_preferences:
        # Exclude foods with category containing meat
        filtered_foods = filtered_foods[~filtered_foods['category'].str.contains('meat', case=False, na=False)]
        # Exclude meat-based protein foods
        meat_pattern = 'chicken|beef|pork|turkey|lamb'
        protein_foods = filtered_foods['category'] == 'protein'
        contains_meat = filtered_foods['name'].str.contains(meat_pattern, case=False, na=False)
        filtered_foods = filtered_foods[~(protein_foods & contains_meat)]
    
    if 'Vegan' in dietary_preferences:
        # Exclude animal products by category
        filtered_foods = filtered_foods[~filtered_foods['category'].str.contains('meat|dairy', case=False, na=False)]
        
        # Exclude foods with animal products in the name
        animal_pattern = 'milk|cheese|yogurt|egg|chicken|beef|pork|fish|turkey|lamb'
        filtered_foods = filtered_foods[~filtered_foods['name'].str.contains(animal_pattern, case=False, na=False)]
    
    if 'Gluten-Free' in dietary_preferences:
        # Exclude gluten-containing foods
        filtered_foods = filtered_foods[~filtered_foods['name'].str.contains('wheat|bread|pasta|cereal', case=False, na=False)]
        
    if 'Dairy-Free' in dietary_preferences:
        # Exclude dairy products
        filtered_foods = filtered_foods[~filtered_foods['category'].str.contains('dairy', case=False, na=False)]
        filtered_foods = filtered_foods[~filtered_foods['name'].str.contains('milk|cheese|yogurt', case=False, na=False)]
    
    # Handle foods to avoid
    food_avoid_patterns = []
    for food in avoided_foods:
        if food == "Red Meat":
            food_avoid_patterns.append('beef|steak|pork|lamb')
        elif food == "Poultry":
            food_avoid_patterns.append('chicken|turkey|duck')
        elif food == "Seafood":
            food_avoid_patterns.append('fish|salmon|tuna|cod|tilapia')
        elif food == "Eggs":
            food_avoid_patterns.append('egg')
        elif food == "Dairy":
            food_avoid_patterns.append('milk|cheese|yogurt')
        elif food == "Gluten":
            food_avoid_patterns.append('wheat|bread|pasta|cereal')
        elif food == "Nuts":
            food_avoid_patterns.append('nut|almond|peanut|walnut|cashew')
        elif food == "Soy":
            food_avoid_patterns.append('soy|tofu')
        elif food == "Shellfish":
            food_avoid_patterns.append('shrimp|crab|lobster')
        elif food == "Spicy Foods":
            food_avoid_patterns.append('spicy|chili|pepper')
        elif food == "Processed Foods":
            food_avoid_patterns.append('processed')
        elif food == "Added Sugar":
            food_avoid_patterns.append('sugar|sweet|dessert|candy')
        else:
            # Add custom foods to avoid (with exact matching)
            food_avoid_patterns.append(food.lower())
    
    # Apply the filters for foods to avoid
    if food_avoid_patterns:
        combined_pattern = '|'.join(food_avoid_patterns)
        filtered_foods = filtered_foods[~filtered_foods['name'].str.lower().str.contains(combined_pattern, case=False, na=False)]
    
    # Apply filters based on health conditions
    if 'Diabetes' in health_conditions and 'sugar' in filtered_foods.columns:
        filtered_foods = filtered_foods[filtered_foods['sugar'] < 10]
    
    if 'Hypertension' in health_conditions and 'sodium' in filtered_foods.columns:
        filtered_foods = filtered_foods[filtered_foods['sodium'] < 500]
    
    # If no foods left after filtering, use original foods
    if len(filtered_foods) == 0:
        filtered_foods = foods_df
    
    # Select random food items
    if len(filtered_foods) <= num_items:
        selected_foods = filtered_foods
    else:
        selected_foods = filtered_foods.sample(num_items)
    
    # Create meal items list
    meal_items = []
    
    for _, food in selected_foods.iterrows():
        # Calculate portion size based on calories
        portion_factor = 1.0
        if 'calories' in food:
            meal_calories_target = daily_calories * 0.3 if 'breakfast' in food['meal_type'].lower() else daily_calories * 0.35
            if food['calories'] > 0:
                portion_factor = min(2.0, meal_calories_target / (food['calories'] * num_items))
        
        # Create meal item
        item = {
            'name': food['name'],
            'calories': food['calories'] * portion_factor if 'calories' in food else 0,
            'protein': food['protein'] * portion_factor if 'protein' in food else 0,
            'carbs': food['carbs'] * portion_factor if 'carbs' in food else 0,
            'fat': food['fat'] * portion_factor if 'fat' in food else 0,
            'benefits': generate_benefits(food, health_conditions),
            'portion': generate_portion_description(food, portion_factor)
        }
        
        meal_items.append(item)
    
    return meal_items

def generate_benefits(food, health_conditions):
    """
    Generate health benefits description for a food item
    
    Args:
        food (pandas.Series): Food data
        health_conditions (list): User's health conditions
        
    Returns:
        list: List of health benefits
    """
    benefits = []
    
    # Add general benefits based on nutritional content
    if 'protein' in food and food['protein'] > 15:
        benefits.append("High in protein, good for muscle maintenance and recovery")
    
    if 'fiber' in food and food['fiber'] > 5:
        benefits.append("Rich in fiber, promotes digestive health")
    
    if 'vitamins' in food and 'A' in str(food['vitamins']):
        benefits.append("Contains Vitamin A, supports vision and immune function")
    
    if 'vitamins' in food and 'C' in str(food['vitamins']):
        benefits.append("Contains Vitamin C, boosts immunity")
    
    # Add benefits specific to health conditions
    for condition in health_conditions:
        if condition == 'Diabetes':
            if 'glycemic_index' in food and food['glycemic_index'] < 55:
                benefits.append("Low glycemic index, helps maintain stable blood sugar levels")
        
        elif condition == 'Hypertension':
            if 'sodium' in food and food['sodium'] < 140:
                benefits.append("Low in sodium, supports healthy blood pressure")
            
            if 'potassium' in food and food['potassium'] > 300:
                benefits.append("Good source of potassium, helps regulate blood pressure")
        
        elif condition == 'Heart Disease':
            if 'saturated_fat' in food and food['saturated_fat'] < 2:
                benefits.append("Low in saturated fat, heart-friendly option")
            
            if 'omega3' in food and food['omega3'] > 0:
                benefits.append("Contains omega-3 fatty acids, supports heart health")
    
    # If no specific benefits found, add a generic one
    if not benefits:
        food_category = food['category'] if 'category' in food else "food"
        benefits.append(f"A nutritious {food_category} option in your balanced diet")
    
    return benefits

def generate_portion_description(food, portion_factor):
    """
    Generate portion size description
    
    Args:
        food (pandas.Series): Food data
        portion_factor (float): Factor to adjust portion size
        
    Returns:
        str: Portion description
    """
    base_portion = "1 serving"
    
    if 'serving_size' in food and not pd.isna(food['serving_size']):
        base_portion = food['serving_size']
    
    if portion_factor != 1.0:
        if portion_factor < 0.75:
            return f"Small portion ({portion_factor:.1f} x {base_portion})"
        elif portion_factor > 1.25:
            return f"Large portion ({portion_factor:.1f} x {base_portion})"
    
    return f"Regular portion ({base_portion})"
