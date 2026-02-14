from googleapiclient.discovery import build


FORM_MIME_TYPE = "application/vnd.google-apps.form"


def create_form(creds, title):
    service = build("forms", "v1", credentials=creds)
    return service.forms().create(
        body={"info": {"title": title}},
    ).execute()


def list_forms(creds):
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(
        q=f"mimeType='{FORM_MIME_TYPE}'",
        fields="nextPageToken, files(id, name)",
    ).execute()
    return results.get("files", [])


def _question_payload(question_type, options):
    if question_type == "text":
        return {"textQuestion": {"paragraph": False}}

    if question_type == "paragraph":
        return {"textQuestion": {"paragraph": True}}

    if question_type == "choice":
        if not options:
            raise ValueError("--options is required for choice questions.")
        return {
            "choiceQuestion": {
                "type": "RADIO",
                "options": [{"value": option} for option in options],
                "shuffle": False,
            }
        }

    raise ValueError(f"Unsupported question type: {question_type}")


def add_question(creds, form_id, question_type, title, options=None):
    service = build("forms", "v1", credentials=creds)
    form = service.forms().get(formId=form_id).execute()
    item_index = len(form.get("items", []))

    request = {
        "createItem": {
            "item": {
                "title": title,
                "questionItem": {
                    "question": _question_payload(question_type, options),
                },
            },
            "location": {
                "index": item_index,
            },
        }
    }

    return service.forms().batchUpdate(
        formId=form_id,
        body={"requests": [request]},
    ).execute()


def get_responses(creds, form_id):
    service = build("forms", "v1", credentials=creds)
    return service.forms().responses().list(formId=form_id).execute()


def extract_answer_values(answer):
    text_answers = answer.get("textAnswers", {}).get("answers", [])
    return [item.get("value", "") for item in text_answers if "value" in item]

