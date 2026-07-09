from flask import Flask, render_template, request

from modules.sheets import (
    get_students,
    record_attendance,
    create_weekly_attendance,
    color_attendance
)

from modules.qr_generator import create_qr

from modules.security import check_token


app = Flask(__name__)


# ==========================
# STUDENT ATTENDANCE
# ==========================

@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    token = request.args.get("token")


    # Require QR token

    if not token:
        return "❌ Please scan the QR Code first"


    # Check QR validity

    if not check_token(token):
        return "❌ Invalid or expired QR Code"



    if request.method == "POST":

        student_id = request.form.get("student_id")


        students = get_students()


        found = False


        for student in students:


            if student["Student ID"] == student_id:


                success = record_attendance(
                    student["Student ID"],
                    student["Name"]
                )


                if success:

                    message = (
                        f"Welcome {student['Name']}! "
                        "Attendance Recorded ✅"
                    )

                else:

                    message = (
                        "Attendance already recorded ⚠️"
                    )


                found = True
                break



        if not found:

            message = "Student ID not found ❌"



    return render_template(
        "index.html",
        message=message
    )



# ==========================
# CREATE WEEKLY ATTENDANCE
# ==========================

@app.route("/create-week")
def create_week():

    create_weekly_attendance()

    return "Weekly attendance created ✅"



# ==========================
# UPDATE GOOGLE SHEET COLORS
# ==========================

@app.route("/color")
def color():

    color_attendance()

    return "Colors updated ✅"



# ==========================
# GENERATE QR CODE
# ==========================

@app.route("/generate-qr")
def generate_qr():

    token, path = create_qr()


    return (
        "QR Generated ✅<br>"
        f"Token: {token}<br>"
        f"File: {path}"
    )



# ==========================
# SERVER START
# ==========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )