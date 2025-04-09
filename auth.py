import os
import pyrebase
import streamlit as st

# Firebase configuration
def get_firebase_config():
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY", "your-api-key"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "your-auth-domain"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "your-database-url"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID", "your-project-id"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "your-storage-bucket"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "your-messaging-sender-id"),
        "appId": os.getenv("FIREBASE_APP_ID", "your-app-id")
    }

# Initialize Firebase
@st.cache_resource
def initialize_firebase():
    config = get_firebase_config()
    return pyrebase.initialize_app(config)

def get_auth():
    firebase = initialize_firebase()
    return firebase.auth()

def get_database():
    firebase = initialize_firebase()
    return firebase.database()

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
        auth = get_auth()
        user = auth.sign_in_with_email_and_password(email, password)
        return True, user
    except Exception as e:
        error_message = str(e)
        if "INVALID_PASSWORD" in error_message:
            return False, "Invalid password"
        elif "EMAIL_NOT_FOUND" in error_message:
            return False, "Email not found"
        else:
            return False, f"Login error: {error_message}"

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
        auth = get_auth()
        user = auth.create_user_with_email_and_password(email, password)
        
        # Add user to database with default preferences
        db = get_database()
        user_data = {
            "email": email,
            "created_at": {".sv": "timestamp"},
            "preferences": {
                "dietary_restrictions": [],
                "favorite_foods": []
            }
        }
        db.child("users").child(user['localId']).set(user_data)
        
        return True, user
    except Exception as e:
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            return False, "Email already exists"
        elif "WEAK_PASSWORD" in error_message:
            return False, "Password is too weak"
        else:
            return False, f"Signup error: {error_message}"

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

def save_user_preferences(user_id, preferences):
    """
    Save user preferences to Firebase database
    
    Args:
        user_id (str): User ID
        preferences (dict): User preferences to save
        
    Returns:
        bool: Success status
    """
    try:
        db = get_database()
        db.child("users").child(user_id).child("preferences").update(preferences)
        return True
    except Exception as e:
        st.error(f"Error saving preferences: {e}")
        return False

def get_user_preferences(user_id):
    """
    Get user preferences from Firebase database
    
    Args:
        user_id (str): User ID
        
    Returns:
        dict: User preferences
    """
    try:
        db = get_database()
        preferences = db.child("users").child(user_id).child("preferences").get().val()
        return preferences if preferences else {}
    except Exception as e:
        st.error(f"Error getting preferences: {e}")
        return {}
