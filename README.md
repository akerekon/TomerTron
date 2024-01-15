# TomerTron
A bot that manages the house jobs for [Alpha Chi Rho Delta Sigma Phi](https://axpdsp.org/).

Made by Andrew Kerekon (1162), Brendan Leu, ...

# Setup
We recommend running the bot on Python `3.11.7`. A useful tool for managing python environments is [pyenv](https://github.com/pyenv/pyenv).

You may need to port forward the bot server. In production, a static IP and properly forwarded port should be used, but locally a service like [ngrok](https://ngrok.com/download) or [CloudFlare Tunnels](https://www.cloudflare.com/products/tunnel/) should work fine.

## Install packages
`pip install -r requirements.txt`

## Environment Variables
In this directory, place a file called `.env` which contrains the following vairables:
```
SLACK_BOT_TOKEN="" # The token for the slack bot
SLACK_SIGNING_SECRET="" # The signing secret token for the slack app 
APP_NAME="TomberTron" # The start command used with the bot
CHANNEL_ID="" # The ID of the slack channel to make announcements in

# PRODUCTION (used with waitress)
SERVER_IP="localhost" # The IP to run the server on
SERVER_PORT="3000" # The port to run the server on
```

## Setting up Slack
Refer to [this guide](https://slack.dev/bolt-python/tutorial/getting-started-http).

The events should go to `/slack/events`. For example, if you are using a port forwarding service such as [ngrok](https://ngrok.com/download) it would look something like: `https://example.ngrok-free.app/slack/events`


## Setting up Google
Refer to [this guide](https://developers.google.com/sheets/api/quickstart/python).

Place `credentials.json` in this directory. Run the bot and the first time a request to Google Sheets is made, you will see a sign in link in the console. Click it and sign in with Google, then `token.json` should appear.

The ID of the Google Sheet to be used is in `bot/sheets_data.py` in a variable called `SPREADSHEET_ID`.

# Running
## To run in production

`python server.py`

## To run in a test environment

`flask --app bot run --debug -p 3000`

`ngrok http --domain="{{ DOMAIN HERE }}" 3000`

# Other useful resources
- [Slack Block Builder](https://app.slack.com/block-kit-builder)
- [Bolt Start Guide](https://slack.dev/bolt-python/tutorial/getting-started-http)

# Conventions
If people dont follow these so be it, but try your best.
- Actions begin with the name of the flow they belong to such as they follow `flow-action`, such as `signoff-begin` in `signoff.py`.