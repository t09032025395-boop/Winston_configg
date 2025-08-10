from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bcrypt import checkpw
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# اتصال به دیتابیس
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["taha1973"]
passwords_col = db["Password"]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        user = passwords_col.find_one({"plain_password": password})  
        # اگر رمز هش شده داری:
        # user = passwords_col.find_one({"password_hash": {"$exists": True}})
        # و بعدش checkpw()

        if user:
            device_token = request.cookies.get("device_token")
            owner_token = user.get("device_token")

            # اولین ورود → ذخیره دستگاه
            if not owner_token:
                new_token = str(uuid.uuid4())
                passwords_col.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"device_token": new_token}}
                )
                resp = make_response(redirect(url_for("main_page")))
                resp.set_cookie("device_token", new_token, max_age=60*60*24*365)  # یک سال
                session["logged_in"] = True
                session["expiry_date"] = user.get("expiry_date")
                return resp

            # ورود با همون دستگاه
            elif device_token == owner_token:
                session["logged_in"] = True
                session["expiry_date"] = user.get("expiry_date")
                return redirect(url_for("main_page"))

            # دستگاه متفاوت → خطا
            else:
                flash("این رمز قبلاً توسط دستگاه دیگری استفاده شده است", "error")
                return redirect(url_for("login"))

        else:
            flash("رمز عبور اشتباه است", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/main")
def main_page():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    expiry_date = session.get("expiry_date", "نامشخص")
    return render_template("main.html", expiry_date=expiry_date)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
