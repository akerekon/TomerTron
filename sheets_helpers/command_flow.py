"""
command_flow is a module to house CommandFlow below
"""

from sheets_helpers.sheets_data import SheetsData # pylint: disable=import-error disable=no-name-in-module

class CommandFlow:
    """
    Provide a static class to handle commands and events sent to TomerTron
    """

    #Provide a static class to access house job and point data
    sheets_data = SheetsData()

    def start_command(self, say):
        """
        Provide an interface for a user to select to...
          signoff a house job
          reassign a house job
          unsignoff a house job
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

    def signoff_command(self, ack, body, client):
        """
        Provide a flow to signoff a housejob, opening new views as needed
        """
        ack()
        client.views_open(trigger_id=body["trigger_id"], view={
        "type": "modal",
        "callback_id": "signoff-name-view",
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
    def signoff_name_submitted(self, ack, body, client, view):
        print(str(view))
        print(str(body))
        print(str(client))
        success_view = {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Which job is this?"
            },
            "submit": {
                "type": "plain_text",
                "text": "Confirm Signoff",
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "Signing off <person>"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "radio_buttons",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Tuesday at 8 -- 1st Floor Bathroom"
                                    },
                                    "value": "job-0"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Thursday at Mack's -- 1st Floor Bathroom"
                                    },
                                    "value": "job-1"
                                }
                            ],
                            "action_id": "job-option"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "If none of the above jobs apply, verify if they've swapped with someone. If so, reassign this job first."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "checkboxes",
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Is this job late?"
                                    },
                                    "value": "late"
                                }
                            ],
                            "action_id": "job-late"
                        }
                    ]
                }
            ]
        }
        ack(response_action="update", view=success_view)

    def reassign_command(self, ack, body, client):
        """
        Provide a flow to reassign a housejob, opening new views as needed
        """
        ack()
    def unsignoff_command(self, ack, body, client):
        """
        Provide a flow to unsignoff a housejob, opening new views as needed
        """
        ack()
