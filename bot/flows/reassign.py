from bot import slack_app, sheets_data

@slack_app.action("reassign")
def reassign_flow(ack, body, client):
    """
    Begin the reassign process when the "reassign" button is clicked
    """
    ack()


# TODO: Present all (or only not done?) jobs
# TODO: Present brothers that can be assigned to the job (all but the currently assigned brother)
# TODO: Change person assigned