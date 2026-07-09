import secrets
from datetime import datetime, timedelta


def create_token():

    # random QR code
    token = secrets.token_urlsafe(12)

    # valid for 1 hour
    expiry = datetime.now() + timedelta(hours=1)

    return token, expiry



def check_token(token, qr_data):

    if qr_data is None:
        return False


    # attendance closed
    if qr_data["Token"] == "CLOSED":
        return False


    # wrong QR
    if token != qr_data["Token"]:
        return False


    expiry = datetime.fromisoformat(
        qr_data["Expiry"]
    )


    # expired
    if datetime.now() > expiry:
        return False


    return True