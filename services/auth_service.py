import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from google_auth_oauthlib.flow import InstalledAppFlow

from services.config import (
    CLIENT_SECRETS_FILE,
    CREDENTIALS_FILE,
    TOKEN_REVOKE_URL,
    SCOPES,
)
from services.credentials import ensure_credentials_dir, load_token_payload


def login():
    ensure_credentials_dir()

    if not os.path.exists(CLIENT_SECRETS_FILE):
        raise FileNotFoundError(
            f"client_secrets.json not found at {CLIENT_SECRETS_FILE}"
        )

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())


def _revoke_refresh_token(refresh_token):
    encoded_data = urlencode({"token": refresh_token}).encode("utf-8")
    request = Request(
        TOKEN_REVOKE_URL,
        data=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    try:
        with urlopen(request, timeout=10) as response:
            return response.status == 200, None
    except HTTPError as error:
        return False, f"Token revocation failed with HTTP {error.code}."
    except URLError as error:
        return False, f"Token revocation request failed: {error.reason}"


def logout():
    if not os.path.exists(CREDENTIALS_FILE):
        return {
            "credentials_found": False,
            "credentials_deleted": False,
            "revocation_attempted": False,
            "token_revoked": False,
            "revoke_error": None,
        }

    payload = load_token_payload()
    refresh_token = payload.get("refresh_token")

    revocation_attempted = bool(refresh_token)
    token_revoked = False
    revoke_error = None
    if refresh_token:
        token_revoked, revoke_error = _revoke_refresh_token(refresh_token)

    os.remove(CREDENTIALS_FILE)

    return {
        "credentials_found": True,
        "credentials_deleted": True,
        "revocation_attempted": revocation_attempted,
        "token_revoked": token_revoked,
        "revoke_error": revoke_error,
    }

