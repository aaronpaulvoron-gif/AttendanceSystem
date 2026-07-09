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

from modules.security import create_token


app = Flask(__name__)


# ==========================
# STUDENT PAGE
# ==========================

@app.route("/", methods=["GET", "POST"])
def home():

    token = request.args.get("token")


    if not token:
        return "❌ Please scan QR Code first"


    qr_data = get_qr_token()


    # DEBUG MODE
    return f"""
    <h2>DEBUG QR</h2>

    <b>Token from phone:</b>
    <br>
    {token}

    <br><br>

    <b>Data from Google Sheet:</b>
    <br>
    {qr_data}
    """


# ==========================
# CREATE WEEK
# ==========================

@app.route("/create-week")
def create_week():

    create_weekly_attendance()

    return "Week created ✅"



# ==========================
# COLOR
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


    save_qr_token(
        token,
        expiry
    )


    path = create_qr(
        token
    )


    return f"""
    <h2>QR Generated ✅</h2>

    Token:
    <br>
    {token}

    <br><br>

    Expiry:
    <br>
    {expiry}

    <br><br>

    Saved:
    <br>
    {path}
    """



if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )