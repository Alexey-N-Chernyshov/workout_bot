"""
Loads Google spreadsheets.
"""

from __future__ import print_function

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
GOOGLE_TOKEN_FILENAME = 'secrets/google_token.json'


def get_values(spreadsheet_id, pagename):
    """
    Reads google spreadsheet page in specific format.

    str spreadsheet_id -- is an id of the table, can be found in page http
    str pagename -- name of table page
    return spreadsheet cells merges and values
    """
    range_name = pagename + '!A:E'

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    google_token_file = Path(GOOGLE_TOKEN_FILENAME)
    if google_token_file.is_file():
        creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILENAME,
                                                      SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "secrets/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("secrets/google_token.json", 'w', encoding="utf-8") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        # get cell merges
        result_merges = sheet.get(spreadsheetId=spreadsheet_id,
                                  ranges=range_name,
                                  includeGridData=False).execute()

        # get values
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=range_name).execute()
        values = result.get("values", [])

        return (result_merges["properties"]["title"],
                result_merges["sheets"][0]["merges"], values[1:])

    except HttpError as err:
        print(err)
