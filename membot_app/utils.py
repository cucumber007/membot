import base64
from datetime import timedelta


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
    return base64.b64encode(base64.b64encode(base64.b64encode(s)))


def decrypt(s):
    return base64.b64decode(base64.b64decode(base64.b64decode(s)))
