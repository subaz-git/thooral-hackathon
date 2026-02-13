import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from services.config import CREDENTIALS_DIR, CREDENTIALS_FILE, SCOPES
from services.errors import echo_error


def ensure_credentials_dir():
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)


def load_token_payload():
    if not os.path.exists(CREDENTIALS_FILE):
        return {}
    with open(CREDENTIALS_FILE, "r", encoding="utf-8") as token_file:
        return json.load(token_file)


def get_credentials():
    creds = None
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as error:
                echo_error("auth", f"Failed to refresh credentials: {error}")
                return None
        else:
            echo_error(
                "auth",
                "Credentials not found or expired.",
                "Run 'python3 gsuite_cli.py auth login' first.",
            )
            return None

    return creds

