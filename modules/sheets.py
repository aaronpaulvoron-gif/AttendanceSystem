import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from gspread_formatting import (
    CellFormat,
    Color,
    format_cell_range
)


def connect_google_sheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]


    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes
    )


    client = gspread.authorize(
        creds
    )

    return client



def get_students():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    students_sheet = sheet.worksheet(
        "Students"
    )


    return students_sheet.get_all_records()



def record_attendance(student_id, name):

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    attendance = sheet.worksheet(
        "Attendance"
    )


    data = attendance.get_all_records()


    for row_number, row in enumerate(data, start=2):

        if row["Student ID"] == student_id:

            # Find current week column
            headers = attendance.row_values(1)


            week = headers[-1]


            current = attendance.cell(
                row_number,
                len(headers)
            ).value


            if current == "P":
                return False


            attendance.update_cell(
                row_number,
                len(headers),
                "P"
            )


            return True


    return False



def create_weekly_attendance():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    students_sheet = sheet.worksheet(
        "Students"
    )


    attendance = sheet.worksheet(
        "Attendance"
    )


    students = students_sheet.get_all_records()


    week = (
        "Week "
        +
        str(datetime.now().isocalendar().week)
    )


    attendance.update_cell(
        1,
        attendance.col_count + 1,
        week
    )


    for index, student in enumerate(students, start=2):

        attendance.append_row(
            [
                student["Student ID"],
                student["Name"],
                "A"
            ]
        )



def color_attendance():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    attendance = sheet.worksheet(
        "Attendance"
    )


    values = attendance.get_all_values()


    for row in range(2, len(values)+1):

        for col in range(3, len(values[0])+1):

            cell = attendance.cell(
                row,
                col
            )


            if cell.value == "P":

                format_cell_range(
                    attendance,
                    cell.address,
                    CellFormat(
                        backgroundColor=Color(
                            0.4,
                            1,
                            0.4
                        )
                    )
                )


            elif cell.value == "A":

                format_cell_range(
                    attendance,
                    cell.address,
                    CellFormat(
                        backgroundColor=Color(
                            1,
                            0.4,
                            0.4
                        )
                    )
                )



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


    if not data:
        return None


    return data[0]