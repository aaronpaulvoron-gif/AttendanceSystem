import gspread
import os
import json

from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

from gspread_formatting import (
    CellFormat,
    Color,
    format_cell_range
)


# =========================
# GOOGLE SHEETS CONNECTION
# =========================

def connect_google_sheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Render uses Environment Variables.
    google_credentials = os.environ.get(
        "GOOGLE_CREDENTIALS"
    )

    if google_credentials:

        creds = Credentials.from_service_account_info(
            json.loads(google_credentials),
            scopes=scopes
        )

    else:

        # Local computer fallback.
        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=scopes
        )

    client = gspread.authorize(
        creds
    )

    return client


# =========================
# GET STUDENTS
# =========================

def get_students():

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    students_sheet = spreadsheet.worksheet(
        "Students"
    )

    return students_sheet.get_all_records()


# =========================
# CREATE DAILY ATTENDANCE
# =========================

def create_daily_attendance():

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    students_sheet = spreadsheet.worksheet(
        "Students"
    )

    attendance = spreadsheet.worksheet(
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

    # Get student IDs already inside the Attendance sheet.
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
            student.get(
                "Student ID",
                ""
            )
        ).strip()

        student_name = str(
            student.get(
                "Name",
                ""
            )
        ).strip()

        if (
            student_id
            and student_id not in existing_ids
        ):

            attendance.append_row([
                student_id,
                student_name
            ])

            existing_ids.add(
                student_id
            )

    # Refresh the headers.
    headers = attendance.row_values(1)

    # Do not create the same date twice.
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
# ADD STUDENT
# =========================

def add_student(student_id, name):

    student_id = str(student_id).strip()
    name = str(name).strip()

    if not student_id or not name:

        return {
            "success": False,
            "reason": "missing_fields"
        }

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    students_sheet = spreadsheet.worksheet(
        "Students"
    )

    students = students_sheet.get_all_records()

    for student in students:

        saved_id = str(
            student.get(
                "Student ID",
                ""
            )
        ).strip()

        if saved_id == student_id:

            return {
                "success": False,
                "reason": "duplicate"
            }

    students_sheet.append_row([
        student_id,
        name
    ])

    return {
        "success": True
    }


# =========================
# DELETE STUDENT
# =========================

def delete_student(student_id):

    student_id = str(student_id).strip()

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    students_sheet = spreadsheet.worksheet(
        "Students"
    )

    values = students_sheet.get_all_values()

    for row_number, row in enumerate(
        values[1:],
        start=2
    ):

        if not row:
            continue

        saved_id = str(
            row[0]
        ).strip()

        if saved_id == student_id:

            students_sheet.delete_rows(
                row_number
            )

            return True

    return False

# =========================
# ATTENDANCE TIME STATUS
# =========================

def get_attendance_status():

    qr_data = get_qr_token()

    if not qr_data:
        return None

    if str(qr_data.get("Token", "")) == "CLOSED":
        return None

    try:
        expiry = datetime.fromisoformat(
            str(qr_data.get("Expiry", ""))
        )

    except (ValueError, TypeError):
        return None

    current_time = datetime.now()

    if current_time > expiry:
        return None

    late_start = expiry - timedelta(
        minutes=15
    )

    if current_time >= late_start:
        return "L"

    return "P"

