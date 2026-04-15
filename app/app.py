from flask import Flask, render_template, request
import sys
import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(BASE_DIR, "src"))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from predict import predict_pcos

app = Flask(__name__)




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
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


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
    email = request.form["email"]
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
    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        return redirect("/dashboard")
    else:
        return "Invalid email or password!"

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