from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bcrypt import checkpw

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

# ---------------- صفحه اصلی → ریدایرکت به لاگین ----------------
@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------------- صفحه لاگین ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    print("📩 Request method:", request.method)   # برای تست در لاگ Render
    print("📦 POST data:", request.form)
    print("🔑 Password received:", request.form.get("password"))

    if request.method == "POST":
        password = request.form.get("password")

        # گرفتن اولین کاربر (چون ظاهراً فقط یک رمز داری)
        user = passwords_col.find_one({})
        if user:
            stored_hash = user.get("password_hash")
            if stored_hash and checkpw(password.encode("utf-8"), stored_hash):
                session["logged_in"] = True
                session["expiry_date"] = user.get("expiry_date")
                print("✅ Login success")
                return redirect(url_for("main_page"))
            else:
                flash("رمز عبور اشتباه است", "error")
                print("❌ Wrong password")
        else:
            flash("کاربری یافت نشد", "error")
            print("❌ No user in DB")

        return redirect(url_for("login"))

    return render_template("login.html")

# ---------------- صفحه اصلی بعد از لاگین ----------------
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
