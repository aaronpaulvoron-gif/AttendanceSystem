from flask import (
    Flask,
    render_template,
    request,
    session
)


from modules.sheets import (
    get_students,
    record_attendance,
    create_weekly_attendance,
    color_attendance
)


from modules.qr_generator import create_qr


from modules.security import (
    create_token,
    check_token
)



app = Flask(__name__)


app.secret_key = "attendance-secret-key"



# ==========================
# STUDENT PAGE
# ==========================

@app.route("/", methods=["GET", "POST"])
def home():

    message = ""


    token = request.args.get(
        "token"
    )


    if not token:

        return "❌ Please scan the QR Code first"



    if not check_token(
        token,
        session.get("qr_expiry")
    ):

        return "❌ Invalid or expired QR Code"



    if request.method == "POST":


        student_id = request.form.get(
            "student_id"
        )


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

            message = (
                "Student ID not found ❌"
            )




    return render_template(
        "index.html",
        message=message
    )





# ==========================
# CREATE WEEK
# ==========================

@app.route("/create-week")
def create_week():

    create_weekly_attendance()

    return "Weekly attendance created ✅"






# ==========================
# COLORS
# ==========================

@app.route("/color")
def color():

    color_attendance()

    return "Colors updated ✅"






# ==========================
# GENERATE QR
# ==========================

@app.route("/generate-qr")
def generate_qr():


    token, expiry = create_token()


    session["qr_token"] = token

    session["qr_expiry"] = expiry



    path = create_qr(
        token
    )



    return (
        "QR Generated ✅<br>"
        f"Token: {token}<br>"
        f"File: {path}"
    )






if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )