import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
import time
from datetime import datetime

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

# Mock authentication for demo
# This allows the app to run without actual Firebase credentials
class MockAuth:
    def __init__(self):
        self.users = {}
    
    def create_user(self, email, password):
        if email in self.users:
            raise ValueError("EMAIL_EXISTS")
        
        user_id = f"user_{len(self.users) + 1}"
        self.users[email] = {
            "email": email,
            "password": password,
            "localId": user_id,
            "idToken": f"mock_token_{user_id}"
        }
        return self.users[email]
    
    def get_user_by_email(self, email):
        if email not in self.users:
            raise ValueError("EMAIL_NOT_FOUND")
        return self.users[email]

class MockFirestore:
    def __init__(self):
        self.data = {}
    
    def collection(self, collection_name):
        if collection_name not in self.data:
            self.data[collection_name] = {}
        return MockCollection(self.data[collection_name])

class MockCollection:
    def __init__(self, collection_data):
        self.collection_data = collection_data
    
    def document(self, doc_id):
        if doc_id not in self.collection_data:
            self.collection_data[doc_id] = {}
        return MockDocument(self.collection_data[doc_id])

class MockDocument:
    def __init__(self, document_data):
        self.document_data = document_data
    
    def set(self, data, merge=False):
        if merge:
            self.document_data.update(data)
        else:
            self.document_data.clear()
            self.document_data.update(data)
    
    def update(self, data):
        self.document_data.update(data)
    
    def get(self):
        return MockDocumentSnapshot(self.document_data)

class MockDocumentSnapshot:
    def __init__(self, data):
        self.data = data
    
    def to_dict(self):
        return self.data

# Initialize Firebase
@st.cache_resource
def initialize_firebase():
    """Initialize Firebase Admin SDK or fallback to mock for demonstration"""
    # For demo purposes, we'll use a mock implementation
    return {
        "auth": MockAuth(),
        "firestore": MockFirestore(),
        "is_mock": True
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
        firebase_instance = initialize_firebase()
        mock_auth = firebase_instance["auth"]
        
        # Try to get user by email
        try:
            user_data = mock_auth.get_user_by_email(email)
            # Simple password check for demo purposes
            if user_data["password"] != password:
                return False, "Invalid password"
            
            # Create a user object similar to what Firebase would return
            user = {
                "localId": user_data["localId"],
                "email": email,
                "idToken": user_data["idToken"],
            }
            return True, user
        except ValueError as e:
            error_message = str(e)
            if "EMAIL_NOT_FOUND" in error_message:
                return False, "Email not found"
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
        firebase_instance = initialize_firebase()
        mock_auth = firebase_instance["auth"]
        mock_db = firebase_instance["firestore"]
        
        # Create user
        try:
            user_data = mock_auth.create_user(email, password)
            user_id = user_data["localId"]
            
            # Add user to database with default preferences
            user_record = {
                "email": email,
                "created_at": datetime.now().isoformat(),
                "preferences": {
                    "dietary_restrictions": [],
                    "favorite_foods": []
                }
            }
            
            # Store in Firestore
            mock_db.collection("users").document(user_id).set(user_record)
            
            # Return user data
            user = {
                "localId": user_id,
                "email": email,
                "idToken": user_data["idToken"]
            }
            return True, user
        except ValueError as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                return False, "Email already exists"
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
        firebase_instance = initialize_firebase()
        mock_db = firebase_instance["firestore"]
        
        # Update preferences in Firestore
        user_ref = mock_db.collection("users").document(user_id)
        pref_data = {"preferences": preferences}
        user_ref.update(pref_data)
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
        firebase_instance = initialize_firebase()
        mock_db = firebase_instance["firestore"]
        
        # Get user document from Firestore
        user_doc = mock_db.collection("users").document(user_id).get()
        user_data = user_doc.to_dict()
        
        # Return preferences or empty dict
        return user_data.get("preferences", {}) if user_data else {}
    except Exception as e:
        st.error(f"Error getting preferences: {e}")
        return {}
