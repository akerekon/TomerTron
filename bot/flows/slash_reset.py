from bot import slack_app, sheets_data

@slack_app.command("/reset")
def register_command(ack, client, body, command, respond, context):
    """
    Provide a flow to reset points for the week and schedule reminders
    """
    ack()
    sheets_data.reset_points()
    respond("Reset points and scheduled reminders for this week!", replace_original=False)