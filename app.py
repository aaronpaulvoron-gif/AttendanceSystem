import os

from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from modules.sheets import (
    add_student,
    clear_attendance,
    color_attendance,
    create_daily_attendance,
    delete_student,
    get_attendance_stats,
    get_qr_token,
    get_student_report,
    get_students,
    record_attendance,
    save_qr_token
)

from modules.qr_generator import create_qr

from modules.security import (
    check_token,
    create_token
)


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key"
)


# Protect teacher pages
def admin_required(route_function):

    @wraps(route_function)
    def protected_route(*args, **kwargs):

        if not session.get("admin_logged_in"):

            return redirect(
                url_for("login")
            )

        return route_function(
            *args,
            **kwargs
        )

    return protected_route


# Load dashboard
def render_admin_dashboard(message=""):

    stats = get_attendance_stats()

    qr_data = get_qr_token()

    qr_status = "CLOSED"
    expiry_text = "No active QR"

    if qr_data:

        saved_token = str(
            qr_data.get(
                "Token",
                ""
            )
        )

        saved_expiry = str(
            qr_data.get(
                "Expiry",
                ""
            )
        )

        if saved_token != "CLOSED":

            try:

                expiry = datetime.fromisoformat(
                    saved_expiry
                )

                if datetime.now() <= expiry:

                    qr_status = "OPEN"

                    expiry_text = expiry.strftime(
                        "%I:%M %p"
                    )

            except (
                ValueError,
                TypeError
            ):

                qr_status = "CLOSED"
                expiry_text = "Invalid expiry"

    return render_template(
        "admin.html",
        message=message,
        stats=stats,
        qr_status=qr_status,
        expiry_text=expiry_text
    )


# Student attendance page
@app.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)
def home():

    token = (
        request.args.get("token")
        or request.form.get("token")
    )

    if not token:

        return render_template(
            "index.html",
            token="",
            message="❌ Scan the active attendance QR first.",
            expiry=""
        )

    qr_data = get_qr_token()

    expiry = ""

    if qr_data:

        expiry = str(
            qr_data.get(
                "Expiry",
                ""
            )
        )

    if not check_token(
        token,
        qr_data
    ):

        return render_template(
            "index.html",
            token=token,
            message=(
                "❌ QR expired, invalid, "
                "or attendance is closed."
            ),
            expiry=""
        )

    message = ""

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            ""
        ).strip()

        if not student_id:

            message = (
                "❌ Please enter your Student ID."
            )

        else:

            students = get_students()

            for student in students:

                saved_student_id = str(
                    student.get(
                        "Student ID",
                        ""
                    )
                ).strip()

                if saved_student_id == student_id:

                    device_student_id = session.get(
                        "attendance_student_id"
                    )

                    device_token = session.get(
                        "attendance_token"
                    )

                    if (
                        device_token == token
                        and device_student_id
                        and device_student_id
                        != saved_student_id
                    ):

                        message = (
                            "❌ This phone or browser has "
                            "already submitted attendance "
                            "for another student."
                        )

                        break

                    result = record_attendance(
                        saved_student_id
                    )

                    if result["success"]:

                        session[
                            "attendance_student_id"
                        ] = saved_student_id

                        session[
                            "attendance_token"
                        ] = token

                        if result["status"] == "P":

                            message = (
                                f'✅ {student["Name"]} '
                                "is marked Present."
                            )

                        elif result["status"] == "L":

                            message = (
                                f'⚠️ {student["Name"]} '
                                "is marked Late."
                            )

                    elif result["reason"] == "duplicate":

                        previous_status = result.get(
                            "status",
                            ""
                        )

                        if previous_status == "P":

                            status_text = "Present"

                        elif previous_status == "L":

                            status_text = "Late"

                        else:

                            status_text = (
                                "already recorded"
                            )

                        message = (
                            "⚠️ Attendance already "
                            f"recorded as {status_text}."
                        )

                    elif result["reason"] == "closed":

                        message = (
                            "❌ The attendance time "
                            "window is already closed."
                        )

                    elif result["reason"] == "date_not_found":

                        message = (
                            "❌ Today's attendance "
                            "column could not be created."
                        )

                    else:

                        message = (
                            "❌ Attendance could not "
                            "be recorded."
                        )

                    break

            else:

                message = (
                    "❌ Student ID not found."
                )

    return render_template(
        "index.html",
        token=token,
        message=message,
        expiry=expiry
    )


