import time
import random
import string


current_token = None
created_time = None



def generate_token():

    global current_token
    global created_time


    current_token = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=10
        )
    )


    created_time = time.time()


    return current_token





def check_token(token):

    global current_token
    global created_time


    if token != current_token:

        return False



    # 7 days expiration

    expire_time = 7 * 24 * 60 * 60


    if time.time() - created_time > expire_time:

        return False



    return True