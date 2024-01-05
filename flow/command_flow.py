"""
command_flow is a module to house CommandFlow below
"""
import reassign_flow
import register_flow
import signoff_flow
import unsignoff_flow

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

    def signoff_begin(self, ack, body, client):
        signoff_flow.signoff_begin(self.sheets_data, ack, body, client)

    def signoff_show_jobs(self, ack, view):
        signoff_flow.signoff_show_jobs(self.sheets_data, ack, view)

    def signoff_confirm(self, ack, body, client, view, say):
        signoff_flow.signoff_confirm(self.sheets_data, self.channel_id, self.last_bot_timestamp, ack, body, client, view, say)
        self.start_command(say, needs_channel=True)

    def unsignoff_command(self, ack, body, client):
        unsignoff_flow.unsignoff_command(ack, body, client)

    def reassign_command(self, ack, body, client):
        reassign_flow.reassign_command(ack, body, client)

    def register_command(self, ack, body, client):
        register_flow.register_command(self.sheets_data, ack, body, client)

    def register_submitted(self, ack, body, view, say):
        register_flow.register_submitted(ack, body, view, say)

    def start_command(self, say, needs_channel=False):
        """
        Provide an interface for a user to select to...
          signoff a house job
          reassign a house job
          unsignoff a house job
          register their Slack account
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
    
