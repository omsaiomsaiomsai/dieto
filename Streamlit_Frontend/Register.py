import streamlit as st
import json
import requests

def sign_up_with_email_and_password():
    try:
        email = st.session_state["email"]
        password = st.session_state["password"]
        username = st.session_state.get("username", "")

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
        user_info = response.json()
        st.success(f"User {user_info['email']} registered successfully!")
    except requests.exceptions.HTTPError as e:
        error_message = e.response.json()
        st.error(f"Signup failed: {error_message.get('error', {}).get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Streamlit form for user registration
st.header(":red[Register]")
first_name = st.text_input("First Name")
last_name = st.text_input("Last Name")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

st.session_state["email"] = email
st.session_state["password"] = password
st.session_state["username"] = username

st.button("Register", on_click=sign_up_with_email_and_password)
