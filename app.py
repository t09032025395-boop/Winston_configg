from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

# بارگذاری متغیرهای محیطی
load_dotenv()

# ایجاد اپ Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# اتصال به MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["taha1973"]
passwords_col = db["Password"]

# ---------------- صفحه لاگین ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        user = passwords_col.find_one({"password": password})

        if user:
            session["logged_in"] = True
            session["expiry_date"] = user.get("expiry_date")
            return redirect(url_for("main_page"))
        else:
            flash("رمز عبور اشتباه است", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

# ---------------- صفحه اصلی ----------------
@app.route("/main")
def main_page():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    expiry_date = session.get("expiry_date", "نامشخص")
    return render_template("main.html", expiry_date=expiry_date)

# ---------------- خروج ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- اجرای برنامه ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
