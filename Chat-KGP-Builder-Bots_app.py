import json
import os
import google.generativeai as genai

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# =========================================
# إعداد Gemini
# =========================================
GEMINI_API_KEY = "AIzaSyAPiRKJ_2xj5L3sGH8vbgP-HYAFvQ_vL3k"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================================
# ملف التدريب
# =========================================
DATA_FILE = "training.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        training_data = json.load(f)
else:
    training_data = {}

# =========================================
# أوامر البوت
# =========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في Chat KGP Builder Bots + Gemini"
    )

# =========================================
# الرد على الرسائل
# =========================================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if not text:
        return

    # الردود المحلية
    if text in training_data:
        await update.message.reply_text(training_data[text])
        return

    # Gemini
    try:
        response = model.generate_content(text)

        reply = response.text.strip()

        if not reply:
            reply = "🤖 لم أستطع إنشاء رد"

        # تيليجرام له حد أحرف
        if len(reply) > 4000:
            reply = reply[:4000]

        await update.message.reply_text(reply)

    except Exception as e:
        print("Gemini Error:", e)

        await update.message.reply_text(
            "❌ حدث خطأ أثناء الاتصال بـ Gemini"
        )

# =========================================
# تشغيل البوت
# =========================================
def run_bot(token):

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("🤖 البوت يعمل الآن...")

    # النسخة المستقرة
    app.run_polling(
        drop_pending_updates=True
    )

# =========================================
# التدريب المحلي
# =========================================
def train():

    print("\n🧠 وضع التدريب")
    print("اكتب exit للخروج\n")

    while True:

        q = input("السؤال: ")

        if q.lower() == "exit":
            break

        a = input("الرد: ")

        training_data[q] = a

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                training_data,
                f,
                ensure_ascii=False,
                indent=4
            )

        print("✅ تم حفظ التدريب\n")

# =========================================
# الواجهة الرئيسية
# =========================================
def main():

    print("=" * 40)
    print("🤖 Chat KGP Builder Bots + Gemini")
    print("=" * 40)

    token = input("🔑 أدخل Telegram Bot Token: ").strip()

    if not token:
        print("❌ التوكن فارغ")
        return

    while True:

        print("\n1 - تشغيل البوت")
        print("2 - تدريب البوت")
        print("3 - خروج")

        choice = input("\nاختيارك: ").strip()

        if choice == "1":

            try:
                run_bot(token)

            except Exception as e:
                print("❌ خطأ:", e)

        elif choice == "2":
            train()

        elif choice == "3":
            print("👋 Goodbye")
            break

        else:
            print("❌ خيار غير صحيح")

# =========================================
# تشغيل البرنامج
# =========================================
if __name__ == "__main__":
    main()