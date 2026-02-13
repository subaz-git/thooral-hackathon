import click
import os
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

def get_credentials():
    creds = None
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            click.echo("Credentials not found or expired. Please run 'gsuite auth login' first.")
            return None
    return creds

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
    creds = get_credentials()
    if not creds:
        return

    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().create(body={'title': title}).execute()
        click.echo(f"Created document with title: {title}")
        click.echo(f"Document ID: {document.get('documentId')}")
        click.echo(f"Document URL: https://docs.google.com/document/d/{document.get('documentId')}/edit")
    except HttpError as error:
        click.echo(f"An error occurred: {error}")


@docs.command()
def list():
    """Lists Google Docs."""
    creds = get_credentials()
    if not creds:
        return

    try:
        service = build('drive', 'v3', credentials=creds)
        # Call the Drive v3 API to list Google Docs files.
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.document'",
            fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            click.echo('No documents found.')
        else:
            click.echo('Documents:')
            for item in items:
                click.echo(f"{item['name']} ({item['id']})")
    except HttpError as error:
        click.echo(f"An error occurred: {error}")


@docs.command()
@click.argument('document_id')
def get(document_id):
    """Gets the content of a Google Doc."""
    creds = get_credentials()
    if not creds:
        return

    try:
        service = build('docs', 'v1', credentials=creds)
        document = service.documents().get(documentId=document_id).execute()
        
        click.echo(f"Document Title: {document.get('title')}")
        click.echo(f"Document ID: {document.get('documentId')}")
        click.echo("\nContent:")

        if 'body' in document and 'content' in document['body']:
            for structural_element in document['body']['content']:
                if 'paragraph' in structural_element:
                    for paragraph_element in structural_element['paragraph']['elements']:
                        if 'textRun' in paragraph_element:
                            click.echo(paragraph_element['textRun']['content'], nl=False) # nl=False to prevent extra newlines
        else:
            click.echo("Document is empty or has no readable content.")
            
    except HttpError as error:
        click.echo(f"An error occurred: {error}")

@docs.command()
@click.argument('document_id')
def delete(document_id):
    """Deletes a Google Doc."""
    creds = get_credentials()
    if not creds:
        return

    try:
        service = build('drive', 'v3', credentials=creds)
        service.files().delete(fileId=document_id).execute()
        click.echo(f"Document with ID '{document_id}' deleted successfully.")
    except HttpError as error:
        click.echo(f"An error occurred: {error}")

@docs.command()
@click.argument('document_id')
@click.option('--append', help='Text content to append to the document.')
def edit(document_id, append):
    """Edits a Google Doc (currently appends text)."""
    creds = get_credentials()
    if not creds:
        return

    if not append:
        click.echo("Please provide text to append using the --append option.")
        return

    try:
        service = build('docs', 'v1', credentials=creds)
        # Get the current document to find the end index for appending
        # Note: Appending to a truly empty document might still have nuances
        # with the Google Docs API's insertText. This implementation assumes
        # the document has at least a default structural element.
        document = service.documents().get(documentId=document_id, fields='body(content)').execute()
        
        max_end_index = 1 # Default to 1 for new docs, as the minimal content is a newline at index 0-1
        if 'body' in document and 'content' in document['body']:
            for element in document['body']['content']:
                if 'endIndex' in element:
                    max_end_index = max(max_end_index, element['endIndex'])
            
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': max_end_index,
                    },
                    'text': append + '\n'
                }
            }
        ]
        
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
        click.echo(f"Text appended to document ID '{document_id}' successfully.")
    except HttpError as error:
        click.echo(f"An error occurred: {error}")

if __name__ == '__main__':
    gsuite()
