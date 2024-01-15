import sqlite3

from bot import slack_app, sheets_data

@slack_app.command("/unregister")
def register_command(ack, client, body, command, respond, context):
    """
    Provide a flow to register a Slack account to a name
    """
    ack()

    user_slack_id = context.user_id

    # Connect to SQL Database
    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()

    # See if user is registered
    registered_name = cur.execute("SELECT name, slack_id FROM slack_id sid WHERE sid.slack_id = \"" + user_slack_id+"\"").fetchone()

    # User is not registered 
    if registered_name is None:
        respond("You are not registered")
        con.close()
    # User is registered
    else:
        cur.execute("DELETE FROM slack_id WHERE slack_id = \"" + user_slack_id+"\"")
        con.commit()
        con.close()

        respond("You are no longer registered as "+registered_name[0])