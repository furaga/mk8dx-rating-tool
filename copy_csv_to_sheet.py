import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def read_csv_file(file_path):
    data = []
    with open(file_path, "r", encoding="utf8") as f:
        for line_i, line in enumerate(f.readlines()):
            d = [t.strip() for t in line.split(",")]
            if line_i >= 1:
                d = [t if i <= 2 else int(t) for i, t in enumerate(d)]
                print(d)
            data.append([t.strip() for t in line.split(",")])
    return data


def copy_csv_data_to_google_sheet(sheet_id, sheet_range, data, credentials_file):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("sheets", "v4", credentials=creds)

        body = {"values": data}

        request = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=sheet_id,
                range=sheet_range,
                valueInputOption="USER_ENTERED",
                body=body,
            )
        )
        response = request.execute()

        print(f'{response.get("updatedCells")} cells updated.')

    except HttpError as error:
        print(f"An error occurred: {error}")
        response = None

    return response


if __name__ == "__main__":
    # Replace with your own values
    CSV_FILE_PATH = "out.csv"
    SHEET_ID = "1Mu9AMnnkw6fFvxUlTN5JsspKSLxWbYAXCUpmfePdgqU"
    SHEET_RANGE = "シート1"  # Update the sheet name and range if needed
    CREDENTIALS_FILE = r"C:\Users\furag\Documents\data\google_api\client_secret_1088977421046-92c2t7g6ur1gdb9tasp1j0p3o17pvodj.apps.googleusercontent.com.json"

    csv_data = read_csv_file(CSV_FILE_PATH)
    copy_csv_data_to_google_sheet(SHEET_ID, SHEET_RANGE, csv_data, CREDENTIALS_FILE)
