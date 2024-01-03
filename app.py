"""Module allowing access to os environment variables."""
import os
import sheets_helpers.SheetsData

from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from waitress import serve

#Load in environment variables using dotenv, from a .env file
#These secrets can be accessed by the current administrator of TomerTron via the Slack interface
load_dotenv()
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

#In production, TomerTron uses Flask (and waitress) as a webserver
#Reference https://slack.dev/bolt-python/concepts#adapters
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

#Provide a static access point for house jobs and points
sheets_data = sheets_helpers.SheetsData.SheetsData()

@app.message("signoff")
def message_hello(message, say):
    """
    Listen for messages containing the string "signoff"
    """
    sheets_data.load_jobs_and_points()
    say(sheets_data.job_data)
    say(sheets_data.point_data)

@app.event("message")
def handle_message():
    """
    Ignore all messages not containing the above strings
    """

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Pass all requests under the path /slack/events to the events above
    """
    return handler.handle(request)

if __name__ == "__main__":
    #In testing, run with Flask using "flask run -p 3000"
    #In production, serve our application using waitress using "python app.py"
    serve(flask_app, host=os.getenv("SERVER_IP"), port=os.getenv("SERVER_PORT"))
