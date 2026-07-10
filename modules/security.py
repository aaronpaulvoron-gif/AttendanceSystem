import secrets

from datetime import (
    datetime,
    timedelta
)


def create_token(close_time=None):

    token = secrets.token_urlsafe(12)

    if close_time:

        today = datetime.now().date()

        expiry = datetime.combine(
            today,
            close_time
        )

        if expiry <= datetime.now():

            expiry = expiry + timedelta(
                days=1
            )

    else:

        expiry = (
            datetime.now()
            +
            timedelta(hours=1)
        )

    return token, expiry


def check_token(token, qr):

    if qr is None:
        return False

    if qr["Token"] == "CLOSED":
        return False

    if token != qr["Token"]:
        return False

    expiry = datetime.fromisoformat(
        qr["Expiry"]
    )

    if datetime.now() > expiry:
        return False

    return True