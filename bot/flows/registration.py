import sqlite3

from bot import slack_app, sheets_data

@slack_app.action("register")
def register_flow(ack, body, client):
    """
    Provide a flow to register a Slack account to a name
    """
    # TODO: Only show brothers that have not been registered yet
    # TODO: Allow a brother to disassociate their slack (new slack account, they screw up registration, the bot messes up, etc.)

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
            },
            {
                "type": "actions",
                "block_id": "other-user-block",
                "elements": [
                    {
                        "type": "checkboxes",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Are you registering someone else?"
                                },
                                "value": "other"
                            }
                        ],
                        "action_id": "other-user"
                    }
                ]
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
    other_user_checkbox = view["state"]["values"]["other-user-block"]["other-user"]['selected_options']
    is_other_user = False

    for option in other_user_checkbox:
        if (option['value'] == "other"):
            is_other_user = True
    
    if is_other_user:
        select_other_user_view = {
            "callback_id": "other-user-confirm",
            "title": {
                "type": "plain_text",
                "text": "Register Someone Else"
            },
            "submit": {
                "type": "plain_text",
                "text": "Register"
            },
            "type": "modal",
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Which account matches " + matched_name + "?"
                    },
                    "accessory": {
                        "type": "users_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Accounts"
                        },
                        "action_id": "other-user-select"
                    }
                }
            ]
        }
        ack(response_action="update", view=select_other_user_view)
    else:
        user_slack_id = body['user']['id']

        con = sqlite3.connect("find_name_from_slack_id.db")
        cur = con.cursor()
        cur.execute("INSERT OR REPLACE INTO slack_id(slack_id, name) VALUES ('" + user_slack_id + "', '" + matched_name + "')")
        con.commit()
        con.close()

        say(channel=user_slack_id, text="Your Slack account is now tied to the name " + matched_name + ". If you are an Assistant House Manager, you can now sign off jobs. You will also receive reminders to complete your house jobs.")

@slack_app.action("other-user-select")
def register_other_user_select(ack):
    """
    Acknowledge, but do not take any action when clicking the register another user checkbox
    """
    ack()
@slack_app.action("other-user-confirm")
def register_other_user_confirm(ack, body, view, say):
    ack()
    print(view)
    print(body)
