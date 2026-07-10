import gspread
import os
import json

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


    # Render uses Environment Variables
    google_credentials = os.environ.get(
        "GOOGLE_CREDENTIALS"
    )


    if google_credentials:

        creds = Credentials.from_service_account_info(
            json.loads(google_credentials),
            scopes=scopes
        )


    else:

        # Local computer fallback
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


    students = sheet.worksheet(
        "Students"
    )


    return students.get_all_records()



# =========================
# CREATE DAILY ATTENDANCE
# =========================

def create_daily_attendance():

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


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    headers = attendance.row_values(1)



    if today in headers:
        return



    # add today's date column

    new_column = len(headers) + 1


    attendance.update_cell(
        1,
        new_column,
        today
    )



    students = students_sheet.get_all_records()



    for student in students:

        attendance.append_row(
            [
                student["Student ID"],
                student["Name"],
                "A"
            ]
        )





# =========================
# RECORD PRESENT
# =========================

def record_attendance(student_id):


    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    attendance = sheet.worksheet(
        "Attendance"
    )


    headers = attendance.row_values(1)


    today_column = len(headers)



    records = attendance.get_all_records()



    for row_number, row in enumerate(
        records,
        start=2
    ):


        if row["Student ID"] == student_id:



            current = attendance.cell(
                row_number,
                today_column
            ).value



            if current == "P":

                return False



            attendance.update_cell(
                row_number,
                today_column,
                "P"
            )


            return True



    return False





# =========================
# QR STORAGE
# =========================

def save_qr_token(token, expiry):

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    qr = sheet.worksheet(
        "QR"
    )


    qr.clear()


    qr.append_row(
        [
            "Token",
            "Expiry"
        ]
    )


    qr.append_row(
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


    qr = sheet.worksheet(
        "QR"
    )


    data = qr.get_all_records()


    if not data:
        return None


    return data[0]





# =========================
# COLORS
# =========================

def color_attendance():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    attendance = sheet.worksheet(
        "Attendance"
    )


    values = attendance.get_all_values()



    for r in range(2, len(values)+1):

        for c in range(3, len(values[0])+1):


            cell = attendance.cell(
                r,
                c
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





# =========================
# CLEAR TEST DATA
# =========================

def clear_attendance():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    attendance = sheet.worksheet(
        "Attendance"
    )


    attendance.clear()


    attendance.append_row(
        [
            "Student ID",
            "Name"
        ]
    )