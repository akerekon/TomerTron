"""
app.py is the main module, used to receive incoming Slack requests
"""

import os

from dotenv import load_dotenv
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from waitress import serve

from flow.command_flow import CommandFlow # pylint: disable=import-error disable=no-name-in-module

#Load in environment variables using dotenv, from a .env file
#These secrets can be accessed by the current administrator of TomerTron via the Slack interface
load_dotenv()
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
    raise_error_for_unhandled_request=True
)

#In production, TomerTron uses Flask (and waitress) as a webserver
#Reference https://slack.dev/bolt-python/concepts#adapters
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

#Provide a static class to handle all commands and events sent to TomerTron
command_flow = CommandFlow()

@app.message(os.getenv("APP_NAME") + " start")
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
    command_flow.signoff_begin(ack=ack, body=body, client=client)

@app.view("signoff-name-view")
def signoff_show_jobs(ack, body, client, view):
    command_flow.signoff_show_jobs(ack=ack, body=body, client=client, view=view)

@app.view("signoff-confirm")
def signoff_confirm(ack, body, client, view, say):
    command_flow.signoff_confirm(ack=ack, body=body, client=client, view=view, say=say)

@app.action("job-option")
def job_selected(ack):
    """
    Acknowledge, but do not take any action when a job is selected
    """
    ack()

@app.action("reassign")
def reassign_flow(ack, body, client):
    """
    Begin the reassign process when the "reassign" button is clicked
    """
    command_flow.reassign_command(ack=ack, body=body, client=client)
    

@app.action("unsignoff")
def unsignoff_flow(ack, body, client):
    """
    Begin the unsignoff process when the "unsignoff" button is clicked
    """
    command_flow.unsignoff_command(ack=ack, body=body, client=client)

@app.action("register")
def register_flow(ack, body, client):
    """
    Begin the Slack account registration process when the "register" button is clicked
    """
    command_flow.register_command(ack=ack, body=body, client=client)

@app.command("/tomertron")
def register_command(ack, body, client):
    """
    Begin the Slack account registration process when the "tomertron" command is sent
    """
    command_flow.register_command(ack=ack, body=body, client=client)

@app.view("registration-view")
def register_submitted(ack, body, client, view, say):
    """
    Send the user a DM when they have successfully registered their account
    """
    command_flow.register_submitted(ack=ack, body=body, client=client, view=view, say=say)

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
