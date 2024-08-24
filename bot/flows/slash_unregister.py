from bot import slack_app, sheets_data
from bot.utilities.database import Database

@slack_app.command("/unregister")
def register_command(ack, client, body, command, respond, context):
    """
    Provide a flow to register a Slack account to a name
    """
    ack()

    user_slack_id = context.user_id

    # See if user is registered
    db = Database()
    registered_name = db.get_name_from_slack_id(user_slack_id)

    # User is not registered 
    if registered_name is None:
        respond("You are not registered")
    # User is registered
    else:
        db.delete_connection(user_slack_id)
        respond("You are no longer registered as "+registered_name[0])
    db.close()