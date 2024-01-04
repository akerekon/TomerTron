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
        input_name = view['state']['values']['b/p6s']['signoff-name']['value']
        matched_name = self.sheets_data.match_closest_name(input_name)
        jobs = self.sheets_data.get_jobs_by_name(matched_name)
        job_json_builder = ""
        for index, job in enumerate(jobs):
            day = job[2]
            where = job[1]
            what = job[0]
            if index != 0:
                job_json_builder += ","
            job_json_builder += """{"text": { "type": "plain_text", "text": """
            job_json_builder += '"' + day + " at " + where + " -- " + what + '"'
            job_json_builder += """}, "value":"""
            job_json_builder += '"job-' + str(index) + '" }'

        success_view = """{
            "type": "modal",
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
                        "text": "Signing off """ + matched_name + '"' + """
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "radio_buttons",
                            "options": [
                                """ + job_json_builder + """
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
        }"""
        print(success_view)
        ack(response_action="update", view=json.loads(success_view))

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
