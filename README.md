# Thooral Hackathon - GSuite CLI

A command-line interface (CLI) for interacting with Google Workspace (Docs, Sheets, Forms).

## Technology Stack

*   **Language:** Python
*   **CLI Framework:** Click
*   **Google API Client Libraries:** `google-api-python-client`, `google-auth-oauthlib`

## Implemented Features

Currently, the CLI supports authentication, Google Docs operations, and core Google Sheets operations.

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

Revokes your refresh token (when available) and deletes local credentials from `~/.gsuite_cli/credentials.json`.

**Usage:**

```bash
python3 gsuite_cli.py auth logout
```

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

```bash
python3 gsuite_cli.py docs get <document_id> --format markdown
```

```bash
python3 gsuite_cli.py docs get <document_id> --format markdown --output ./doc.md
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

```bash
python3 gsuite_cli.py docs delete <document_id> --yes
```

Without `--yes`, the CLI asks for confirmation before deleting.

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

**`gsuite docs edit <document_id> --set <text_content>`**

Replaces the full document content with the provided text.

**Usage:**

```bash
python3 gsuite_cli.py docs edit <document_id> --set "This becomes the full content."
```

**Output:**

```
Document ID '<document_id>' content replaced successfully.
```

`docs edit` accepts exactly one mode at a time: `--append` or `--set`.

**`gsuite docs copy <document_id> <new_title>`**

Creates a copy of an existing Google Document with a new title.

**Usage:**

```bash
python3 gsuite_cli.py docs copy <document_id> "Copied Document Title"
```

**`gsuite docs share <document_id> --email <email> --role <reader|writer|commenter>`**

### 3. Google Sheets Commands

**`gsuite sheets create <title>`**

Creates a new Google Sheet.

**Usage:**

```bash
python3 gsuite_cli.py sheets create "Budget 2026"
```

**`gsuite sheets list`**

Lists Google Sheets available through your Drive access.

**Usage:**

```bash
python3 gsuite_cli.py sheets list
```

**`gsuite sheets read <spreadsheet_id> <range>`**

Reads values from a specific range.

**Usage:**

```bash
python3 gsuite_cli.py sheets read <spreadsheet_id> "Sheet1!A1:C5"
```

**`gsuite sheets write <spreadsheet_id> <range> <data>`**

Writes values to a specific range.

Supported data input formats:
- Comma-separated single row: `"1,2,3"`
- Semicolon-separated rows: `"1,2;3,4"`
- JSON list/list-of-lists: `"[\"A\",\"B\"]"` or `"[[\"A\",\"B\"],[\"C\",\"D\"]]"`

**Usage:**

```bash
python3 gsuite_cli.py sheets write <spreadsheet_id> "Sheet1!A1:C1" "1,2,3"
```

```bash
python3 gsuite_cli.py sheets write <spreadsheet_id> "Sheet1!A1:B2" "[[\"A\",\"B\"],[\"C\",\"D\"]]" --value-input-option user_entered
```

**`gsuite sheets clear <spreadsheet_id> <range>`**

Clears values from a specific range.

**Usage:**

```bash
python3 gsuite_cli.py sheets clear <spreadsheet_id> "Sheet1!A1:C5"
```

### 4. Google Forms Commands

**`gsuite forms create <title>`**

Creates a new Google Form.

**Usage:**

```bash
python3 gsuite_cli.py forms create "Customer Feedback"
```

**`gsuite forms list`**

Lists Google Forms accessible via your Drive.

**Usage:**

```bash
python3 gsuite_cli.py forms list
```

**`gsuite forms add-question <form_id> --type <text|paragraph|choice> --title <question_text> [--options <opt1,opt2,...>]`**

Adds a question to an existing form.

**Usage:**

```bash
python3 gsuite_cli.py forms add-question <form_id> --type text --title "What is your name?"
```

```bash
python3 gsuite_cli.py forms add-question <form_id> --type paragraph --title "Tell us more about your experience."
```

```bash
python3 gsuite_cli.py forms add-question <form_id> --type choice --title "Rate us" --options "Excellent,Good,Fair,Poor"
```

`--options` is required when `--type choice` is used.

**`gsuite forms get-responses <form_id>`**

Fetches responses for a form and prints each response with answer values.

**Usage:**

```bash
python3 gsuite_cli.py forms get-responses <form_id>
```

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
    *   Enable the **Google Docs API**, **Google Drive API**, **Google Sheets API**, and **Google Forms API** for your project.
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

If you authenticated before Sheets/Forms support was added, run `auth login` again so new scopes are granted.

You are now ready to use the GSuite CLI!
