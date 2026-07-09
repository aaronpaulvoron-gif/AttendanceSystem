import secrets
from datetime import datetime, timedelta



def create_token():

    token = secrets.token_urlsafe(8)

    expiry = (
        datetime.now() + timedelta(minutes=5)
    )

    return token, expiry



def check_token(token, qr_data):

    if not qr_data:
        return False


    if token != qr_data["Token"]:
        return False



    expiry_time = datetime.fromisoformat(
        qr_data["Expiry"]
    )


    if datetime.now() > expiry_time:

        return False


    return True