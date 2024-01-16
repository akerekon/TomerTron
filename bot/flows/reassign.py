import os
import sqlite3
from bot import slack_app, sheets_data

@slack_app.action("reassign")
def reassign_flow(ack, body, client, respond):
    """
    Begin the reassign process when the "reassign" button is clicked
    """
    ack()

    # Find available jobs
    jobs = sheets_data.get_available_jobs()

    job_blocks = []
    for index, job in enumerate(jobs):
        who = job[3]
        day = job[2]
        where = job[1]
        what = job[0]

        job_blocks.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": f"{who} -- {what} -- {day} @ {where}"
                },
                "value": f"{str(index)},{who},{what}"
            }
        )

    if len(jobs) == 0:
        respond(text="There are no jobs to reassign.", replace_original=False)
    else:
        # Get available brothers
        all_brothers = sheets_data.all_brothers_with_nicknames()
        brother_blocks = []
        for brother in all_brothers:
            brother_blocks.append(
                {
                    "text": {
                        "type": "plain_text",
                        "text": brother + (f" ({all_brothers[brother]})" if all_brothers[brother] is not None else ""),
                    },
                    "value": brother
                }
            )

        # Build the modal
        client.views_open(trigger_id=body["trigger_id"], view={
            "type": "modal",
            "callback_id": "reassign-submit",
            "title": {
                "type": "plain_text",
                "text": "Reassign a House Job"
            },
            "submit": {
                "type": "plain_text",
                "text": "Confirm Reassignment"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "job-block",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a job to reassign",
                        },
                        "options": job_blocks,
                        "action_id": "reassign-option-jobs"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Which job is being reassigned?"
                    }
                },
                {
                    "type": "input",
                    "block_id": "brother-block",
                    "element": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select a brother/postulant",
                        },
                        "options": brother_blocks,
                        "action_id": "reassign-option-brothers"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Who is taking this job?"
                    }
                }
            ]
        })

@slack_app.view("reassign-submit")
def reassign_submit(ack, body, client, view, say, context, payload):
    ack()

    print(view["state"]["values"]["job-block"]["reassign-option-jobs"]["selected_option"]["value"].split())
    print(view["state"]["values"]["brother-block"]["reassign-option-brothers"]["selected_option"]["value"])

    # Get signoff info
    selected_job = view["state"]["values"]["job-block"]["reassign-option-jobs"]["selected_option"]["value"].split(",")

    original_name = selected_job[1]
    swapped_name = view["state"]["values"]["brother-block"]["reassign-option-brothers"]["selected_option"]["value"]
    asshoman_id = context.user_id
    job = selected_job[2]
    job_id = selected_job[0]

    # Swap and send message
    sheets_data.swap_job(swapped_name, job_id)
    say(channel=os.getenv("CHANNEL_ID"), text=f"<@{asshoman_id}> gave {original_name}'s `{job}` job to {swapped_name}")

@slack_app.action("reassign-option-jobs")
def signoff_job_option(ack):
    """
    Acknowledge, but do not take any action when a job is selected
    """
    ack()

@slack_app.action("reassign-option-brothers")
def signoff_job_checkboxes(ack):
    """
    Acknowledge, but do not take any action when a brother is selected
    """
    ack()