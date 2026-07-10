import os

from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from modules.sheets import (
    get_students,
    record_attendance,
    create_daily_attendance,
    color_attendance,
    save_qr_token,
    get_qr_token,
    clear_attendance
)

from modules.qr_generator import create_qr

from modules.security import (
    create_token,
    check_token
)


app = Flask(__name__)


# Used to keep the teacher logged in.
# Put a stronger SECRET_KEY in Render later.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "attendance-secret-key-change-this"
)


# =========================
# ADMIN LOGIN PROTECTION
# =========================

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


# =========================
# STUDENT ATTENDANCE PAGE
# =========================

@app.route("/", methods=["GET", "POST"])
def home():

    token = (
        request.args.get("token")
        or request.form.get("token")
    )

    if not token:

        return render_template(
            "index.html",
            token="",
            message="❌ Scan the attendance QR first"
        )

    qr_data = get_qr_token()

    if not check_token(token, qr_data):

        return render_template(
            "index.html",
            token=token,
            message="❌ QR expired or attendance is closed"
        )

    message = ""

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            ""
        ).strip()

        students = get_students()

        for student in students:

            saved_student_id = str(
                student["Student ID"]
            ).strip()

            if saved_student_id == student_id:

                result = record_attendance(
                    saved_student_id
                )

                if result:

                    message = (
                        f'✅ {student["Name"]} '
                        "is marked Present"
                    )

                else:

                    message = (
                        "⚠️ Attendance already recorded"
                    )

                break

        else:

            message = "❌ Student ID not found"

    return render_template(
        "index.html",
        token=token,
        message=message
    )


# =========================
# TEACHER LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
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
        )

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

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        message = "Incorrect username or password."

    return render_template(
        "login.html",
        message=message
    )


# =========================
# TEACHER LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
@admin_required
def admin():

    return render_template(
        "admin.html",
        message=""
    )


# =========================
# GENERATE QR
# =========================

@app.route("/generate-qr")
@admin_required
def generate_qr():

    # Create today's attendance.
    create_daily_attendance()

    # Create a secure QR token.
    token, expiry = create_token()

    # Save it in the QR worksheet.
    save_qr_token(
        token,
        expiry
    )

    # Generate the QR image.
    create_qr(
        token
    )

    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>Attendance QR</title>

        <link
            rel="stylesheet"
            href="/static/css/style.css"
        >

    </head>

    <body>

        <div class="container">

            <h1>Attendance QR</h1>

            <img
                src="/static/qr/attendance_qr.png?token={token}"
                width="300"
                alt="Attendance QR"
            >

            <h3>
                Valid until:
                {expiry.strftime("%I:%M %p")}
            </h3>

            <a
                href="/admin"
                class="admin-button gray-button"
            >
                Back to Dashboard
            </a>

        </div>

    </body>

    </html>

    """


# =========================
# CLOSE ATTENDANCE
# =========================

@app.route("/close")
@admin_required
def close():

    save_qr_token(
        "CLOSED",
        datetime.now()
    )

    return render_template(
        "admin.html",
        message="🔒 Attendance closed successfully"
    )


# =========================
# UPDATE COLORS
# =========================

@app.route("/color")
@admin_required
def color():

    color_attendance()

    return render_template(
        "admin.html",
        message="✅ Attendance colors updated"
    )


# =========================
# CLEAR ATTENDANCE
# =========================

@app.route("/clear")
@admin_required
def clear():

    clear_attendance()

    return render_template(
        "admin.html",
        message="✅ Attendance sheet cleared"
    )


# =========================
# RUN APPLICATION
# =========================

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