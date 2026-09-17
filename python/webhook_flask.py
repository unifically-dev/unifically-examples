"""Receive Unifically task callbacks and verify the signature.

Pass "callback_url" at the top level of POST /v1/tasks (next to "model" and
"input") and the API will POST here when the task completes or fails.
Turn on signing in the dashboard under Settings, then set
UNIFICALLY_WEBHOOK_SECRET to the 64 character hex secret it gives you.

  pip install flask
  UNIFICALLY_WEBHOOK_SECRET=... flask --app webhook_flask run --port 8000
"""
import hashlib
import hmac
import os
import re
import time

from flask import Flask, abort, request

app = Flask(__name__)
SECRET = os.environ.get("UNIFICALLY_WEBHOOK_SECRET", "")
TOLERANCE_SECONDS = 300  # replay window, your choice


def verified(req) -> bool:
    timestamp = req.headers.get("x-webhook-timestamp", "")
    signature = req.headers.get("x-webhook-signature", "")
    if not timestamp.isdigit() or not re.fullmatch(r"[a-f0-9]{64}", signature):
        return False
    if abs(time.time() - int(timestamp)) > TOLERANCE_SECONDS:
        return False
    # Sign the raw bytes, not re-serialized JSON.
    message = timestamp.encode() + b"." + req.get_data()
    expected = hmac.new(SECRET.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.post("/webhook")
def webhook():
    if SECRET and not verified(request):
        abort(401)
    event = request.get_json()
    if event["status"] == "completed":
        print("done", event["task_id"], event["data"])
    else:
        print("failed", event["task_id"], event.get("error_message"))
    return "", 200
