import sqlite3

from bot import slack_app, sheets_data

@slack_app.command("/register")
def register_command(ack, client, body, command, respond, context):
    """
    Provide a flow to register a Slack account to a name
    """
    ack()

    user_slack_id = context.user_id

    # Connect to SQL Database
    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()

    # Find user in database
    registered_name = cur.execute("SELECT name, slack_id FROM slack_id sid WHERE sid.slack_id = \"" + user_slack_id+"\"").fetchone()

    # User registered already registered
    if registered_name is not None:
        respond("You are already registered as "+registered_name[0])
        con.close()
    # User not registered
    else:
        # Get the current slack connections
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

        # Open the view
        client.views_open(trigger_id=body["trigger_id"], view={
            "type": "modal",
            "callback_id": "slash-register-finish",
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

@slack_app.view("slash-register-finish")
def register_submitted(ack, body, client, view, say, context, respond):
    """
    Send the user a DM when they have successfully registered their account
    """
    ack()

    registration_block_id = view['blocks'][0]['block_id']
    matched_name = view['state']['values'][registration_block_id]['registration-block']['selected_option']['value']

    user_slack_id = context.user_id

    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO slack_id(slack_id, name) VALUES ('" + user_slack_id + "', '" + matched_name + "')")
    con.commit()
    con.close()

    # respond("You are now registered as "+matched_name+".")
    say(channel=user_slack_id, text="Your Slack account is now tied to the name " + matched_name + ". If you are an Assistant House Manager, you can now sign off jobs. You will also receive reminders to complete your house jobs.")