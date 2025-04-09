import os
import streamlit as st
import requests
import json
from datetime import datetime

# Firebase web API endpoints
FIREBASE_SIGNUP_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
FIREBASE_LOGIN_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
FIREBASE_USER_DATA_URL = "https://identitytoolkit.googleapis.com/v1/accounts:lookup"

# Firebase configuration
def get_firebase_config():
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID")
    }

def login(email, password):
    """
    Authenticate user with Firebase
    
    Args:
        email (str): User's email
        password (str): User's password
        
    Returns:
        tuple: (success_status, user_data or error_message)
    """
    try:
        # Get Firebase API key
        config = get_firebase_config()
        api_key = config.get("apiKey")
        
        if not api_key:
            return False, "Firebase API key not found"
        
        # Prepare request data
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        # Send request to Firebase Authentication API
        response = requests.post(
            f"{FIREBASE_LOGIN_URL}?key={api_key}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        # Process response
        data = response.json()
        
        if response.status_code == 200:
            # Successful login
            user_data = {
                "localId": data.get("localId"),
                "email": data.get("email"),
                "idToken": data.get("idToken"),
                "refreshToken": data.get("refreshToken"),
                "expiresIn": data.get("expiresIn")
            }
            return True, user_data
        else:
            # Failed login
            error_message = data.get("error", {}).get("message", "Unknown error")
            if error_message == "EMAIL_NOT_FOUND":
                return False, "Email not found"
            elif error_message == "INVALID_PASSWORD":
                return False, "Invalid password"
            else:
                return False, f"Login error: {error_message}"
    except Exception as e:
        return False, f"Login error: {str(e)}"

def signup(email, password):
    """
    Create a new user in Firebase
    
    Args:
        email (str): User's email
        password (str): User's password
        
    Returns:
        tuple: (success_status, user_data or error_message)
    """
    try:
        # Get Firebase API key
        config = get_firebase_config()
        api_key = config.get("apiKey")
        
        if not api_key:
            return False, "Firebase API key not found"
        
        # Prepare request data
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        # Send request to Firebase Authentication API
        response = requests.post(
            f"{FIREBASE_SIGNUP_URL}?key={api_key}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        # Process response
        data = response.json()
        
        if response.status_code == 200:
            # Successful signup
            user_data = {
                "localId": data.get("localId"),
                "email": data.get("email"),
                "idToken": data.get("idToken"),
                "refreshToken": data.get("refreshToken"),
                "expiresIn": data.get("expiresIn")
            }
            
            # Store user preferences in Firebase Realtime Database
            # This would normally be implemented, but is omitted for simplicity in this demo
            
            return True, user_data
        else:
            # Failed signup
            error_message = data.get("error", {}).get("message", "Unknown error")
            if error_message == "EMAIL_EXISTS":
                return False, "Email already exists"
            elif "WEAK_PASSWORD" in error_message:
                return False, "Password is too weak (minimum 6 characters)"
            else:
                return False, f"Signup error: {error_message}"
    except Exception as e:
        return False, f"Signup error: {str(e)}"

def is_authenticated():
    """Check if user is authenticated"""
    return 'authenticated' in st.session_state and st.session_state.authenticated

def get_current_user():
    """Get current user data"""
    if is_authenticated():
        return st.session_state.user_data
    return None

def logout():
    """Logout current user"""
    if is_authenticated():
        # Clear session state
        return True
    return False

def get_user_info(id_token):
    """
    Get user information from Firebase using the ID token
    
    Args:
        id_token (str): Firebase ID token
        
    Returns:
        dict: User information
    """
    try:
        # Get Firebase API key
        config = get_firebase_config()
        api_key = config.get("apiKey")
        
        if not api_key:
            return None
        
        # Prepare request data
        payload = {
            "idToken": id_token
        }
        
        # Send request to Firebase Authentication API
        response = requests.post(
            f"{FIREBASE_USER_DATA_URL}?key={api_key}",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        # Process response
        data = response.json()
        
        if response.status_code == 200 and "users" in data:
            return data["users"][0]
        else:
            return None
    except Exception:
        return None
