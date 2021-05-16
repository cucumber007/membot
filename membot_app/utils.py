import base64
import json
from datetime import timedelta

try:
    with open("local-properties.json", "r") as f:
        LOCAL_PROPERTIES = json.loads(f.read())
except FileNotFoundError:
    LOCAL_PROPERTIES = {}

LOCAL_ADMIN_URL = "http://127.0.0.1:8000"


def timedelta_to_seconds(td):
    return td.days * 86400 + td.seconds


def timedelta_from_seconds(sec):
    return timedelta(sec / 86400)


def format_underscore(s):
    r = s.split("_")
    r[0] = r[0].capitalize()
    return " ".join(r)


def format_datetime(dt):
    return dt.strftime("%b %d, %H:%M")


# lol
def encrypt(s):
    return base64.b64encode(base64.b64encode(base64.b64encode(s.encode("utf-8")))).decode("utf-8")


def decrypt(s):
    return base64.b64decode(base64.b64decode(base64.b64decode(s.encode("utf-8")))).decode("utf-8")

