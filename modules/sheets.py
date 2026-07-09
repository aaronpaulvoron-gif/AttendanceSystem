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


    data = qr_sheet.get_all_records()


    if len(data) == 0:
        return None


    return data[0]