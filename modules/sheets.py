# ==========================
# QR TOKEN STORAGE
# ==========================


def save_qr_token(token, expiry):

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    qr_sheet = sheet.worksheet(
        "QR"
    )


    qr_sheet.clear()


    qr_sheet.append_row(
        [
            "Token",
            "Expiry"
        ]
    )


    qr_sheet.append_row(
        [
            token,
            expiry.isoformat()
        ]
    )




def get_qr_token():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    qr_sheet = sheet.worksheet(
        "QR"
    )


    records = qr_sheet.get_all_records()


    if len(records) == 0:

        return None



    return records[0]