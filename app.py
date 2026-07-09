from flask import Flask, render_template, request

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

    token = request.args.get(
        "token"
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


                if record_attendance(
                    student["Student ID"],
                    student["Name"]
                ):

                    message = (
                        "Attendance recorded ✅"
                    )

                else:

                    message = (
                        "Already recorded ⚠️"
                    )

                break

        else:

            message = (
                "Student ID not found ❌"
            )


    return render_template(
        "index.html",
        message=message
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
    QR Generated ✅
    <br>
    Token: {token}
    <br>
    Saved: {path}
    """



@app.route("/create-week")
def create_week():

    create_weekly_attendance()

    return "Week created ✅"



@app.route("/color")
def color():

    color_attendance()

    return "Updated ✅"



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )