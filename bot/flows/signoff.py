import sqlite3
import os

from bot import slack_app, sheets_data

@slack_app.action("signoff")
def signoff_flow(ack, body, client, respond):
    """
    Provide a flow to signoff a housejob, opening new views as needed
    """
    ack()

    # Build the list of brothers to select from
    available = sheets_data.available_signoffs()
    brother_blocks = []
    for brother in available:
        brother_blocks.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": brother + (f" ({available[brother]})" if available[brother] is not None else ""),
                },
                "value": brother
            }
        )

    # If there are no jobs to sign off notify the user!
    if len(brother_blocks) == 0:
        respond(text="There are no jobs that can be signed off!", replace_original=False)
    else:
    # Build the buttons
        client.views_open(trigger_id=body["trigger_id"], view={
            "type": "modal",
            "callback_id": "signoff-show-jobs",
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
        })

@slack_app.view("signoff-show-jobs")
def signoff_show_jobs(ack, body, client, view):
    """
    Provide a view for matching jobs when a name has been matched
    """
    signoff_block_id = view['blocks'][0]['block_id']
    matched_name = view['state']['values'][signoff_block_id]['signoff-block']['selected_option']['value']
    jobs = sheets_data.get_jobs_by_name(matched_name)

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

            if job[4] == "E-SIGNOFF":
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
                    "block_id": "job-block",
                    "elements": [
                        {
                            "type": "radio_buttons",
                            "options": job_json_builder,
                            "initial_option": job_json_builder[0],
                            "action_id": "signoff-job-option"
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
                    "block_id": "info-block",
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
                            "action_id": "signoff-job-checkboxes"
                        }
                    ]
                }
            ]
        }
        ack(response_action="update", view=success_view)

@slack_app.view("signoff-confirm")
def signoff_confirm(ack, body, client, view, say):
    ack()

    # Get signoff info
    signedoff_name = " ".join(body["view"]["blocks"][0]["text"]["text"].split(" ")[2:])
    signedoffby_id = body["user"]["id"]
    job = view["state"]["values"]["job-block"]["signoff-job-option"]["selected_option"]
    job_id = view["state"]["values"]["job-block"]["signoff-job-option"]["selected_option"]["value"].split("-")[1]

    # Get checkbox info
    job_checkboxes = view["state"]["values"]["info-block"]["signoff-job-checkboxes"]['selected_options']
    is_late = False

    for option in job_checkboxes:
        if (option['value'] == "late"):
            is_late = True

    # Send message
    con = sqlite3.connect("find_name_from_slack_id.db")
    cur = con.cursor()
    res = cur.execute("SELECT name FROM slack_id WHERE slack_id='" + signedoffby_id + "'")
    matched_name = res.fetchone()
    if matched_name is None:
        say(channel=os.getenv("CHANNEL_ID"), text="<@"+ signedoffby_id +">, please first register your account!")
    else:
        # Sign off the person
        sheets_data.signoff_job(signedoff_name, matched_name[0], job_id, is_late)
        say(channel=os.getenv("CHANNEL_ID"), text="<@"+ signedoffby_id +"> signed off " + signedoff_name + " for " + job['text']['text'])
    con.close()

@slack_app.action("signoff-job-option")
def signoff_job_option(ack):
    """
    Acknowledge, but do not take any action when a job is selected
    """
    ack()

@slack_app.action("signoff-job-checkboxes")
def signoff_job_checkboxes(ack):
    """
    Acknowledge, but do not take any action when a job is selected
    """
    ack()