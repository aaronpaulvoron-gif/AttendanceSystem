import gspread
import os
import json

from google.oauth2.service_account import Credentials
from datetime import datetime, time

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

    # Make sure the Attendance sheet has headers.
    headers = attendance.row_values(1)

    if len(headers) < 2:

        attendance.clear()

        attendance.append_row([
            "Student ID",
            "Name"
        ])

        headers = [
            "Student ID",
            "Name"
        ]

    students = students_sheet.get_all_records()

    attendance_values = attendance.get_all_values()

    existing_ids = set()

    # Get IDs already inside the Attendance sheet.
    for row in attendance_values[1:]:

        if len(row) >= 1:

            existing_id = str(
                row[0]
            ).strip()

            if existing_id:

                existing_ids.add(
                    existing_id
                )

    # Add missing students only once.
    for student in students:

        student_id = str(
            student["Student ID"]
        ).strip()

        student_name = str(
            student["Name"]
        ).strip()

        if student_id not in existing_ids:

            attendance.append_row([
                student_id,
                student_name
            ])

            existing_ids.add(
                student_id
            )

    # Refresh headers after syncing students.
    headers = attendance.row_values(1)

    # If today's date already exists, do nothing.
    if today in headers:

        return

    # Add today's date as a new column.
    today_column = len(headers) + 1

    attendance.update_cell(
        1,
        today_column,
        today
    )

    # Mark every student Absent by default.
    attendance_values = attendance.get_all_values()

    total_rows = len(
        attendance_values
    )

    for row_number in range(
        2,
        total_rows + 1
    ):

        attendance.update_cell(
            row_number,
            today_column,
            "A"
        )





# =========================
# RECORD PRESENT
# =========================
def get_attendance_status():

    current_time = datetime.now().time()

    # Change these times based on your class schedule.
    present_until = time(8, 0)
    late_until = time(8, 15)

    if current_time <= present_until:
        return "P"

    if current_time <= late_until:
        return "L"

    return None

def record_attendance(student_id):

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )

    attendance = sheet.worksheet(
        "Attendance"
    )

    headers = attendance.row_values(1)

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    if today not in headers:
        create_daily_attendance()
        headers = attendance.row_values(1)

    today_column = headers.index(today) + 1

    status = get_attendance_status()

    if status is None:
        return {
            "success": False,
            "reason": "closed"
        }

    records = attendance.get_all_records()

    for row_number, row in enumerate(
        records,
        start=2
    ):

        saved_id = str(
            row["Student ID"]
        ).strip()

        if saved_id == str(student_id).strip():

            current = attendance.cell(
                row_number,
                today_column
            ).value

            if current in ["P", "L"]:

                return {
                    "success": False,
                    "reason": "duplicate",
                    "status": current
                }

            attendance.update_cell(
                row_number,
                today_column,
                status
            )

            return {
                "success": True,
                "status": status
            }

    return {
        "success": False,
        "reason": "not_found"
    }

def get_attendance_stats():

    client = connect_google_sheet()

    sheet = client.open(
        "Attendance Monitoring System"
    )

    attendance = sheet.worksheet(
        "Attendance"
    )

    values = attendance.get_all_values()

    stats = {
        "total": 0,
        "present": 0,
        "late": 0,
        "absent": 0
    }

    if not values:
        return stats

    headers = values[0]

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    if today not in headers:
        return stats

    today_column = headers.index(today)

    for row in values[1:]:

        if not row:
            continue

        student_id = str(
            row[0]
        ).strip()

        if not student_id:
            continue

        stats["total"] += 1

        if today_column < len(row):

            status = row[today_column]

        else:

            status = "A"

        if status == "P":

            stats["present"] += 1

        elif status == "L":

            stats["late"] += 1

        else:

            stats["absent"] += 1

    return stats


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
            elif cell.value == "L":

                format_cell_range(
                    attendance,
                    cell.address,
                    CellFormat(
                        backgroundColor=Color(
                            1,
                            0.85,
                            0.3
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