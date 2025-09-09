from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import uuid
import hashlib

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# اتصال به دیتابیس
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["taha1973"]
passwords_col = db["Password"]

# --- توابع کمکی ---
def hash_token(token: str) -> str:
    """توکن را هش می‌کند"""
    return hashlib.sha256(token.encode()).hexdigest()


# --- مسیر ورود ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        user = passwords_col.find_one({"plain_password": password})

        if not user:
            flash("رمز عبور اشتباه است", "error")
            return redirect(url_for("login"))

        # تولید توکن جدید برای ورود موفق
        new_token = str(uuid.uuid4())
        hashed_token = hash_token(new_token)

        # ذخیره توکن هش شده در دیتابیس → دستگاه قبلی غیرفعال می‌شود
        passwords_col.update_one(
            {"_id": user["_id"]},
            {"$set": {"device_token": hashed_token}}
        )

        # ست کردن کوکی با توکن اصلی
        resp = make_response(redirect(url_for("main_page")))
        resp.set_cookie(
            "device_token",
            new_token,
            max_age=60*60*24*365,
            httponly=True,
            samesite='Strict'
        )

        # ست کردن session
        session["logged_in"] = True
        session["expiry_date"] = user.get("expiry_date")

        return resp

    return render_template("login.html")


# --- مسیر اصلی ---
@app.route("/main")
def main_page():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # بررسی device_token کوکی با هش دیتابیس
    cookie_token = request.cookies.get("device_token")
    hashed_cookie = hash_token(cookie_token) if cookie_token else None

    user = passwords_col.find_one({"device_token": hashed_cookie})
    if not user:
        # توکن معتبر نیست → لوگ‌اوت خودکار
        session.clear()
        flash("ورود از دستگاه دیگری انجام شد. شما از سیستم خارج شدید.", "error")
        return redirect(url_for("login"))

    expiry_date = session.get("expiry_date", "نامشخص")
    return render_template("main.html", expiry_date=expiry_date)


# --- مسیر خروج ---
@app.route("/logout")
def logout():
    session.clear()
    resp = make_response(redirect(url_for("login")))
    resp.set_cookie("device_token", "", expires=0)
    return resp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
