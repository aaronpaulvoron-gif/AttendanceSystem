import qrcode
import os



def create_qr(token):


    url = (
        "https://attendancesystem-li6i.onrender.com/"
        "?token="
        +
        token
    )


    qr = qrcode.make(url)



    os.makedirs(
        "static/qr",
        exist_ok=True
    )


    qr.save(
        "static/qr/attendance_qr.png"
    )