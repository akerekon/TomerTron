"""Module allowing access to os environment variables."""
import os

from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from waitress import serve

import TomerTron.sheets_helpers.command_flow as cf

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

#Provide a static class to handle all commands and events sent to TomerTron
command_flow = cf.CommandFlow()

@app.message("tomertron start")
def tomertron_start_command(say):
    """
    Listen for the start command "tomertron start"
    """
    command_flow.start_command(say=say)

@app.event("message")
def handle_message():
    """
    Ignore all messages besides the start command
    """

@app.action("signoff")
def signoff_flow(ack, body, client):
    """
    Begin the signoff process when the "signoff" button is clicked
    """
    ack()
    command_flow.signoff_command(body=body, client=client)

@app.action("reassign")
def reassign_flow(ack, body, client):
    """
    Begin the reassign process when the "reassign" button is clicked
    """
    ack()
    command_flow.reassign_command(body=body, client=client)
    

@app.action("unsignoff")
def unsignoff_flow(ack, body, client):
    """
    Begin the unsignoff process when the "unsignoff" button is clicked
    """
    ack()
    command_flow.unsignoff_command(body=body, client=client)


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
