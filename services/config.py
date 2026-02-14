import os

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]

CREDENTIALS_DIR = os.path.join(os.path.expanduser("~"), ".gsuite_cli")
CLIENT_SECRETS_FILE = os.path.join(CREDENTIALS_DIR, "client_secrets.json")
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, "credentials.json")
CONFIG_FILE = os.path.join(CREDENTIALS_DIR, "config.json")

TOKEN_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
