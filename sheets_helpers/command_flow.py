"""
command_flow is a module to house CommandFlow below
"""

from sheets_data import SheetsData

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

    def signoff_command(self, body, client):
        """
        Provide a flow to signoff a housejob, opening new views as needed
        """
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
    def reassign_command(self, body, client):
        """
        Provide a flow to reassign a housejob, opening new views as needed
        """
    def unsignoff_command(self, body, client):
        """
        Provide a flow to unsignoff a housejob, opening new views as needed
        """
