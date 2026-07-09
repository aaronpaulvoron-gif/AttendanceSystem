from flask import Flask, render_template, request
from datetime import datetime

from modules.sheets import (
    get_students,
    record_attendance,
    create_weekly_attendance,
    color_attendance,
    save_qr_token,
    get_qr_token
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

        return "❌ Please scan QR Code first"



    qr_data = get_qr_token()



    if not check_token(
        token,
        qr_data
    ):

        return "❌ Invalid or expired QR Code"



    message = ""



    if request.method == "POST":


        student_id = request.form.get(
            "student_id"
        )


        students = get_students()



        for student in students:


            if student["Student ID"] == student_id:


                result = record_attendance(
                    student["Student ID"],
                    student["Name"]
                )


                if result:

                    message = (
                        "Attendance Recorded ✅"
                    )

                else:

                    message = (
                        "Already Recorded ⚠️"
                    )


                break


        else:

            message = (
                "Student ID not found ❌"
            )



    return render_template(
        "index.html",
        message=message,
        token=token
    )





@app.route("/generate-qr")
def generate_qr():


    token, expiry = create_token()



    save_qr_token(
        token,
        expiry
    )



    path = create_qr(
        token
    )



    return f"""

    <h1>Attendance QR Generated ✅</h1>

    <img src="/static/qr/attendance_qr.png"
    width="300">

    <h3>
    Expires:
    {expiry}
    </h3>

    <p>
    Students scan this QR
    </p>

    """





@app.route("/close-attendance")
def close_attendance():


    save_qr_token(
        "CLOSED",
        datetime.now()
    )


    return """
    <h1>
    Attendance Closed 🔒
    </h1>
    """





@app.route("/create-week")
def create_week():

    create_weekly_attendance()

    return "Week created ✅"





@app.route("/color")
def color():

    color_attendance()

    return "Colors Updated ✅"





if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )