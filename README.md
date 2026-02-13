# Thooral Hackathon - GSuite CLI

A command-line interface (CLI) for interacting with Google Workspace (Docs, Sheets, Forms).

## Technology Stack

*   **Language:** Python
*   **CLI Framework:** Click
*   **Google API Client Libraries:** `google-api-python-client`, `google-auth-oauthlib`

## Implemented Features

Currently, the CLI supports authentication and basic Google Docs operations.

### 1. Authentication

Before using any Google Workspace commands, you need to authenticate with your Google account.

**`gsuite auth login`**

Initiates the OAuth 2.0 flow to authenticate the user. You will need to set up a Google Cloud Project and enable the necessary Google Docs and Google Drive APIs. Download your OAuth 2.0 client configuration and save it as `client_secrets.json` in the `~/.gsuite_cli/` directory.

**Usage:**

```bash
python3 gsuite_cli.py auth login
```

Follow the on-screen instructions to complete the authentication process in your web browser.

**`gsuite auth logout`**

(Not yet implemented - planned) Revokes access tokens and deletes local credentials.

### 2. Google Docs Commands

These commands allow you to manage Google Documents.

**`gsuite docs create <title>`**

Creates a new Google Document with the specified title.

**Usage:**

```bash
python3 gsuite_cli.py docs create "My New Document Title"
```

**Output:**

```
Created document with title: My New Document Title
Document ID: <document_id>
Document URL: https://docs.google.com/document/d/<document_id>/edit
```

**`gsuite docs list`**

Lists recently accessed Google Documents (only Google Docs files, not other Drive files).

**Usage:**

```bash
python3 gsuite_cli.py docs list
```

**Output:**

```
Documents:
My New Document Title (<document_id>)
Another Document Title (<another_document_id>)
```

**`gsuite docs get <document_id>`**

Retrieves and displays the content of a specified Google Document.

**Usage:**

```bash
python3 gsuite_cli.py docs get <document_id>
```

**Output:**

```
Document Title: My New Document Title
Document ID: <document_id>

Content:
This is the content of the document.
```

**`gsuite docs delete <document_id>`**

Deletes a specified Google Document.

**Usage:**

```bash
python3 gsuite_cli.py docs delete <document_id>
```

**Output:**

```
Document with ID '<document_id>' deleted successfully.
```

**`gsuite docs edit <document_id> --append <text_content>`**

Appends the provided text content to the end of a specified Google Document.

**Usage:**

```bash
python3 gsuite_cli.py docs edit <document_id> --append "This text will be added at the end."
```

**Output:**

```
Text appended to document ID '<document_id>' successfully.
```

**Important Note on Appending to Empty Documents:**

Due to nuances in the Google Docs API's `insertText` operation, directly appending text to a *truly empty* document (one with no content beyond the default initial newline character) for the *very first* insertion can be inconsistent. This `edit --append` command is most reliable when used on documents that already contain some content. If you encounter issues when appending to a brand new, empty document, consider adding some initial content manually or using a different API request type (e.g., `replaceContent`) for the first write.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/thooral-hackathon.git
    cd thooral-hackathon
    ```
2.  **Create a Python virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Google Cloud Project Setup:**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.
    *   Enable the **Google Docs API** and **Google Drive API** for your project.
    *   Navigate to "APIs & Services" -> "Credentials".
    *   Create "OAuth client ID" credentials for a "Desktop app".
    *   Download the `client_secrets.json` file.
    *   Create a directory `~/.gsuite_cli/` and place the downloaded `client_secrets.json` file inside it.
        ```bash
        mkdir -p ~/.gsuite_cli
        mv /path/to/your/downloaded/client_secrets.json ~/.gsuite_cli/client_secrets.json
        ```
4.  **Authenticate the CLI:**
    ```bash
    python3 gsuite_cli.py auth login
    ```

You are now ready to use the GSuite CLI!
