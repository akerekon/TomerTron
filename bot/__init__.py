"""
app.py is the main module, used to receive incoming Slack requests
"""

import os

from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

from bot.sheets_data import SheetsData

#Load in environment variables using dotenv, from a .env file
#These secrets can be accessed by the current administrator of TomerTron via the Slack interface
load_dotenv()
slack_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
    raise_error_for_unhandled_request=True
)

#In production, TomerTron uses Flask (and waitress) as a webserver
#Reference https://slack.dev/bolt-python/concepts#adapters
flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

#Provide a static class to access data from the Google Sheet
sheets_data = SheetsData()
#Specify which channel TomerTron should send messages to
channel_id = ""
last_bot_timestamp = ""

import bot.flows.start
import bot.flows.signoff
import bot.flows.unsignoff
import bot.flows.reassign

@slack_app.event("message")
def handle_message():
    """
    Ignore all messages besides the start command
    """


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Pass all requests under the path /slack/events to the events above
    """
    return handler.handle(request)
