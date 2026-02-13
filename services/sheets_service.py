import json

from googleapiclient.discovery import build


def create_spreadsheet(creds, title):
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets().create(
        body={"properties": {"title": title}},
        fields="spreadsheetId,spreadsheetUrl,properties.title",
    ).execute()


def list_spreadsheets(creds):
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        fields="nextPageToken, files(id, name)",
    ).execute()
    return results.get("files", [])


def read_values(creds, spreadsheet_id, cell_range):
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=cell_range,
    ).execute()


def _parse_plain_data(data):
    if ";" in data:
        rows = []
        for row in data.split(";"):
            rows.append([cell.strip() for cell in row.split(",")])
        return rows

    if "," in data:
        return [[cell.strip() for cell in data.split(",")]]

    return [[data]]


def parse_input_data(data):
    stripped_data = data.strip()
    if stripped_data.startswith("["):
        parsed = json.loads(stripped_data)
        if not isinstance(parsed, list):
            raise ValueError("JSON data must be a list or list of lists.")
        if parsed and not isinstance(parsed[0], list):
            return [parsed]
        return parsed

    return _parse_plain_data(data)


def write_values(
    creds,
    spreadsheet_id,
    cell_range,
    values,
    major_dimension="ROWS",
    value_input_option="RAW",
):
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=cell_range,
        valueInputOption=value_input_option,
        body={
            "majorDimension": major_dimension,
            "values": values,
        },
    ).execute()


def clear_values(creds, spreadsheet_id, cell_range):
    service = build("sheets", "v4", credentials=creds)
    return service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=cell_range,
        body={},
    ).execute()

