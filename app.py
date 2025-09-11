from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# اتصال به دیتابیس
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["taha1973"]
passwords_col = db["Password"]


# --- مسیر ورود ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        user = passwords_col.find_one({"plain_password": password})

        if not user:
            flash("رمز عبور اشتباه است", "error")
            return redirect(url_for("login"))

        # اگر هنوز به دستگاهی قفل نشده → UUID بساز و ذخیره کن
        if not user.get("device_id"):
            new_device_id = str(uuid.uuid4())
            passwords_col.update_one(
                {"_id": user["_id"]},
                {"$set": {"device_id": new_device_id}}
            )
            flash("ورود موفقیت‌آمیز ✅ (دستگاه ثبت شد)", "success")
            return redirect(url_for("main_page"))

        # اگر device_id قبلاً ثبت شده → ورود فقط برای همان دستگاه
        # اینجا چون اپ چیزی ذخیره نمی‌کنه، عملاً همیشه دستگاه اول معتبر میشه
        flash("این رمز قبلاً روی یک دستگاه دیگر استفاده شده ❌", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


# --- مسیر اصلی ---
@app.route("/main")
def main_page():
    return render_template("main.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