# Teacher login
@app.route(
    "/login",
    methods=[
        "GET",
        "POST"
    ]
)
def login():

    if session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    message = ""

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        correct_username = os.environ.get(
            "ADMIN_USERNAME",
            "admin"
        )

        correct_password = os.environ.get(
            "ADMIN_PASSWORD",
            "admin123"
        )

        if (
            username == correct_username
            and password == correct_password
        ):

            session[
                "admin_logged_in"
            ] = True

            return redirect(
                url_for("admin")
            )

        message = (
            "Incorrect username or password."
        )

    return render_template(
        "login.html",
        message=message
    )


# Teacher logout
@app.route("/logout")
def logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("login")
    )


# Admin dashboard
@app.route("/admin")
@admin_required
def admin():

    return render_admin_dashboard()


# Generate QR
@app.route(
    "/generate-qr",
    methods=[
        "GET",
        "POST"
    ]
)
@admin_required
def generate_qr():

    if request.method == "GET":

        return redirect(
            url_for("admin")
        )

    close_time_text = request.form.get(
        "close_time",
        ""
    ).strip()

    if not close_time_text:

        return render_admin_dashboard(
            "❌ Please choose an attendance closing time."
        )

    try:

        close_time = datetime.strptime(
            close_time_text,
            "%H:%M"
        ).time()

    except ValueError:

        return render_admin_dashboard(
            "❌ Invalid closing time."
        )

    create_daily_attendance()

    token, expiry = create_token(
        close_time
    )

    save_qr_token(
        token,
        expiry
    )

    create_qr(
        token
    )

    return redirect(
        url_for("current_qr")
    )


# View current QR
@app.route("/current-qr")
@admin_required
def current_qr():

    qr_data = get_qr_token()

    if not qr_data:

        return render_admin_dashboard(
            "❌ No QR has been generated."
        )

    token = str(
        qr_data.get(
            "Token",
            ""
        )
    )

    expiry_text = str(
        qr_data.get(
            "Expiry",
            ""
        )
    )

    if token == "CLOSED":

        return render_admin_dashboard(
            "❌ Attendance is currently closed."
        )

    try:

        expiry = datetime.fromisoformat(
            expiry_text
        )

    except (
        ValueError,
        TypeError
    ):

        return render_admin_dashboard(
            "❌ The saved QR expiry is invalid."
        )

    if datetime.now() > expiry:

        return render_admin_dashboard(
            "❌ The current QR has already expired."
        )

    return render_template(
        "current_qr.html",
        token=token,
        expiry=expiry.isoformat(),
        expiry_display=expiry.strftime(
            "%I:%M %p"
        )
    )


# Close attendance
@app.route("/close")
@admin_required
def close():

    save_qr_token(
        "CLOSED",
        datetime.now()
    )

    return render_admin_dashboard(
        "🔒 Attendance closed successfully."
    )


# Update colors
@app.route("/color")
@admin_required
def color():

    color_attendance()

    return render_admin_dashboard(
        "✅ Attendance colors updated."
    )


# Clear attendance
@app.route("/clear")
@admin_required
def clear():

    clear_attendance()

    return render_admin_dashboard(
        "✅ Attendance sheet cleared."
    )


# Manage students
@app.route(
    "/students",
    methods=[
        "GET",
        "POST"
    ]
)
@admin_required
def students():

    message = ""

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        result = add_student(
            student_id,
            name
        )

        if result["success"]:

            message = (
                "✅ Student added successfully."
            )

        elif result["reason"] == "duplicate":

            message = (
                "⚠️ Student ID already exists."
            )

        else:

            message = (
                "❌ Student ID and name are required."
            )

    student_list = get_students()

    return render_template(
        "students.html",
        students=student_list,
        message=message
    )


# Delete student
@app.route(
    "/students/delete/<student_id>",
    methods=["POST"]
)
@admin_required
def remove_student(student_id):

    delete_student(
        student_id
    )

    return redirect(
        url_for("students")
    )


# Search student
@app.route(
    "/student-search",
    methods=[
        "GET",
        "POST"
    ]
)
@admin_required
def student_search():

    message = ""
    report = None

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            ""
        ).strip()

        if not student_id:

            message = (
                "❌ Enter a Student ID."
            )

        else:

            result = get_student_report(
                student_id
            )

            if result["success"]:

                report = result

            else:

                message = (
                    "❌ Student ID not found."
                )

    return render_template(
        "student_search.html",
        message=message,
        report=report
    )


# Start app
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )