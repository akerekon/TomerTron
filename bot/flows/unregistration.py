import sqlite3
import os

from bot import slack_app, sheets_data

@slack_app.action("unregister")
def unregister_flow(ack, body, client):
    """
    Provide a flow to unregister a user
    """
    ack()

    # Get the current slack connections
    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()
    slack_connections = cur.execute("SELECT name FROM slack_id").fetchall()
    con.close()

    # Make list of the names of brothers with a connected Slack
    brother_blocks = []
    for connection in slack_connections:
        brother_blocks.append(
                {
                    "text": {
                        "type": "plain_text",
                        "text": connection[0],
                    },
                    "value": connection[0]
                }
            )
            

    # Open the view
    client.views_open(trigger_id=body["trigger_id"], view={
        "type": "modal",
        "callback_id": "unregistration-view",
        "title": {
            "type": "plain_text",
            "text": "Unregister Account"
        },
        "submit": {
            "type": "plain_text",
            "text": "Confirm Unregistration"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "element": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select name to unregister",
                        "emoji": True
                    },
                    "options": brother_blocks,
                    "action_id": "unregistration-block"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Who are you unregistering?",
                }
            },
        ]
    })
@slack_app.view("unregistration-view")
def unregister_submitted(ack, view, say):
    """
    Confirm a user has been unregistered
    """
    ack()

    name_block_id = view['blocks'][0]['block_id']
    matched_name = view['state']['values'][name_block_id]['unregistration-block']['selected_option']['value']

    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()
    cur.execute("DELETE FROM slack_id WHERE name LIKE %" + matched_name + "%")
    con.commit()
    con.close()

    say(channel=os.getenv("CHANNEL_ID"), text="Successfully unregistered " + matched_name)