from googleapiclient.discovery import build


def create_document(creds, title):
    service = build("docs", "v1", credentials=creds)
    return service.documents().create(body={"title": title}).execute()


def copy_document(creds, document_id, new_title):
    service = build("drive", "v3", credentials=creds)
    return service.files().copy(
        fileId=document_id,
        body={"name": new_title},
        fields="id, name",
    ).execute()


def share_document(creds, document_id, email, role):
    service = build("drive", "v3", credentials=creds)
    permission = {
        "type": "user",
        "role": role,
        "emailAddress": email,
    }
    return service.permissions().create(
        fileId=document_id,
        body=permission,
        fields="id",
        sendNotificationEmail=True,
    ).execute()


def list_documents(creds):
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.document'",
        fields="nextPageToken, files(id, name)",
    ).execute()
    return results.get("files", [])


def get_document(creds, document_id):
    service = build("docs", "v1", credentials=creds)
    return service.documents().get(documentId=document_id).execute()


def delete_document(creds, document_id):
    service = build("drive", "v3", credentials=creds)
    service.files().delete(fileId=document_id).execute()


def _max_end_index(document):
    max_end = 1
    content = document.get("body", {}).get("content", [])
    for element in content:
        end_index = element.get("endIndex")
        if isinstance(end_index, int):
            max_end = max(max_end, end_index)
    return max_end


def _extract_plain_text(document):
    chunks = []
    for structural_element in document.get("body", {}).get("content", []):
        if "paragraph" not in structural_element:
            continue
        for paragraph_element in structural_element["paragraph"].get("elements", []):
            text_run = paragraph_element.get("textRun")
            if text_run and "content" in text_run:
                chunks.append(text_run["content"])
    return "".join(chunks)


def get_document_summary(creds, document_id):
    document = get_document(creds, document_id)
    return {
        "title": document.get("title"),
        "document_id": document.get("documentId"),
        "content": _extract_plain_text(document),
    }


def render_content(title, content, output_format):
    if output_format == "markdown":
        safe_title = title or "Untitled Document"
        rendered_content = content.rstrip("\n")
        if rendered_content:
            return f"# {safe_title}\n\n{rendered_content}\n"
        return f"# {safe_title}\n"

    return content


def append_text(creds, document_id, text):
    service = build("docs", "v1", credentials=creds)
    document = service.documents().get(documentId=document_id, fields="body(content)").execute()
    insertion_index = max(1, _max_end_index(document) - 1)

    requests = [
        {
            "insertText": {
                "location": {"index": insertion_index},
                "text": text + "\n",
            }
        }
    ]
    service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests},
    ).execute()


def set_text(creds, document_id, text):
    service = build("docs", "v1", credentials=creds)
    document = service.documents().get(documentId=document_id, fields="body(content)").execute()
    end_index = _max_end_index(document)

    requests = []
    if end_index > 2:
        requests.append(
            {
                "deleteContentRange": {
                    "range": {
                        "startIndex": 1,
                        "endIndex": end_index - 1,
                    }
                }
            }
        )

    if text:
        requests.append(
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": text,
                }
            }
        )

    if requests:
        service.documents().batchUpdate(
            documentId=document_id,
            body={"requests": requests},
        ).execute()
