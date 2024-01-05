"""
command_flow is a module to house CommandFlow below
"""
import json

from sheets_helpers.sheets_data import SheetsData # pylint: disable=import-error disable=no-name-in-module

class CommandFlow:
    """
    Provide a static class to handle commands and events sent to TomerTron
    """

    #Provide a static class to access house job and point data
    sheets_data = SheetsData()

    #Specify which channel TomerTron should send messages to
    channel_id = ""

    last_bot_timestamp = ""

    def start_command(self, say, needs_channel=False):
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
		}
	    ]
        if needs_channel:
            result = say(channel=self.channel_id, blocks=blocks, text="What would you like to do?")
        else:
            result = say(blocks=blocks, text="What would you like to do?")
        self.channel_id = result["channel"]
        self.last_bot_timestamp = result["ts"]

    def signoff_command(self, ack, body, client):
        """
        Provide a flow to signoff a housejob, opening new views as needed
        """
        ack()

        # Build the list of brothers to select from
        available = self.sheets_data.available_signoffs()
        brother_blocks = []
        for brother in available:
            brother_blocks.append(
                {
                    "text": {
                        "type": "plain_text",
                        "text": brother + (f" ({available[brother]})" if available[brother] is not None else ""),
                        "emoji": True
                    },
                    "value": brother
                }
            )
        
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
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a brother/postulant",
                    },
                    "options": brother_blocks,
                    "action_id": "signoff-block"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Who are you signing off?"
                }
            }
        ]
    }
    )
        
    def signoff_name_submitted(self, ack, body, client, view):
        """
        Provide a view for matching jobs when a name has been matched
        """
        signoff_block_id = view['blocks'][0]['block_id']
        matched_name = view['state']['values'][signoff_block_id]['signoff-block']['selected_option']['value']
        jobs = self.sheets_data.get_jobs_by_name(matched_name)

        if len(jobs) == 0:
            failure_view = {
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": "No Jobs Found!"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": matched_name + " does not have any jobs assigned. Check if the bot picked the wrong person, or if this person swapped with someone else."
                        }
                    }
                ]
            }
            ack(response_action="update", view=failure_view)
        else:
            job_json_builder = []
            for index, job in enumerate(jobs):
                day = job[2]
                where = job[1]
                what = job[0]

                job_json_builder.append({
                    "text": {
                        "type": "plain_text",
                        "text": f"{day} {where} -- {what}"
                    },
                    "value": f"job-{str(index)}"
                })

            success_view = {
                "type": "modal",
                "callback_id": "signoff-confirm",
                "title": {
                    "type": "plain_text",
                    "text": "Which job is this?"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Confirm Signoff"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": f"Signing off {matched_name}"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "radio_buttons",
                                "options": job_json_builder,
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

    def signoff_confirm(self, ack, body, client, view, say):
        ack()

        signedoff_name = " ".join(body["view"]["blocks"][0]["text"]["text"].split(" ")[2:])
        signedoffby_name = body["user"]["username"]
        job_block_id = body["view"]["blocks"][1]["block_id"]
        job = view["state"]["values"][job_block_id]["job-option"]["selected_option"]
        job_id = view["state"]["values"][job_block_id]["job-option"]["selected_option"]["value"].split("-")[1]

        self.sheets_data.signoff_job(signedoff_name, signedoffby_name, job_id)

        say(channel=self.channel_id, text="<@"+ signedoffby_name +"> signed off " + signedoff_name + " for " + job['text']['text'])
        client.chat_delete(channel=self.channel_id, ts=self.last_bot_timestamp)
        self.start_command(say, True)

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
    def register_command(self, ack, body, client):
        """
        Provide a flow to register a Slack account to a name
        """
        ack()
        all_brothers = self.sheets_data.all_brothers()
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
