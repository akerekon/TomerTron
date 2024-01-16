"""
sheets_data is a module used to house SheetsData below
"""

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsData:
    """
    Provide a static class that will hold data about jobs and points and make API calls
    """
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    SPREADSHEET_ID = "1EPY4FXw_K87VMz0MpMEFh5JWgdLMilBnudYXqhMr2-g"

    JOB_RANGE = "House_Jobs!A2:G256"
    POINT_RANGE = "Week_Scores!A1:F256"
    NICKNAME_RANGE = "Nicknames"

    signoff_points = 2
    signoff_ho_man_points = 0.1
    signoff_not_done_name = "E-SIGNOFF"

    job_data = []
    point_data = []
    nickname_data = []

    def refresh_token(self):
        self._get_spreadsheet()

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
        sheet.values().update(spreadsheetId=self.SPREADSHEET_ID, range=self.JOB_RANGE, body=self.job_data, valueInputOption="USER_ENTERED").execute()
        sheet.values().update(spreadsheetId=self.SPREADSHEET_ID, range=self.POINT_RANGE, body=self.point_data, valueInputOption="USER_ENTERED").execute()
    
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
    
    def signoff_job(self, signedoff_name, signedoffby_name, job_id, is_late):
        self._load_jobs_and_points()

        # Update jobs
        jobs = self.get_jobs_by_name(signedoff_name)
        job = jobs[int(job_id)]
        job[4] = signedoffby_name

        # Update scores
        points = self.point_data.get("values", [])
        for row in points:
            if row[0] == signedoff_name: # Update signoff
                row[1] = float(row[1]) + self.signoff_points
            if row [0] == signedoffby_name: # Update ass ho
                row[2] = float(row[2]) + self.signoff_ho_man_points

        # Is late
        job[5] = "y" if is_late else "n"

        self._save_jobs_and_points()

    def unsignoff_job(self, unsignedoff_name, unsignedoffby_name, job_id):
        self._load_jobs_and_points()

        # Get job
        jobs = self.get_jobs_by_name(unsignedoff_name)
        job = jobs[int(job_id)]

        # Update scores
        points = self.point_data.get("values", [])
        for row in points:
            if row[0] == unsignedoff_name: # Update signoff
                row[1] = float(row[1]) - self.signoff_points
            if row [0] == job[4]: # Update ass ho
                row[2] = float(row[2]) - self.signoff_ho_man_points

        # Update lateness
        job[5] = "n"

        # Update job sheet
        job[4] = self.signoff_not_done_name
        self._save_jobs_and_points()
    
    def all_brothers(self):
        self._load_jobs_and_points()
        points = self.point_data.get("values", [])
        brother_names = []
        for row in points[1:]:
            if len(row) > 0:
                brother_names.append(row[0])
        return brother_names
    
    def all_brothers_with_nicknames(self):
        """
        Gets all of the brothers currently with a job and gets their nicknames
        """
        brother_names = {}

        self._load_jobs_and_points()
        points = self.point_data.get("values", [])
        nicknames = self.nickname_data.get("values", [])

        for row in points[1:]:
            if len(row) > 0:
                brother_names[row[0]] = None
                
        for row in nicknames:
            if row[0] in brother_names:
                brother_names[row[0]] = row[1]

        return dict(sorted(brother_names.items()))

    def available_signoffs(self, unsignoff=False):
        """
        Gets all of the brothers currently with a job and gets their nicknames
        """
        available = {}

        self._load_jobs_and_points()
        jobs = self.job_data.get("values", [])
        nicknames = self.nickname_data.get("values", [])

        for row in jobs:
            if len(row) > 4 and (row[4] == self.signoff_not_done_name) ^ unsignoff:
                available[row[3]] = None
                
        for row in nicknames:
            if row[0] in available:
                available[row[0]] = row[1]

        return dict(sorted(available.items()))
    
    def reset_points(self):
        self._load_jobs_and_points()
        jobs = self.job_data.get("values", [])
        points = self.point_data.get("values", [])

        for job_row in jobs:
            if len(job_row) > 0:
                user_name = job_row[3]
                for point_row in points[1:]:
                    if len(point_row) > 0:
                        if point_row[0] == user_name:
                            point_row[1] = float(point_row[1]) - 1.0
                            break
        for point_row in points[1:]:
            if len(point_row) > 0:
                point_row[2] = float(0.0)
        self._save_jobs_and_points()


    def get_available_jobs(self):
        """
        Gets all of the current, non signed off jobs
        """
        self._load_jobs_and_points()
        jobs = self.job_data.get("values", [])

        matching_jobs = []
        for row in jobs:
            if len(row) > 4 and (row[4] == self.signoff_not_done_name):
                    matching_jobs.append(row)
        return matching_jobs

    def swap_job(self, swapped_name, job_id):
        self._load_jobs_and_points()

        # Update jobs
        jobs = self.get_available_jobs()
        job = jobs[int(job_id)]
        job[3] = swapped_name

        self._save_jobs_and_points()