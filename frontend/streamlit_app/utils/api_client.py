import requests
from typing import Optional
import streamlit as st
import os


class APIClient:

    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url or os.getenv("API_URL", "http://fastapi:8000")

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

    def get_documents(self):
        response = requests.get(
            f"{self.api_url}/documents/",
            headers=self.get_headers()
        )

        if response.status_code != 200:
            raise Exception("Failed to fetch documents")

        return response.json()

    def create_document(self, title: str, content: str):
        response = requests.post(
            f"{self.api_url}/documents/",
            headers=self.get_headers(),
            json={
                "title": title,
                "content": content
            }
        )

        if response.status_code != 201:
            raise Exception("Failed to create document")

        return response.json()

    def add_version(self, document_id: str, content: str, base_version_id: str):
        response = requests.post(
            f"{self.api_url}/documents/{document_id}/versions",
            headers=self.get_headers(),
            json={
                "content": content,
                "base_version_id": base_version_id,
            }
        )

        if response.status_code == 409:
            raise Exception("Conflict")

        if response.status_code != 200:
            raise Exception("Failed to save version")

        return response.json()

    def get_versions(self, document_id: str, limit: int = 8):
        response = requests.get(
            f"{self.api_url}/documents/{document_id}/versions?limit={limit}",
            headers=self.get_headers()
        )

        if response.status_code != 200:
            raise Exception("Failed to fetch versions")

        return response.json()

    def revert_version(self, document_id: str, version_id: str):
        response = requests.post(
            f"{self.api_url}/documents/{document_id}/revert/{version_id}",
            headers=self.get_headers(),
        )

        if response.status_code != 200:
            raise Exception("Failed to revert")

        return response.json()

    def share_document(self, document_id: str, email: str):
        response = requests.post(
            f"{self.api_url}/documents/{document_id}/share",
            headers=self.get_headers(),
            json={
                "email": email
            }
        )

        if response.status_code != 200:
            raise Exception("Failed to share document")

        return response.json()

    def update_profile(self, full_name: str, about_user: str):
        response = requests.put(
            f"{self.api_url}/users/me",
            headers=self.get_headers(),
            json={
                "full_name": full_name,
                "about_user": about_user
            }
        )

        if response.status_code != 200:
            raise Exception("Failed to update profile")

        return response.json()

    def change_password(self, old_password: str, new_password: str):
        response = requests.post(
            f"{self.api_url}/users/me/change-password",
            headers=self.get_headers(),
            json={
                "old_password": old_password,
                "new_password": new_password
            }
        )

        if response.status_code != 200:
            raise Exception("Failed to change password")

        return response.json()

    def get_diff(self, document_id: str, version_id: str):
        response = requests.get(
            f"{self.api_url}/documents/{document_id}/diff/{version_id}",
            headers=self.get_headers()
        )

        if response.status_code != 200:
            raise Exception("Failed to fetch diff")

        return response.json()["diff"]


api_client = APIClient()
