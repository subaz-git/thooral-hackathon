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
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE)

        granted_scopes = set(creds.scopes or [])
        required_scopes = set(SCOPES)
        missing_scopes = sorted(required_scopes - granted_scopes)
        if missing_scopes:
            echo_error(
                "auth",
                "Stored credentials are missing required scopes.",
                "Run 'python3 gsuite_cli.py auth login' to re-authorize with new scopes.",
            )
            return None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as error:
                error_text = str(error)
                if "invalid_scope" in error_text:
                    echo_error(
                        "auth",
                        "Stored credentials are no longer valid for current scopes.",
                        "Run 'python3 gsuite_cli.py auth logout' then 'python3 gsuite_cli.py auth login'.",
                    )
                    return None
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
