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
    NICKNAME_RANGE = "Nicknames"

    job_data = []
    point_data = []
    nickname_data = []

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
        Refresh data for house jobs and points from the spreadsheet
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

        self.nickname_data = (
            sheet.values()
            .get(spreadsheetId=self.SPREADSHEET_ID, range=self.NICKNAME_RANGE)
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
        """
        Find the closest name against the list of names in the points spreadsheet
        
        First, refresh jobs and points
        If the input has a space, it is probably a full name, so compare against full names
        If not, it is either a firstname, lastname, or nickname, so compare against the minimum distance of each
        """
        self._load_jobs_and_points()
        points = self.point_data.get("values", [])

        best_match_distance = sys.maxsize
        best_match = ""

        if " " in input_string:
            for row in points[1:]:
                if len(row) > 0:
                    distance = Levenshtein.distance(input_string, row[0])
                    if distance < best_match_distance:
                        best_match_distance = distance
                        best_match = row[0]
        else:
            for row in points[1:]:
                if len(row) > 0:
                    first_name = row[0].split(" ")[0]
                    last_name = row[0].split(" ")[1]

                    first_name_distance = Levenshtein.distance(input_string, first_name)
                    last_name_distance = Levenshtein.distance(input_string, last_name)

                    if min(first_name_distance, last_name_distance) < best_match_distance:
                        best_match_distance = min(first_name_distance, last_name_distance)
                        best_match = row[0]
            #TODO -- compare against nicknames here
        return best_match
    
    def get_jobs_by_name(self, name):
        """
        Given a valid name, find a list of (preloaded) jobs for that name
        """
        jobs = self.job_data.get("values", [])
        matching_jobs = []
        for row in jobs:
            if len(row) > 0:
                if row[3] == name:
                    matching_jobs.append(row)
        return matching_jobs

    def available_signoffs(self):
        """
        Gets all of the brothers currently with a job and gets their nicknames
        """
        available = {};

        self._load_jobs_and_points()
        jobs = self.job_data.get("values", []);
        nicknames = self.nickname_data.get("values", []);

        for row in jobs:
            if len(row) > 3:
                available[row[3]] = None;
                
        for row in nicknames:
            if row[0] in available:
                available[row[0]] = row[1];

        return dict(sorted(available.items()));

