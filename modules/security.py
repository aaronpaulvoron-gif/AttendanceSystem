import secrets
from datetime import datetime, timedelta


def create_token():

    token = secrets.token_urlsafe(8)

    expiry = datetime.now() + timedelta(minutes=5)

    return token, expiry



def check_token(token, qr_data):

    if qr_data is None:
        return False

    if token != qr_data["Token"]:
        return False

    expiry = datetime.fromisoformat(
        qr_data["Expiry"]
    )

    if datetime.now() > expiry:
        return False

    return True