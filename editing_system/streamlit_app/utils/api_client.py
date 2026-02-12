import requests
from typing import Optional
import streamlit as st
from editing_system.streamlit_app.config import settings


class APIClient:

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or f"http://{settings.HOST}:{settings.FASTAPI_PORT}"

    def login(self, email: str, password: str):
        response = requests.post(
            f"{self.api_url}/auth/login",  # TODO здесь сделать не json a LoginRequest
            json={
                "email": email,
                "password": password
            }
        )

        if response.status_code != 200:
            raise Exception("Invalid credentials")

        return response.json()

    def get_headers(self):
        token = st.session_state.get("access_token")
        return {
            "Authorization": f"Bearer {token}"
        }

    def get_current_user(self):
        response = requests.get(
            f"{self.api_url}/users/me",
            headers=self.get_headers()
        )

        if response.status_code == 401:
            raise Exception("Unauthorized")

        if response.status_code != 200:
            raise Exception("Error checking user")

        return response.json()

    def register(self, email: str, password: str):
        response = requests.post(
            f"{self.api_url}/users/",
            json={
                "email": email,
                "password": password,
                "full_name": email.split("@")[0]
            }
        )

        if response.status_code == 400:
            raise Exception("User already exists")

        if response.status_code != 201:
            raise Exception("Registration failed")

        return response.json()


api_client = APIClient()
