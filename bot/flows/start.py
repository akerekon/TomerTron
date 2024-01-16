import os
from bot import slack_app, sheets_data

# Core routes
@slack_app.command("/" + os.getenv("APP_NAME"))
def tomertron_start_command(ack, command, respond, context):
    """
    Provide an interface for a user to select to...
        signoff a house job
        reassign a house job
        unsignoff a house job
    """
    ack()

    # Check if command is run in Ho-Man channel
    if context.channel_id != os.getenv("CHANNEL_ID"):
        respond("This is not the house manager channel!")
    else:
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
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Register Account"
                        },
                        "action_id": "register"
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
                            "text": "Unregister an Account"
                        },
                        "action_id": "unregister"
                    }
                ]
            }
        ]

        respond(blocks=blocks, text="What would you like to do?")
