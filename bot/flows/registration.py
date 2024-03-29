import os
import sqlite3

from bot import slack_app, sheets_data

@slack_app.action("register")
def register_flow(ack, body, client, respond):
    """
    Provide a flow to register a Slack account to a name
    """
    ack()

    # Get the current slack connections
    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()
    slack_connections = cur.execute("SELECT name FROM slack_id").fetchall()
    con.close()

    # Make list of the names of brothers with a connected Slack
    brothers_with_slack = []
    for connection in slack_connections:
        brothers_with_slack.append(connection[0])

    # Make blocks for the non-registered brothers
    all_brothers = sheets_data.all_brothers()
    brother_blocks = []
    for brother in all_brothers:
        if brother not in brothers_with_slack:
            brother_blocks.append(
                {
                    "text": {
                        "type": "plain_text",
                        "text": brother,
                    },
                    "value": brother
                }
            )

    if not brother_blocks:
        respond("All accounts are registered!", replace_original=False)
    else:
        # Open the view
        client.views_open(trigger_id=body["trigger_id"], view={
            "type": "modal",
            "callback_id": "registration-view",
            "title": {
                "type": "plain_text",
                "text": "Register Account"
            },
            "submit": {
                "type": "plain_text",
                "text": "Confirm Registration"
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
                            "text": "Select name to register",
                            "emoji": True
                        },
                        "options": brother_blocks,
                        "action_id": "registration-block"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Who are you registering?",
                    }
                },
                {
                        "type": "input",
                        "element": {
                            "type": "users_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select Slack account to register"
                            },
                            "action_id": "slack-id-select"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Which Slack account is tied to this name?"
                        }
                    }
            ]
        })

@slack_app.view("registration-view")
def register_submitted(ack, body, client, view, say):
    """
    Send the user a DM when they have successfully registered their account
    """
    ack()

    name_block_id = view['blocks'][0]['block_id']
    slack_block_id = view['blocks'][1]['block_id']
    matched_name = view['state']['values'][name_block_id]['registration-block']['selected_option']['value']
    user_slack_id = view['state']['values'][slack_block_id]['slack-id-select']['selected_user']

    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO slack_id(slack_id, name) VALUES ('" + user_slack_id + "', '" + matched_name + "')")
    con.commit()
    con.close()

    say(channel=os.getenv("CHANNEL_ID"), text="Registered " + matched_name + " to the account " + user_slack_id)
    say(channel=user_slack_id, text="Your Slack account is now tied to the name " + matched_name + ". If you are an Assistant House Manager, you can now sign off jobs. You will also receive reminders to complete your house jobs.")
