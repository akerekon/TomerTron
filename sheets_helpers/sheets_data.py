"""
sheets_data is a module used to house SheetsData below
"""

import sys
import os.path
import Levenshtein

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsData:
    """
    Provide a static class that will hold data about jobs and points and make API calls
    """
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    SPREADSHEET_ID = "1EPY4FXw_K87VMz0MpMEFh5JWgdLMilBnudYXqhMr2-g"
    JOB_RANGE = "AllJobs"
    POINT_RANGE = "PointRange"

    job_data = []
    point_data = []

    def _get_spreadsheet(self):
        """
        Get the house job points spreadsheet using our access credentials
        As needed, if credentials have expired, reauthenticate
        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w", encoding="utf-8") as token:
                token.write(creds.to_json())
        try:
            service = build("sheets", "v4", credentials=creds)
            return service.spreadsheets() # pylint: disable=no-member
        except HttpError as err:
            print(err)

    def _load_jobs_and_points(self):
        """
        Load in data for house jobs and points from the spreadsheet
        """
        sheet = self._get_spreadsheet()
        self.job_data = (
            sheet.values()
            .get(spreadsheetId=self.SPREADSHEET_ID, range=self.JOB_RANGE)
            .execute()
        )

        self.point_data = (
            sheet.values()
            .get(spreadsheetId=self.SPREADSHEET_ID, range=self.POINT_RANGE)
            .execute()
        )

    def _save_jobs_and_points(self):
        """
        Save data for house jobs and points to the spreadsheet
        """
        sheet = self._get_spreadsheet()
        sheet.values().update(spreadsheetId=self.SPREADSHEET_ID, range=self.JOB_RANGE, body=self.job_data).execute()
        sheet.values().update(spreadsheetId=self.SPREADSHEET_ID, range=self.POINT_RANGE, body=self.point_data).execute()
    
    def match_closest_name(self, input_string):
        self._load_jobs_and_points()
        points = self.point_data.get("values", [])

        best_match_count = sys.maxsize
        best_match = ""

        if " " in input_string:
            for row in points[1:]:
                if len(row) > 0:
                    if Levenshtein.distance(input_string, row[0]) < best_match_count:
                        best_match_count = Levenshtein.distance(input_string, row[0])
                        best_match = row[0]
        else:
            for row in points[1:]:
                if len(row) > 0:
                    first_name = row[0].split(" ")[0]
                    last_name = row[0].split(" ")[1]
                    if Levenshtein.distance(input_string, first_name) < Levenshtein.distance(input_string, last_name):
                        if Levenshtein.distance(input_string, first_name) < best_match_count:
                            best_match_count = Levenshtein.distance(input_string, first_name)
                            best_match = row[0]
                    else:
                        if Levenshtein.distance(input_string, last_name) < best_match_count:
                            best_match_count = Levenshtein.distance(input_string, last_name)
                            best_match = row[0]
        return best_match
