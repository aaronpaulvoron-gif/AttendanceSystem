from flask import Flask, render_template, request
from datetime import datetime

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


@app.route("/", methods=["GET","POST"])
def home():

    token = (
        request.args.get("token")
        or request.form.get("token")
    )


    if not token:
        return "❌ Scan QR first"


    qr_data = get_qr_token()


    if not check_token(token, qr_data):
        return "❌ QR expired or closed"


    message = ""


    if request.method == "POST":

        student_id = request.form.get(
            "student_id"
        )


        students = get_students()


        for student in students:

            if student["Student ID"] == student_id:


                result = record_attendance(
                    student["Student ID"]
                )


                if result:
                    message = "Present ✅"

                else:
                    message = "Already recorded ⚠️"


                break


        else:
            message = "Student ID not found ❌"



    return render_template(
        "index.html",
        token=token,
        message=message
    )





@app.route("/generate-qr")
def generate_qr():


    # create today's attendance
    create_daily_attendance()


    token, expiry = create_token()


    save_qr_token(
        token,
        expiry
    )


    create_qr(
        token
    )


    return """

    <h1>Attendance QR</h1>

    <img src="/static/qr/attendance_qr.png"
    width="300">

    <h3>
    Valid for 1 hour
    </h3>

    """





@app.route("/close")
def close():

    save_qr_token(
        "CLOSED",
        datetime.now()
    )

    return "Attendance Closed 🔒"





@app.route("/color")
def color():

    color_attendance()

    return "Colors Updated ✅"





@app.route("/clear")
def clear():

    clear_attendance()

    return "Attendance cleared ✅"





if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )