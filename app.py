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

@app.message("tomertron start")
def tomertron_start_command(say):
    """
    Listen for the start command "tomertron start"
    """
    blocks = [
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "What would you like to do?"
			}
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Signoff a House Job"
					},
					"action_id": "signoff"
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Reassign a House Job"
					},
					"action_id": "reassign"
				}
			]
		},
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Unsignoff a House Job"
					},
					"action_id": "unsignoff"
				}
			]
		}
	]
    say(blocks=blocks, text="What would you like to do?")

@app.event("message")
def handle_message():
    """
    Ignore all messages besides the start command
    """

@app.action("signoff")
def signoff_flow(body, ack, client):
    """
    Begin the signoff process when the "signoff" button is clicked
    """
    ack()
    client.views_open(trigger_id=body["trigger_id"], view={
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Signoff a House Job"
        },
        "submit": {
            "type": "plain_text",
            "text": "Confirm Name"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "signoff-name"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Who are you signing off?",
                }
            }
	    ]}
    )

@app.action("reassign")
def reassign_flow(body, ack, say):
    """
    Begin the reassign process when the "reassign" button is clicked
    """
    ack()
    say(f"<@{body['user']['id']}> Sent a reassign request")

@app.action("unsignoff")
def unsignoff_flow(body, ack, say):
    """
    Begin the unsignoff process when the "unsignoff" button is clicked
    """
    ack()
    say(f"<@{body['user']['id']}> Sent an unsignoff request")


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