def get_student_report(student_id):

    student_id = str(student_id).strip()

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    students_sheet = spreadsheet.worksheet(
        "Students"
    )

    attendance_sheet = spreadsheet.worksheet(
        "Attendance"
    )

    students = students_sheet.get_all_records()

    student_name = None

    for student in students:

        saved_id = str(
            student.get(
                "Student ID",
                ""
            )
        ).strip()

        if saved_id == student_id:

            student_name = str(
                student.get(
                    "Name",
                    ""
                )
            ).strip()

            break

    if not student_name:

        return {
            "success": False,
            "reason": "not_found"
        }

    values = attendance_sheet.get_all_values()

    report = {
        "success": True,
        "student_id": student_id,
        "name": student_name,
        "present": 0,
        "late": 0,
        "absent": 0,
        "total_classes": 0,
        "percentage": 0,
        "today_status": "No attendance today",
        "history": []
    }

    if not values:

        return report

    headers = values[0]

    target_row = None

    for row in values[1:]:

        if not row:
            continue

        saved_id = str(
            row[0]
        ).strip()

        if saved_id == student_id:

            target_row = row
            break

    if target_row is None:

        return report

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    for column_index in range(
        2,
        len(headers)
    ):

        attendance_date = headers[
            column_index
        ]

        if not attendance_date:
            continue

        if column_index < len(target_row):

            status = str(
                target_row[
                    column_index
                ]
            ).strip()

        else:

            status = "A"

        if not status:

            status = "A"

        report["total_classes"] += 1

        if status == "P":

            report["present"] += 1
            status_text = "Present"

        elif status == "L":

            report["late"] += 1
            status_text = "Late"

        else:

            report["absent"] += 1
            status_text = "Absent"

        if attendance_date == today:

            report["today_status"] = (
                status_text
            )

        report["history"].append({
            "date": attendance_date,
            "status": status,
            "status_text": status_text
        })

    if report["total_classes"] > 0:

        attended_classes = (
            report["present"]
            +
            report["late"]
        )

        report["percentage"] = round(
            (
                attended_classes
                /
                report["total_classes"]
            )
            *
            100,
            2
        )

    report["history"].reverse()

    return report
# =========================
# RECORD ATTENDANCE
# =========================

def record_attendance(student_id):

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    attendance = spreadsheet.worksheet(
        "Attendance"
    )

    create_daily_attendance()

    headers = attendance.row_values(1)

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    if today not in headers:

        return {
            "success": False,
            "reason": "date_not_found"
        }

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

        saved_student_id = str(
            row.get(
                "Student ID",
                ""
            )
        ).strip()

        if saved_student_id == str(student_id).strip():

            current_status = attendance.cell(
                row_number,
                today_column
            ).value

            if current_status in [
                "P",
                "L"
            ]:

                return {
                    "success": False,
                    "reason": "duplicate",
                    "status": current_status
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


# =========================
# ATTENDANCE STATISTICS
# =========================

def get_attendance_stats():

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    attendance = spreadsheet.worksheet(
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

    # No attendance column for today yet.
    if today not in headers:

        stats["total"] = max(
            len(values) - 1,
            0
        )

        stats["absent"] = stats["total"]

        return stats

    # List indexes start at 0.
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

            status = str(
                row[today_column]
            ).strip()

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

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    qr_sheet = spreadsheet.worksheet(
        "QR"
    )

    qr_sheet.clear()

    qr_sheet.append_row([
        "Token",
        "Expiry"
    ])

    qr_sheet.append_row([
        token,
        expiry.isoformat()
    ])


def get_qr_token():

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    qr_sheet = spreadsheet.worksheet(
        "QR"
    )

    data = qr_sheet.get_all_records()

    if not data:
        return None

    return data[0]


# =========================
# ATTENDANCE COLORS
# =========================

def color_attendance():

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    attendance = spreadsheet.worksheet(
        "Attendance"
    )

    values = attendance.get_all_values()

    if not values:
        return

    # Start at row 2 and column 3.
    # Columns 1 and 2 are Student ID and Name.
    for row_number in range(
        2,
        len(values) + 1
    ):

        for column_number in range(
            3,
            len(values[0]) + 1
        ):

            cell = attendance.cell(
                row_number,
                column_number
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
# CLEAR ATTENDANCE DATA
# =========================

def clear_attendance():

    client = connect_google_sheet()

    spreadsheet = client.open(
        "Attendance Monitoring System"
    )

    attendance = spreadsheet.worksheet(
        "Attendance"
    )

    attendance.clear()

    attendance.append_row([
        "Student ID",
        "Name"
    ])