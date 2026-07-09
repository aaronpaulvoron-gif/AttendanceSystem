import gspread
import os
import json

from google.oauth2.service_account import Credentials
from datetime import datetime

from gspread_formatting import (
    format_cell_range,
    CellFormat,
    Color
)



def connect_google_sheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]


    # Render uses this
    google_credentials = os.environ.get(
        "GOOGLE_CREDENTIALS"
    )


    if google_credentials:

        credentials_dict = json.loads(
            google_credentials
        )


        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=scopes
        )


    # Local PyCharm testing
    else:

        credentials = Credentials.from_service_account_file(
            "credentials.json",
            scopes=scopes
        )


    client = gspread.authorize(credentials)

    return client





# GET STUDENTS LIST
def get_students():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )

    students_sheet = sheet.worksheet(
        "Students"
    )

    students = students_sheet.get_all_records()

    return students





# CREATE WEEKLY ATTENDANCE
def create_weekly_attendance():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    students_sheet = sheet.worksheet(
        "Students"
    )

    attendance_sheet = sheet.worksheet(
        "Attendance"
    )


    students = students_sheet.get_all_records()


    attendance_sheet.clear()


    attendance_sheet.append_row(
        [
            "Student ID",
            "Name",
            "Status",
            "Time"
        ]
    )


    for student in students:

        attendance_sheet.append_row(
            [
                student["Student ID"],
                student["Name"],
                "A",
                "-"
            ]
        )


    color_attendance()






# RECORD PRESENT
def record_attendance(student_id, name):

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    attendance_sheet = sheet.worksheet(
        "Attendance"
    )


    records = attendance_sheet.get_all_records()


    for index, row in enumerate(records, start=2):


        if row["Student ID"] == student_id:


            if row["Status"] == "P":

                return False



            attendance_sheet.update_cell(
                index,
                3,
                "P"
            )


            attendance_sheet.update_cell(
                index,
                4,
                datetime.now().strftime(
                    "%I:%M %p"
                )
            )


            color_attendance()


            return True



    return False






# COLOR STATUS
def color_attendance():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )


    attendance_sheet = sheet.worksheet(
        "Attendance"
    )


    records = attendance_sheet.get_all_records()



    for index, row in enumerate(records, start=2):

        cell = f"C{index}"



        if row["Status"] == "P":

            format_cell_range(
                attendance_sheet,
                cell,
                CellFormat(
                    backgroundColor=Color(
                        0.5,
                        1,
                        0.5
                    )
                )
            )


        elif row["Status"] == "A":

            format_cell_range(
                attendance_sheet,
                cell,
                CellFormat(
                    backgroundColor=Color(
                        1,
                        0.5,
                        0.5
                    )
                )
            )