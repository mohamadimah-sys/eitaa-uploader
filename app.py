import os
from flask import Flask, request, render_template_string
from eitaayarbot import EitaaBot
import tempfile

app = Flask(__name__)

# 🔴🔴🔴 مقادیر خودتان را اینجا قرار دهید 🔴🔴🔴
# 🔴🔴🔴 این دو مقدار را با مقادیر واقعی خود جایگزین کنید 🔴🔴🔴
BOT_TOKEN = "bot524944:d2f21315-a137-40c1-96ad-4ee0ad65a203"
CHAT_ID = "11292179"

HTML_FORM = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ارسال عکس به کانال</title>
    <style>
        body { font-family: Tahoma, sans-serif; text-align: center; margin: 0; padding: 20px; background-color: #f0f2f5; }
        .container { background: white; max-width: 420px; margin: 40px auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h2 { color: #333; }
        input, button { width: 92%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; font-family: inherit; font-size: 15px; }
        button { background-color: #4CAF50; color: white; border: none; cursor: pointer; font-size: 16px; }
        button:disabled { background-color: #999; cursor: not-allowed; }
        .spinner { display: none; margin: 20px auto; width: 45px; height: 45px; border: 5px solid #f3f3f3; border-top: 5px solid #4CAF50; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .wait-msg { display: none; color: #555; font-size: 15px; margin-top: 10px; line-height: 1.8; }
        .warn { background: #fff3cd; color: #856404; padding: 10px; border-radius: 8px; font-size: 13px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📸 ارسال عکس (نسخه نهایی)</h2>
        <p>لطفاً اطلاعات خود را وارد کرده و عکس را انتخاب کنید.</p>
        <form id="uploadForm" method="POST" enctype="multipart/form-data">
            <input type="text" name="first_name" placeholder="نام" required>
            <input type="text" name="last_name" placeholder="نام خانوادگی" required>
            <input type="file" name="photo" accept="image/*" required>
            <button type="submit" id="submitBtn">ارسال به کانال</button>
        </form>
        <div class="spinner" id="spinner"></div>
        <div class="wait-msg" id="waitMsg">⏳ در حال ارسال عکس به کانال...<br>لطفاً صبر کنید و صفحه را نبندید.</div>
    </div>
    <script>
        document.getElementById('uploadForm').addEventListener('submit', function() {
            var btn = document.getElementById('submitBtn');
            btn.disabled = true;
            btn.textContent = 'در حال ارسال...';
            document.getElementById('spinner').style.display = 'block';
            document.getElementById('waitMsg').style.display = 'block';
        });
    </script>
</body>
</html>
"""

SUCCESS_PAGE = """<div style="font-family:Tahoma;text-align:center;margin-top:50px;"><h1 style="color:#4CAF50;">✅ عکس شما با موفقیت ارسال شد</h1><a href="/">ارسال عکس دیگر</a></div>"""
ERROR_PAGE = """<div style="font-family:Tahoma;text-align:center;margin-top:50px;"><h1 style="color:#e74c3c;">❌ خطا در ارسال</h1><p>__ERROR__</p><a href="/">تلاش مجدد</a></div>"""

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        photo = request.files.get("photo")

        if not photo or photo.filename == "":
            return ERROR_PAGE.replace("__ERROR__", "لطفاً یک عکس انتخاب کنید."), 400

        temp_dir = tempfile.gettempdir()
        safe_name = f"upload_{os.getpid()}_{photo.filename}"
        filepath = os.path.join(temp_dir, safe_name)
        photo.save(filepath)

        caption = f"📷 فرستنده: {first_name} {last_name}"

        try:
            bot = EitaaBot(token=BOT_TOKEN)
            bot.send_file(chat_id=CHAT_ID, file_path=filepath, caption=caption)
            bot.close()
            return SUCCESS_PAGE
        except Exception as e:
            return ERROR_PAGE.replace("__ERROR__", f"خطا: {e}"), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template_string(HTML_FORM)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
