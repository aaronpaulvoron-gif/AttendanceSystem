import qrcode
import os

from modules.security import generate_token



def create_qr():


    token = generate_token()




    url = (
        "http://192.168.1.130:5000/"
        f"?token={token}"
    )



    qr = qrcode.make(url)



    folder = os.path.join(
        "static",
        "qr"
    )



    if not os.path.exists(folder):

        os.makedirs(folder)



    path = os.path.join(
        folder,
        "attendance_qr.png"
    )



    qr.save(path)



    return token, path