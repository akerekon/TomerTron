import sqlite3

from bot import slack_app, sheets_data

@slack_app.action("register")
def register_flow(ack, body, client):
    """
    Provide a flow to register a Slack account to a name
    """
    ack()
    all_brothers = sheets_data.all_brothers()
    brother_blocks = []
    for brother in all_brothers:
        brother_blocks.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": brother,
                },
                "value": brother
            }
        )
    client.views_open(trigger_id=body["trigger_id"], view={
        "type": "modal",
        "callback_id": "registration-view",
        "title": {
            "type": "plain_text",
            "text": "What is your name?"
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
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select your name",
                        "emoji": True
                    },
                    "options": brother_blocks,
                    "action_id": "registration-block"
                },
                "label": {
                    "type": "plain_text",
                    "text": "What is your name?",
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

    registration_block_id = view['blocks'][0]['block_id']
    matched_name = view['state']['values'][registration_block_id]['registration-block']['selected_option']['value']
    user_slack_id = body['user']['id']

    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS slack_id(slack_id, name)")
    cur.execute("INSERT OR REPLACE INTO slack_id(slack_id, name) VALUES ('" + user_slack_id + "', '" + matched_name + "')")
    con.commit()
    con.close()

    say(channel=user_slack_id, text="Your Slack account is now tied to the name " + matched_name + ". If you are an Assistant House Manager, you can now sign off jobs. You will also receive reminders to complete your house jobs.")
