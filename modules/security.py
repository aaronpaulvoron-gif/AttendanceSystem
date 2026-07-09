import secrets
from datetime import datetime, timedelta



def create_token():

    token = secrets.token_urlsafe(8)

    expiry = (
        datetime.now() + timedelta(minutes=5)
    ).timestamp()


    return token, expiry




def check_token(token, expiry):

    if not token:
        return False


    if not expiry:
        return False


    if datetime.now().timestamp() > float(expiry):

        return False


    return True