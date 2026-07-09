import qrcode
import os



def create_qr(token):


    website = (
        "https://attendancesystem-li6i.onrender.com/"
    )


    url = (
        website +
        f"?token={token}"
    )


    qr = qrcode.make(
        url
    )


    os.makedirs(
        "static/qr",
        exist_ok=True
    )


    path = (
        "static/qr/attendance_qr.png"
    )


    qr.save(path)


    return path