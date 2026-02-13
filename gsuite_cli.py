import click
import os
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define the scopes required for Google Docs and Drive
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/forms.body.readonly', # To list forms by title
    'https://www.googleapis.com/auth/forms.responses.readonly' # To read forms (if needed later)
]

# Path to the directory for storing CLI credentials
CREDENTIALS_DIR = os.path.join(os.path.expanduser('~'), '.gsuite_cli')
CLIENT_SECRETS_FILE = os.path.join(CREDENTIALS_DIR, 'client_secrets.json')
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, 'credentials.json')

@click.group()
def gsuite():
    """A CLI for interacting with Google Workspace (Docs, Sheets, Forms)."""
    pass

@gsuite.group()
def auth():
    """Authentication commands for Google Workspace."""
    pass

@auth.command()
def login():
    """Logs in to Google Workspace."""
    creds = None
    # Create credentials directory if it doesn't exist
    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR)

    # The file credentials.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                click.echo(f"Error: client_secrets.json not found at {CLIENT_SECRETS_FILE}")
                click.echo("Please download your OAuth 2.0 client configuration from Google Cloud Console ")
                click.echo("and save it as client_secrets.json in the directory: " + CREDENTIALS_DIR)
                return

            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            try:
                creds = flow.run_local_server(port=0)
            except Exception as e:
                click.echo(f"Error during OAuth 2.0 flow: {e}")
                return

        # Save the credentials for the next run
        with open(CREDENTIALS_FILE, 'w') as token:
            token.write(creds.to_json())
        click.echo("Authentication successful. Credentials saved.")
    else:
        click.echo("Already logged in. Credentials are valid.")

@auth.command()
def logout():
    """Logs out from Google Workspace."""
    click.echo("Auth Logout command - Not yet implemented.")

@gsuite.group()
def docs():
    """Commands for Google Docs."""
    pass

@docs.command()
@click.argument('title')
def create(title):
    """Creates a new Google Doc."""
    click.echo(f"Docs Create command for title: {title} - Not yet implemented.")

@docs.command()
def list():
    """Lists Google Docs."""
    click.echo("Docs List command - Not yet implemented.")

@docs.command()
@click.argument('document_id')
def get(document_id):
    """Gets the content of a Google Doc."""
    click.echo(f"Docs Get command for document ID: {document_id} - Not yet implemented.")

@docs.command()
@click.argument('document_id')
def delete(document_id):
    """Deletes a Google Doc."""
    click.echo(f"Docs Delete command for document ID: {document_id} - Not yet implemented.")

@docs.command()
@click.argument('document_id')
@click.option('--append', help='Text content to append to the document.')
def edit(document_id, append):
    """Edits a Google Doc (currently appends text)."""
    click.echo(f"Docs Edit command for document ID: {document_id}, append: {append} - Not yet implemented.")

if __name__ == '__main__':
    gsuite()
