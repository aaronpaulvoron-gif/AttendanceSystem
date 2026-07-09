import qrcode
import os



def create_qr(token):


    # PUT YOUR RENDER LINK HERE
    website = (
        "https://attendancesystem-li6i.onrender.com"
    )


    url = (
        website +
        f"?token={token}"
    )


    qr = qrcode.make(url)


    folder = "static/qr"


    os.makedirs(
        folder,
        exist_ok=True
    )


    path = (
        "static/qr/attendance_qr.png"
    )


    qr.save(path)


    return path