from bot import slack_app, sheets_data

@slack_app.action("unsignoff")
def unsignoff_flow(ack, body, client):
    """
    Begin the unsignoff process when the "unsignoff" button is clicked
    """
    ack()