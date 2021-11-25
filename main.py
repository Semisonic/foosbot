from parser import parse_query
from common import RequestContext
import db
from flask import Flask

import time
import hashlib
import hmac
from pathlib import Path
import requests
import yaml
from flask import request
import json
import logging
app = Flask(__name__)


config = yaml.safe_load(Path("config.yaml").read_text())

logger = logging.Logger(__name__)


def get_user_tokens():
    return json.loads(Path("user_tokens.json").read_text())


def set_user_token(user_id, token):
    tokens = get_user_tokens()
    tokens[user_id] = token
    Path("user_tokens.json").write_text(json.dumps(tokens))


@app.route("/")
def hello_world():
    return "Life is beautiful. \U0001F308"


@app.route("/auth", methods=["GET"])
def auth_new_user():
    code = request.args.get("code")
    state = request.args.get("state")

    r = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": config["slack"]["client_id"],
            "client_secret": config["slack"]["client_secret"],
            "code": code,
        }
    )

    data = r.json()
    if not data["ok"]:
        return "Could not authenticate. \U0001F61E"

    user_id = data["authed_user"]["id"]
    user_token = data["access_token"]

    logger.info("New user signed up %s", user_id)
    set_user_token(user_id, user_token)

    return "All good. You can now return to Slack and search for Foosbot. \U0001F60E"


@app.route("/events", methods=["POST"])
def events_route():
    if not valid_request():
        return {}

    payload = request.get_json()
    return EVENTS_ROUTE_HANDLERS.get(payload.get("type"), events_route_default)(payload)


def valid_request():
    slack_signing_secret = config["slack"]["signing_secret"].encode()
    request_body = request.get_data().decode()
    slack_request_timestamp = request.headers["X-Slack-Request-Timestamp"]
    slack_signature = request.headers["X-Slack-Signature"]

    if (int(time.time()) - int(slack_request_timestamp)) > 60:
        print("Verification failed. Request is out of date.")
        return False

    basestring = f"v0:{slack_request_timestamp}:{request_body}".encode("utf-8")
    my_signature = (
        "v0=" + hmac.new(slack_signing_secret, basestring,
                         hashlib.sha256).hexdigest()
    )
    return hmac.compare_digest(my_signature, slack_signature)


def events_route_url_verification(payload):
    return {"challenge": payload["challenge"]}


def events_route_event_callback(payload):
    return EVENT_HANDLERS.get(payload.get("event", {}).get("type"), event_default)(payload)


def events_route_default(payload):
    logger.warning("Could not handle events call: %s", payload)
    return {}


EVENTS_ROUTE_HANDLERS = {
    "url_verification": events_route_url_verification,
    "event_callback": events_route_event_callback,
}

import executor

def event_message(payload):
    logger.info("User says: %s", payload["event"]["text"], "\x1b[0m")

    if 'bot_profile' in payload["event"]:
        return {}

    response_msg = "No message."
    user_id = payload["event"]["user"]

    ctx = RequestContext(user_id, get_message_refered_users(payload["event"]))
    try:
        cmd = parse_query(payload["event"]["text"], ctx)
        for artifact in executor.execute_command(cmd):
            if isinstance(artifact, executor.SendMessageArtifact):
                send_message(
                    channel=artifact.user_id,  # payload["event"]["channel"],
                    text=artifact.message,
                    token=get_user_tokens()[user_id],
                )

    except Exception as e:
        response_msg = f"Could not parse your query: {e}"


    return {}


def get_message_refered_users(event):
    return {
        element["user_id"]
        for block in event["blocks"]
        for elements in block["elements"]
        for element in elements["elements"]
        if element["type"] == "user"
    }


def event_default(payload):
    logger.warning("Could not process event: %s", payload)
    return {}


EVENT_HANDLERS = {
    "message": event_message,
}


def send_message(channel, text, token):
    r = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "channel": channel,
            "text": text,
        })

    logger.info("Sent message %s", r.json())


logger.setLevel(logging.INFO)


