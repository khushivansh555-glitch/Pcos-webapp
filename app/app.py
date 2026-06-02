from flask import Flask, render_template, request, redirect, session
import sys
import os
import random
import smtplib
from email.message import EmailMessage

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(BASE_DIR, "src"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from predict import predict_pcos

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")




@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = [
            float(request.form['Age']),
            float(request.form['Weight']),
            float(request.form['Height']),
            float(request.form['BMI']),
            float(request.form['Blood_Group']),
            float(request.form['Pulse_rate']),
            float(request.form['RR']),
            float(request.form['Hb']),
            float(request.form['Cycle']),
            float(request.form['Cycle_length']),
            float(request.form['Marriage_Status']),
            float(request.form['Pregnant']),
            float(request.form['Abortions']),
            float(request.form['beta_HCG_1']),
            float(request.form['beta_HCG_2']),
            float(request.form['FSH']),
            float(request.form['LH']),
            float(request.form['FSH_LH']),
            float(request.form['Hip']),
            float(request.form['Waist']),
            float(request.form['WHR']),
            float(request.form['TSH']),
            float(request.form['AMH']),
            float(request.form['PRL']),
            float(request.form['VitD3']),
            float(request.form['PRG']),
            float(request.form['RBS']),
            float(request.form['Weight_gain']),
            float(request.form['Hair_growth']),
            float(request.form['Skin_darkening']),
            float(request.form['Hair_loss']),
            float(request.form['Pimples']),
            float(request.form['Fast_food']),
            float(request.form['Exercise']),
            float(request.form['BP_Systolic']),
            float(request.form['BP_Diastolic']),
            float(request.form['Follicle_L']),
            float(request.form['Follicle_R']),
            float(request.form['Avg_F_L']),
            float(request.form['Avg_F_R']),
            float(request.form['Endometrium'])
        ]

        # ✅ FIX: pad missing features
        while len(data) < 44:
            data.append(0)

        result = predict_pcos(data)

        return render_template('symptom.html', prediction_text=f"Result: {result}")

    except Exception as e:
        return f"Error: {e}"




from flask import render_template, request, redirect
import sqlite3
import re
from predict import predict_pcos


# --------- DATABASE SETUP --------- #

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # COMMUNITY POSTS TABLE 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# --------- EMAIL VALIDATION --------- #

def is_valid_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email)


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(recipient_email, otp_code):
    sender = os.environ.get("EMAIL_ADDRESS")
    password = os.environ.get("EMAIL_PASSWORD")
    smtp_host = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("EMAIL_PORT", 587))

    if not sender or not password:
        raise RuntimeError("Email sender credentials are not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD.")

    message = EmailMessage()
    message["Subject"] = "Your OTP Code"
    message["From"] = sender
    message["To"] = recipient_email
    message.set_content(f"Your verification OTP is: {otp_code}\n\nIf you did not request this, please ignore this message.")

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(message)


# --------- PAGE ROUTES --------- #

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/symptom")
def symptom_page():
    return render_template("symptom.html")

@app.route("/tracker")
def tracker_page():
    return render_template("tracker.html")
# @app.route("/community")
# def community_page():
#     return render_template("community.html")



# --------- COMMUNITY POSTS --------- #

@app.route("/add_post", methods=["POST"])
def add_post():
    content = request.form["content"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO posts (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()

    return redirect("/community")


@app.route("/community")
def community_page():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts ORDER BY id DESC")
    posts = cursor.fetchall()

    conn.close()

    return render_template("community.html", posts=posts)


# --------- SIGNUP --------- #

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"].strip().lower()
    password = request.form["password"]
    confirm = request.form["confirm"]

    # Check email format
    if not is_valid_email(email):
        return "Invalid email format!"

    # Check password match
    if password != confirm:
        return "Passwords do not match!"

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return "Email already registered!"

    # Insert user
    cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()

    return redirect("/")


# --------- LOGIN --------- #

@app.route("/login", methods=["POST"])
def login_user():
    email = request.form["email"].strip().lower()
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        otp_code = generate_otp()
        session["pending_email"] = email
        session["otp_code"] = otp_code

        try:
            send_otp_email(email, otp_code)
        except Exception as e:
            return f"Failed to send OTP: {e}"

        return redirect("/verify")
    else:
        return "Invalid email or password!"


@app.route("/verify", methods=["GET", "POST"])
def verify_email():
    if "pending_email" not in session:
        return redirect("/")

    message = None
    email = session.get("pending_email")

    if request.method == "POST":
        otp = request.form.get("otp")
        if otp == session.get("otp_code"):
            session.pop("otp_code", None)
            session.pop("pending_email", None)
            return redirect("/dashboard")
        message = "Invalid OTP. Please try again."

    return render_template("verify.html", email=email, message=message)


@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    if "pending_email" not in session:
        return redirect("/")

    otp_code = generate_otp()
    session["otp_code"] = otp_code

    try:
        send_otp_email(session["pending_email"], otp_code)
    except Exception as e:
        return f"Failed to resend OTP: {e}"

    return render_template("verify.html", email=session.get("pending_email"), message="OTP resent. Check your email.")


if __name__ == "__main__":
    app.run(debug=True)

# # --------- PREDICTION --------- #

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         input_data = [float(x) for x in request.form.values()]
#         result = predict_pcos(input_data)

#         return render_template("symptom.html", prediction_text=result)

#     except Exception as e:
#         return str(e)    