import qrcode
import os


def create_qr(token):

    website = "https://attendancesystem-li6i.onrender.com/"

    url = website + "?token=" + token

    print("QR URL:", url)  # DEBUG


    qr = qrcode.make(url)


    folder = "static/qr"

    os.makedirs(
        folder,
        exist_ok=True
    )


    path = "static/qr/attendance_qr.png"


    qr.save(path)


    print("QR SAVED:", path)  # DEBUG


    return path